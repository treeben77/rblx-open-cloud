from .exceptions import rblx_opencloudException, InvalidKey, ServiceUnavailable, InsufficientScope, InvalidCode
from urllib import parse
import requests, datetime, time
from typing import Optional, Union, TYPE_CHECKING
from .user import User
from .group import Group
from .experience import Experience
import requests, base64, jwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_der_public_key
from cryptography.hazmat.backends import default_backend

__all__ = (
    "OAuth2App",
    "AccessToken",
    "PartialAccessToken",
    "AccessTokenInfo"
)

class AccessTokenInfo():
    def __init__(self, data: dict):
        self.active: bool = data["active"]
        self.id: str = data["jti"]
        self.client_id: int = int(data["client_id"])
        self.user_id: int = data["sub"]
        self.scope: list[str] = data["scope"].split(" ")
        self.expires_at: datetime.datetime = datetime.datetime.fromtimestamp(data["exp"])
        self.issued_at: datetime.datetime = datetime.datetime.fromtimestamp(data["iat"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.AccessTokenInfo(id={self.id}, user_id={self.user_id})"

class Resources():
    def __init__(self, experiences, accounts):
        self.experiences: list[Experience] = experiences
        self.accounts: list[Union[User, Group]] = accounts
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Resources(experiences={self.experiences}, accounts={self.accounts})"

class PartialAccessToken():
    def __init__(self, app, access_token) -> None:
        self.app: OAuth2App = app
        self.token: str = access_token
    
    def __repr__(self) -> str:
        return f"rblxopencloud.PartialAccessToken(token={self.token[:15]}...)"

    def fetch_userinfo(self) -> User:
        response = requests.get("https://apis.roblox.com/oauth/v1/userinfo", headers={
            "authorization": f"Bearer {self.token}"
        })
        user = User(response.json().get("id") or response.json().get("sub"), f"Bearer {self.token}")
        user.username: str = response.json().get("preferred_username")
        user.display_name: str = response.json().get("nickname")
        user.created_at: datetime.datetime = datetime.datetime.fromtimestamp(response.json()["created_at"]) if response.json().get("created_at") else None

        if response.ok: return user
        elif response.status_code == 401:
            if response.json()["error"] == "insufficient_scope":
                raise InsufficientScope(response.json()["scope"], f"The access token does not have the required scope:'{response.json()['scope']}'")
            raise InvalidKey("The key has expired, been revoked or is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def fetch_resources(self) -> Resources:
        response = requests.post("https://apis.roblox.com/oauth/v1/token/resources", data={
            "token": self.token,
            "client_id": self.app.id,
            "client_secret": self.app._OAuth2App__secret
        })

        if response.status_code == 401:
            if response.json()["error"] == "insufficient_scope":
                raise InsufficientScope(response.json()["scope"], f"The access token does not have the required scope:'{response.json()['scope']}'")
            raise InvalidKey("The key has expired, been revoked or is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        experiences = []
        accounts = []

        for resource in response.json()["resource_infos"]:
            owner = resource["owner"]
            for experience_id in resource["resources"]["universe"]["ids"]:
                experience = Experience(experience_id, f"Bearer {self.token}")
                if owner["type"] == "User":
                    experience.owner = User(owner["id"], f"Bearer {self.token}")
                elif owner["type"] == "Group":
                    experience.owner = Group(owner["id"], f"Bearer {self.token}")
                experiences.append(experience)

            if owner["type"] == "User":
                for creator_id in resource["resources"]["creator"]["ids"]:
                    if creator_id == "U":
                        accounts.append(User(owner["id"], f"Bearer {self.token}"))
                    elif creator_id.startswith("U"):
                        accounts.append(User(creator_id[1:], f"Bearer {self.token}"))
                    elif creator_id.startswith("G"):
                        accounts.append(Group(creator_id[1:], f"Bearer {self.token}"))

        return Resources(experiences=experiences, accounts=accounts)

    def fetch_token_info(self) -> AccessTokenInfo:
        response = requests.post("https://apis.roblox.com/oauth/v1/token/introspect", data={
            "token": self.token,
            "client_id": self.app.id,
            "client_secret": self.app._OAuth2App__secret
        })
        
        if response.ok: return AccessTokenInfo(response.json())
        elif response.status_code == 401:
            if response.json()["error"] == "insufficient_scope":
                raise InsufficientScope(response.json()["scope"], f"The access token does not have the required scope:'{response.json()['scope']}'")
            raise InvalidKey("The key has expired, been revoked or is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def revoke(self):
        self.app.revoke_token(self.token)

class AccessToken(PartialAccessToken):
    def __init__(self, app, payload, id_token) -> None:
        super().__init__(app, payload["access_token"])
        self.refresh_token: str = payload["refresh_token"]
        self.scope: list[str] = payload["scope"].split(" ")
        self.expires_at: datetime = datetime.datetime.now() + datetime.timedelta(payload["expires_in"])
        if id_token:
            self.user: Optional[User] = User(id_token.get("id") or id_token.get("sub"), f"Bearer {self.token}")
            self.user.username: str = id_token.get("preferred_username")
            self.user.display_name: str = id_token.get("nickname")
            self.user.created_at: datetime.datetime = datetime.datetime.fromtimestamp(id_token["created_at"]) if id_token.get("created_at") else None
        else: self.user: Optional[User] = None

    def __repr__(self) -> str:
        return f"rblxopencloud.AccessToken(token={self.token[:15]}..., user={self.user})"
    
    def revoke_refresh_token(self):
        self.app.revoke_token(self.refresh_token)

class OAuth2App():
    def __init__(self, id: int, secret: str, redirect_uri: str, openid_certs_cache_seconds: int = 3600):
        self.id: int = id
        self.redirect_uri: str = redirect_uri
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
                self.__openid_certs_cache_updated = time.time()

            for cert in self.__openid_certs_cache:
                try:
                    id_token = jwt.decode(response.json()["id_token"], cert,  algorithms=['ES256'], audience=str(self.id))
                    break
                except(jwt.exceptions.PyJWTError): pass

        if response.ok: return AccessToken(self, response.json(), id_token)
        elif response.status_code == 400: raise InvalidKey("The client id, client secret, or redirect uri is invalid.")
        elif response.status_code == 401: raise InvalidCode("The code is invalid, or has been used.")
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
        if response.ok: return
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