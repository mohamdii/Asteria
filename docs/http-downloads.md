# Shared external download client

All three acquisition scripts use `asteria/acquisition/http_client.py`. The coverage probe also re-exports `fetch` for compatibility. GET downloads allow three attempts, retrying timeouts, connection failures, DNS errors, and HTTP 408, 429, 500, 502, 503 and 504. Other HTTP errors stop immediately. Without a usable Retry-After header, waits are one then two seconds. Retry-After accepts seconds or an HTTP date; a delay over 60 seconds stops with a retry-later error rather than retrying too early.

Python urllib has a 55-second timeout for blocking network operations, not a whole-download deadline. On Python certificate verification failure, Windows curl is used with certificate verification still enabled. curl has a 55-second transfer timeout and a 60-second subprocess guard. The fallback shares the retry policy, including HTTP status and Retry-After handling. Its certificate failures are not retried. A fallback can add a transport operation within an attempt; there is no whole-job deadline.

Retries log attempt, reason and delay without response content or request URLs. Raw response persistence, hashes, content/schema checks and parsing remain the acquisition scripts' responsibility. Successful HTTP responses with invalid content are not automatically retried. Existing hash-verified caching remains in the expanded-history script.

Tests simulate successful responses, timeouts, rate limits, server failures, permanent failures and certificate fallback without external requests or actual sleeps. Run `python -m unittest discover -s tests`. This component does not yet provide global provider rate limiting, connection pooling or a complete production ingestion service.
