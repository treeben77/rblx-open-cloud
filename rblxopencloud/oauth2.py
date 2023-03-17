from .exceptions import rblx_opencloudException, InvalidKey, ServiceUnavailable, InsufficientScope
from urllib import parse
import requests, datetime, time
from typing import Optional, Union, TYPE_CHECKING
from .user import User
from .experience import Experience
import requests, base64, jwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_der_public_key
from cryptography.hazmat.backends import default_backend

__all__ = (
    "OAuth2App",
    "AccessToken",
    "PartialAccessToken"
)

class PartialAccessToken():
    def __init__(self, client, access_token) -> None:
        self.client: OAuth2App = client
        self.token: str = access_token
    
    def __repr__(self) -> str:
        return f"rblxopencloud.PartialAccessToken(token={self.token})"

    def fetch_userinfo(self) -> User:
        response = requests.get("https://apis.roblox.com/oauth/v1/userinfo", headers={
            "authorization": f"Bearer {self.token}"
        })

        if response.ok: return User(response.json())
        elif response.status_code == 401:
            if response.json()["error"] == "insufficient_scope":
                raise InsufficientScope(response.json()["scope"], f"The access token does not have the required scope:'{response.json()['scope']}'")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def fetch_experiences(self) -> list[Experience]:
        response = requests.post("https://apis.roblox.com/oauth/v1/token/resources", data={
            "token": self.token,
            "client_id": self.client.id,
            "client_secret": self.client._OAuth2App__secret
        })

        if response.status_code == 401:
            if response.json()["error"] == "insufficient_scope":
                raise InsufficientScope(response.json()["scope"], f"The access token does not have the required scope:'{response.json()['scope']}'")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
        
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
    
    def revoke(self):
        self.client.revoke_token(self.token)

class AccessToken(PartialAccessToken):
    def __init__(self, client, payload, id_token) -> None:
        super().__init__(client, payload["access_token"])
        self.refresh_token: str = payload["refresh_token"]
        self.scope: list[str] = payload["scope"].split(" ")
        self.expires_at: datetime = datetime.datetime.now() + datetime.timedelta(payload["expires_in"])
        self.user: Optional[User] = User(id_token) if id_token else None
        self.id_token: Optional[dict] = id_token

    def __repr__(self) -> str:
        return f"rblxopencloud.AccessToken(token={self.token})"
    
    def revoke_refresh_token(self):
        self.client.revoke_token(self.refresh_token)

class OAuth2App():
    def __init__(self, id: int, secret: str, redirect_uri: str, openid_certs_cache_seconds: int = 3600):
        self.id: int = id
        self.redirect_uri: int = redirect_uri
        self.__secret: str = secret

        self.openid_certs_cache_seconds: int = openid_certs_cache_seconds
        self.__openid_certs_cache = None
        self.__openid_certs_cache_updated = None
    
    def __repr__(self) -> str:
        return f"rblxopencloud.OAuth2App(id={self.id}, redirect_uri={self.redirect_uri})"

    def generate_uri(self, scope: Union[str, list[str]], state: Optional[str]=None, generate_code=True) -> str:
        params = {
            "client_id": self.id,
            "scope": " ".join(scope) if type(scope) == list else scope,
            "state": state,
            "redirect_uri": self.redirect_uri,
            "response_type": "code" if generate_code else "none"
        }
        return f"https://apis.roblox.com/oauth/v1/authorize?{parse.urlencode({key: value for key, value in params.items() if value is not None})}"

    def from_access_token_string(self, access_token: str) -> PartialAccessToken:
        return PartialAccessToken(self, access_token)

    def exchange_code(self, code: str) -> AccessToken:
        response = requests.post("https://apis.roblox.com/oauth/v1/token", data={
            "client_id": self.id,
            "client_secret": self.__secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code": code
        })
        id_token = None
        if response.json().get("id_token"):
            if not self.__openid_certs_cache or time.time() - self.__openid_certs_cache_updated > self.openid_certs_cache_seconds:
                certs = requests.get("https://apis.roblox.com/oauth/v1/certs")
                if not certs.ok: raise ServiceUnavailable("Failed to retrieve OpenID certs.")
                self.__openid_certs_cache = convert_certs_to_keys(certs.json()["keys"])

            for cert in self.__openid_certs_cache:
                try:
                    id_token = jwt.decode(response.json()["id_token"], cert,  algorithms=['ES256'], audience=str(self.id))
                    break
                except(Exception): pass

        if response.ok: return AccessToken(self, response.json(), id_token)
        elif response.status_code == 400: raise InvalidKey("The code, client id, client secret, or redirect uri is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def refresh_token(self, refresh_token: str) -> AccessToken:
        response = requests.post("https://apis.roblox.com/oauth/v1/token", data={
            "client_id": self.id,
            "client_secret": self.__secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        })
        if response.ok: return AccessToken(self, response.json(), None)
        elif response.status_code == 400: raise InvalidKey("The code, client id, client secret, or redirect uri is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def revoke_token(self, token: str):
        response = requests.post("https://apis.roblox.com/oauth/v1/token/revoke", data={
            "token": token,
            "client_id": self.id,
            "client_secret": self.__secret
        })
        if response.ok: return AccessToken(self, response.json())
        elif response.status_code == 400: raise InvalidKey("The code, client id, client secret, or redirect uri is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

def convert_certs_to_keys(certs):
    keys = []
    for cert in certs:
        keys.append(load_der_public_key(ec.EllipticCurvePublicNumbers(
            int.from_bytes(base64.urlsafe_b64decode(cert['x'] + '=='), 'big'),
            int.from_bytes(base64.urlsafe_b64decode(cert['y'] + '=='), 'big'),
            ec.SECP256R1()
        ).public_key(default_backend()).public_bytes(
            Encoding.DER,
            PublicFormat.SubjectPublicKeyInfo
        ), default_backend()))
    return keys