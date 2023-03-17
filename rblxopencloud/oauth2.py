from urllib import parse
import requests, datetime, jwt
from typing import Optional, Union, TYPE_CHECKING
from .user import User
from .experience import Experience

__all__ = (
    "OAuth2App",
    "AccessToken"
)

class AccessToken():
    def __init__(self, client, payload) -> None:
        self.client: OAuth2App = client
        self.token: str = payload["access_token"]
        self.refresh_token: str = payload["refresh_token"]
        self.scope: list[str] = payload["scope"].split(" ")
        self.expires_at: datetime = datetime.datetime.now() + datetime.timedelta(payload["expires_in"])

        # TODO: work out how to get this to work lmfao
        # if payload.get("openid"):
        #     token = jwt.decode(payload["openid"])

    def fetch_userinfo(self) -> User:
        response = requests.get("https://apis.roblox.com/oauth/v1/userinfo", headers={
            "authorization": f"Bearer {self.token}"
        })
        if response.ok: return User(response.json())
    
    def fetch_experiences(self) -> list[Experience]:
        response = requests.post("https://apis.roblox.com/oauth/v1/token/resources", data={
            "token": self.token,
            "client_id": self.client.id,
            "client_secret": self.client._OAuth2App__secret
        })
        experiences = []
        for resource in response.json()["resource_infos"]:
            owner = resource["owner"]
            for experience_id in resource["resources"]["universe"]["ids"]:
                experience = Experience(experience_id, self.token)
                experience._Experience__key_type = "BEARER"
                if owner["type"] == "User":
                    experience.owner = User({"id": owner["id"]})
                experiences.append(experience)
        return experiences

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
    
    def refresh_token(self, refresh_token: str) -> AccessToken:
        response = requests.post("https://apis.roblox.com/oauth/v1/token", data={
            "client_id": self.id,
            "client_secret": self.__secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        })
        return AccessToken(self, response.json())