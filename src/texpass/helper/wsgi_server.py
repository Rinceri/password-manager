import wsgiref.simple_server
import wsgiref.util

from google_auth_oauthlib.flow import Flow

# taken from https://github.com/googleapis/google-auth-library-python-oauthlib/blob/main/google_auth_oauthlib/flow.py

class LocalServer:
    def __init__(self, flow: Flow):
        self.flow = flow
        self.local_server = None
        self.wsgi_app = _RedirectWSGIApp()
        

    def get_auth_url(self) -> str:
        """
        Get auth URL. Make sure to run server, as a server has been made
        """
        host = "localhost"
        port = 8080

        self.local_server: wsgiref.simple_server.WSGIServer = wsgiref.simple_server.make_server(
            host,
            port,
            self.wsgi_app
        )

        self.flow.redirect_uri = f"http://{host}:{port}"
        auth_url, _ = self.flow.authorization_url()

        return auth_url
    
    def run_local_server(self):
        try:
            self.local_server.handle_request()

            # Note: using https here because oauthlib is very picky that
            # OAuth 2.0 should only occur over https.
            auth_response = self.wsgi_app.last_request_uri.replace("http", "https")
            self.flow.fetch_token(authorization_response = auth_response)

        finally:
            self.local_server.server_close()

        return self.flow.credentials



class _RedirectWSGIApp(object):
    """WSGI app to handle the authorization redirect.

    Stores the request URI and displays the given success message.
    """

    def __init__(self):
        self.last_request_uri = None
        self._success_message = "The authentication flow has completed. You may close this window."

    def __call__(self, environ, start_response):
        """WSGI Callable.

        Args:
            environ (Mapping[str, Any]): The WSGI environment.
            start_response (Callable[str, list]): The WSGI start_response
                callable.

        Returns:
            Iterable[bytes]: The response body.
        """
        start_response("200 OK", [("Content-type", "text/plain; charset=utf-8")])
        self.last_request_uri = wsgiref.util.request_uri(environ)
        return [self._success_message.encode("utf-8")]
