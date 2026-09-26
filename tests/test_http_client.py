import ssl
import sys
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import http_client as client


class HttpClientTests(unittest.TestCase):
    def response(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'evidence'
        return response

    def test_success_and_timeout_forwarded(self):
        with patch.object(client, 'urlopen', return_value=self.response()) as request:
            self.assertEqual(client.fetch(('fixture', 'https://example.test')), ('fixture', 'https://example.test', b'evidence'))
            request.assert_called_once_with('https://example.test', timeout=55)

    def test_timeout_retries_are_bounded(self):
        with patch.object(client, 'urlopen', side_effect=URLError(TimeoutError() )) as request, patch.object(client.time, 'sleep') as sleep:
            with self.assertRaisesRegex(client.DownloadError, '3 attempt'):
                client.get_bytes('https://example.test')
            self.assertEqual(request.call_count, 3)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [1, 2])

    def test_rate_limit_respects_retry_after(self):
        error = HTTPError('fixture', 429, '', {'Retry-After': '7'}, None)
        with patch.object(client, 'urlopen', side_effect=[error, self.response()]), patch.object(client.time, 'sleep') as sleep:
            self.assertEqual(client.get_bytes('https://example.test'), b'evidence')
            sleep.assert_called_once_with(7)

    def test_long_retry_after_stops_without_early_retry(self):
        error = HTTPError('fixture', 503, '', {'Retry-After': '120'}, None)
        with patch.object(client, 'urlopen', side_effect=error) as request, patch.object(client.time, 'sleep') as sleep:
            with self.assertRaisesRegex(client.DownloadError, 'wait budget'):
                client.get_bytes('https://example.test')
            self.assertEqual(request.call_count, 1)
            sleep.assert_not_called()

    def test_permanent_http_error_not_retried(self):
        with patch.object(client, 'urlopen', side_effect=HTTPError('fixture', 404, '', {}, None)) as request:
            with self.assertRaisesRegex(client.DownloadError, 'HTTP 404'):
                client.get_bytes('https://example.test')
            self.assertEqual(request.call_count, 1)

    def test_server_error_recovers(self):
        with patch.object(client, 'urlopen', side_effect=[HTTPError('fixture', 502, '', {}, None), self.response()]), patch.object(client.time, 'sleep'):
            self.assertEqual(client.get_bytes('https://example.test'), b'evidence')

    def test_certificate_fallback_uses_same_retry_policy(self):
        with patch.object(client, 'urlopen', side_effect=URLError(ssl.SSLCertVerificationError())) as request, patch.object(client, '_curl_get', side_effect=[HTTPError('fixture', 503, '', {}, None), b'ok']) as curl, patch.object(client.time, 'sleep'):
            self.assertEqual(client.get_bytes('https://example.test'), b'ok')
            self.assertEqual(request.call_count, 1)
            self.assertEqual(curl.call_count, 2)

    def test_curl_response_and_secure_arguments(self):
        def run(args, **kwargs):
            Path(args[args.index('--output')+1]).write_bytes(b'body')
            Path(args[args.index('--dump-header')+1]).write_bytes(b'HTTP/1.1 200 Connection established\r\n\r\nHTTP/2 429\r\nRetry-After: 9\r\n\r\n')
            self.assertNotIn('--insecure', args)
            self.assertEqual(kwargs['timeout'], 60)
            return MagicMock(returncode=0, stdout=b'429')
        with patch.object(client.subprocess, 'run', side_effect=run):
            with self.assertRaises(HTTPError) as raised:
                client._curl_get('https://example.test', 55)
            self.assertEqual(raised.exception.headers['retry-after'], '9')
            raised.exception.close()

    def test_retry_after_date_and_invalid_header(self):
        future = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=30))
        self.assertTrue(28 <= client.retry_delay(future, 1) <= 30)
        self.assertEqual(client.retry_delay('invalid', 3), 4)

    def test_curl_certificate_failure_not_retried(self):
        with patch.object(client, 'urlopen', side_effect=URLError(ssl.SSLCertVerificationError())), patch.object(client.subprocess, 'run', return_value=MagicMock(returncode=60)) as run:
            with self.assertRaises(client.DownloadError):
                client.get_bytes('https://example.test')
            self.assertEqual(run.call_count, 1)
