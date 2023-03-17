from urllib import parse
import requests, datetime, jwt
from typing import Optional, Union, TYPE_CHECKING
from .user import User

__all__ = (
    "OAuth2App",
    "AccessToken"
)

class AccessToken():
    def __init__(self, client, payload) -> None:
        self.client = client
        self.token = payload["access_token"]
        self.refresh_token = payload["refresh_token"]
        self.scope = payload["scope"].split(" ")
        self.expires_at = datetime.datetime.now() + datetime.timedelta(payload["expires_in"])

        # TODO: work out how to get this bomb to work lmfao
        # if payload.get("openid"):
        #     token = jwt.decode(payload["openid"])

    def fetch_userinfo(self) -> User:
        response = requests.get("https://apis.roblox.com/oauth/v1/userinfo", headers={
            "authorization": f"Bearer {self.token}"
        })
        if response.ok: return User(response.json())

class OAuth2App():
    def __init__(self, id: int, secret: str, redirect_uri):
        self.id: int = id
        self.redirect_uri: int = redirect_uri
        self.__secret: str = secret

    def generate_uri(self, scope: Union[str, list[str]], state: Optional[str]=None) -> str:
        params = {
            "client_id": self.id,
            "scope": " ".join(scope) if type(scope) == list else scope,
            "state": state,
            "redirect_uri": self.redirect_uri,
            "response_type": "code"
        }
        return f"https://apis.roblox.com/oauth/v1/authorize?{parse.urlencode({key: value for key, value in params.items() if value is not None})}"

    def exchange_code(self, code: str) -> AccessToken:
        response = requests.post("https://apis.roblox.com/oauth/v1/token", data={
            "client_id": self.id,
            "client_secret": self.__secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code": code
        })
        return AccessToken(self, response.json())