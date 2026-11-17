"""Serve this folder for local development, without the caching trap.

    python serve.py           # http://127.0.0.1:8618/
    python serve.py 9000      # a different port

Use this rather than `python -m http.server`. http.server sends no
Cache-Control and no ETag, only Last-Modified, so a browser falls back to
*heuristic* freshness -- it invents an expiry of roughly a tenth of the file's
age and serves the file from cache until then without asking the server
anything. Editing a .py file and reloading shows the old one, and restarting
the server changes nothing, because the browser never made a request.

That is not a hypothetical: it swallowed a newly added champion and a newly
added trait, on two separate occasions, in a way that looked exactly like the
edit had not been saved.

worker.js fetches its Python sources with cache: "no-cache" for the same
reason, but that cannot rescue a browser that has worker.js *itself* cached --
the fix is inside the file that went stale. Only the server can break that
cycle, which is what this does.

no-cache means revalidate, not don't-store: everything is still cached and a
file that hasn't moved comes back as a 304 with no body, so this costs a
conditional request per file, not a re-download.
"""

import functools
import http.server
import os
import sys

PORT = 8618


class RevalidatingHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        # One line per request, without the date noise: seeing 304s go by is
        # how you know revalidation is happening at all.
        sys.stderr.write("%s\n" % (fmt % args))

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except ConnectionError:
            # The browser abandoning a connection is routine here (it opens
            # more than it ends up needing) and is not worth a traceback.
            self.close_connection = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    root = os.path.dirname(os.path.abspath(__file__))
    handler = functools.partial(RevalidatingHandler, directory=root)
    # Threading is not optional: the page opens several connections at once
    # and the Web Worker fetches every Python source in parallel on top of
    # them. A single-threaded server serialises that into a stall.
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"serving http://127.0.0.1:{port}/  (ctrl-c to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    main()
