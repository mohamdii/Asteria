"""Bounded GET retries shared by external evidence acquisition scripts."""
import logging
import socket
import ssl
import subprocess
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

LOG = logging.getLogger(__name__)
RETRY_STATUS = {408, 429, 500, 502, 503, 504}


class DownloadError(RuntimeError):
    """A download failed permanently or exhausted its retry budget."""


def retry_delay(value, attempt):
    """Honor seconds or HTTP-date Retry-After; otherwise exponential backoff."""
    if value:
        try:
            if value.strip().isdigit():
                return float(value)
            stamp = parsedate_to_datetime(value)
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            return max(0, (stamp - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            pass
    return 2 ** (attempt - 1)


def _curl_get(url, timeout):
    # Keep certificate verification enabled; Windows curl uses native trust.
    with TemporaryDirectory(prefix='asteria-http-') as folder:
        body, headers = Path(folder)/'body', Path(folder)/'headers'
        result = subprocess.run(
            ['curl.exe', '--silent', '--show-error', '--location',
             '--max-time', str(timeout), '--connect-timeout', str(timeout),
             '--dump-header', str(headers), '--output', str(body),
             '--write-out', '%{http_code}', url],
            capture_output=True, timeout=timeout + 5)
        if result.returncode:
            # Timeouts and interrupted connections are transient; TLS errors aren't.
            if result.returncode in {5, 6, 7, 18, 28, 52, 55, 56}:
                raise URLError(ConnectionError('curl transport error ' + str(result.returncode)))
            raise DownloadError('curl failed with exit code ' + str(result.returncode))
        status = int(result.stdout.decode().strip())
        # Redirect/proxy responses can precede the final header block.
        final_headers = headers.read_text(encoding='iso-8859-1').strip().split('\n\n')[-1]
        values = {}
        for line in final_headers.splitlines()[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                values[key.lower()] = value.strip()
        if not 200 <= status < 300:
            raise HTTPError(url, status, 'curl HTTP response', values, None)
        return body.read_bytes()


def get_bytes(url, *, timeout=55, max_attempts=3, max_retry_delay=60):
    """GET bytes with limited retries. urllib timeout is per blocking operation.

    A Retry-After exceeding our wait budget stops the request instead of retrying
    earlier than the server permits. curl has a total transfer timeout.
    """
    if timeout <= 0 or max_attempts < 1 or max_retry_delay < 0:
        raise ValueError('Invalid HTTP retry/timeout configuration')
    use_curl = False
    for attempt in range(1, max_attempts + 1):
        retry_after = None
        try:
            if not use_curl:
                try:
                    with urlopen(url, timeout=timeout) as response:
                        return response.read()
                except URLError as error:
                    if not isinstance(error.reason, ssl.SSLCertVerificationError):
                        raise
                    use_curl = True
            return _curl_get(url, timeout)
        except HTTPError as error:
            transient = error.code in RETRY_STATUS
            retry_after = error.headers.get('Retry-After') or error.headers.get('retry-after')
            reason = 'HTTP ' + str(error.code)
            error.close()
        except (URLError, TimeoutError, ConnectionError, subprocess.TimeoutExpired) as error:
            underlying = error.reason if isinstance(error, URLError) else error
            transient = isinstance(underlying, (TimeoutError, ConnectionError, socket.gaierror, subprocess.TimeoutExpired))
            reason = type(underlying).__name__
        except (OSError, DownloadError) as error:
            raise DownloadError('Download failed: ' + type(error).__name__) from error
        if not transient or attempt == max_attempts:
            raise DownloadError(f'Download failed after {attempt} attempt(s): {reason}')
        delay = retry_delay(retry_after, attempt)
        if delay > max_retry_delay:
            raise DownloadError('Retry-After exceeds wait budget; retry later')
        LOG.warning('Download attempt %s failed (%s); retrying in %ss', attempt, reason, delay)
        time.sleep(delay)


def fetch(item):
    """Compatibility interface for acquisition worker pools."""
    name, url = item
    return name, url, get_bytes(url)
