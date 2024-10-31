from flask import Response
from environment import conf

class Response(Response):
    def set_auth_cookies(self, jwt, refresh_token):
        self.set_cookie("api-key", jwt, httponly=True, secure=True, samesite="Lax", max_age=conf.api.refresh_token_validity, path="/api/")
        self.set_cookie("refresh-token", refresh_token, httponly=True, secure=True, samesite="Lax", max_age=conf.api.refresh_token_validity, path="/api/v1/auth/refresh")