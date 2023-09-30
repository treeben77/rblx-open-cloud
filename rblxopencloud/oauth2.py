from .exceptions import rblx_opencloudException, InvalidKey, ServiceUnavailable, InsufficientScope, InvalidCode
from urllib import parse
import datetime, time
from typing import Optional, Union, TYPE_CHECKING
from .user import User
from .group import Group
from .experience import Experience
import base64, jwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_der_public_key
from cryptography.hazmat.backends import default_backend
import hashlib, string, secrets
from . import user_agent, request_session

__all__ = (
    "OAuth2App",
    "AccessToken",
    "PartialAccessToken",
    "Resources",
    "AccessTokenInfo"
)

class AccessTokenInfo():
    """
    Data class that contains information about the access token.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`AccessToken.fetch_token_info()`][rblxopencloud.AccessToken.fetch_token_info].
    
    Attributes:
        active (bool): Wether the token is still active.
        id (str): A unqiue string for every authorization and user.
        client_id (int): The app's client ID.
        user_id (int): The authorized user's ID.
        scope (list[str]): A list of authorized scopes.
        expires_at (datetime.datetime): The time the access token will expire at.
        issued_at (datetime.datetime): The time the access token was issued.
    """

    def __init__(self, data: dict):
        self.active: bool = data["active"]
        self.id: str = data["jti"]
        self.client_id: int = int(data["client_id"])
        self.user_id: int = data["sub"]
        self.scope: list[str] = data["scope"].split(" ")
        self.expires_at: datetime.datetime = datetime.datetime.fromtimestamp(data["exp"])
        self.issued_at: datetime.datetime = datetime.datetime.fromtimestamp(data["iat"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.AccessTokenInfo(id=\"{self.id}\", user_id={self.user_id})"

class Resources():
    """
    Data class that contains all the authorized users, groups, and experiences.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`AccessToken.fetch_resources()`][rblxopencloud.AccessToken.fetch_resources].
    
    Attributes:
        experiences (list[Experience]): A list of authorized experiences. These experiences will have the `owner` attribute filled.
        accounts (list[Union[User, Group]]): A list of authorized users, groups (aka 'accounts', or 'creators').   
    """

    def __init__(self, experiences, accounts):
        self.experiences: list[Experience] = experiences
        self.accounts: list[Union[User, Group]] = accounts
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Resources(experiences={self.experiences}, accounts={self.accounts})"

class PartialAccessToken():
    """
    Represents a partial access via OAuth2 consent. It allows access to all resources authorized by the user, but not other information like the refresh token.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`OAuth2App.from_access_token_string()`][rblxopencloud.OAuth2App.from_access_token_string].
    
    Attributes:
        app (OAuth2App): The app this access token belongs to.
        token (str): The string access token. It can be used with [`OAuth2App.from_access_token_string`][rblxopencloud.OAuth2App.from_access_token_string]
    """

    def __init__(self, app, access_token) -> None:
        self.app: OAuth2App = app
        self.token: str = access_token
    
    def __repr__(self) -> str:
        return f"rblxopencloud.PartialAccessToken(token=\"{self.token[:15]}...\")"

    def fetch_userinfo(self) -> User:
        """
        Returns a [`rblxopencloud.User`][rblxopencloud.User] representing the authorzed user.

        Returns:
            The user object representing the authorized user, it will include `profile` info in the `profile` scope was included.
        
        Raises:
            InsufficientScope: The `openid` scope was not granted.
            InvalidKey: The access token has expired or is invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response.
        """

        response = request_session.get("https://apis.roblox.com/oauth/v1/userinfo", headers={
            "authorization": f"Bearer {self.token}", "user-agent": user_agent
        })
        user = User(response.json().get("id") or response.json().get("sub"), f"Bearer {self.token}")
        user.username: str = response.json().get("preferred_username")
        user.display_name: str = response.json().get("nickname")
        user.headshot_uri: str = response.json().get("picture")
        user.created_at: datetime.datetime = datetime.datetime.fromtimestamp(response.json()["created_at"]) if response.json().get("created_at") else None

        if response.ok: return user
        elif response.status_code == 401:
            if response.json()["error"] == "insufficient_scope":
                raise InsufficientScope(response.json()["scope"], f"The access token does not have the required scope:'{response.json()['scope']}'")
            raise InvalidKey("The key has expired, been revoked or is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def fetch_resources(self) -> Resources:
        """
        Returns a [`rblxopencloud.Resources`][rblxopencloud.Resources] containing all authorized accounts and expirences.

        Returns:
            Contains all resources authorized by the user.
        
        Raises:
            InsufficientScope: The `openid` scope was not granted.
            InvalidKey: The access token has expired or is invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response.
        """

        response = request_session.post("https://apis.roblox.com/oauth/v1/token/resources", data={
            "token": self.token,
            "client_id": self.app.id,
            "client_secret": self.app._OAuth2App__secret
        }, headers={"user-agent": user_agent})

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
            if resource["resources"].get("universe"):
                for experience_id in resource["resources"]["universe"]["ids"]:
                    experience = Experience(experience_id, f"Bearer {self.token}")
                    if owner["type"] == "User":
                        experience.owner = User(owner["id"], f"Bearer {self.token}")
                    elif owner["type"] == "Group":
                        experience.owner = Group(owner["id"], f"Bearer {self.token}")
                    experiences.append(experience)

            if resource["resources"].get("creator"):
                for creator_id in resource["resources"]["creator"]["ids"]:
                    if creator_id == "U":
                        accounts.append(User(owner["id"], f"Bearer {self.token}"))
                    elif creator_id.startswith("U"):
                        accounts.append(User(creator_id[1:], f"Bearer {self.token}"))
                    elif creator_id.startswith("G"):
                        accounts.append(Group(creator_id[1:], f"Bearer {self.token}"))

        return Resources(experiences=experiences, accounts=accounts)

    def fetch_token_info(self) -> AccessTokenInfo:
        """
        Fetches metadata about the token, such as when it was issued, the user's ID and the token's unique ID.

        Returns:
            Contains the information about access token.
        
        Raises:
            InsufficientScope: The `openid` scope was not granted.
            InvalidKey: The access token has expired or is invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response.
        """

        response = request_session.post("https://apis.roblox.com/oauth/v1/token/introspect", data={
            "token": self.token,
            "client_id": self.app.id,
            "client_secret": self.app._OAuth2App__secret
        }, headers={"user-agent": user_agent})
        
        if response.ok: return AccessTokenInfo(response.json())
        elif response.status_code == 401:
            if response.json()["error"] == "insufficient_scope":
                raise InsufficientScope(response.json()["scope"], f"The access token does not have the required scope:'{response.json()['scope']}'")
            raise InvalidKey("The key has expired, been revoked or is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def revoke(self):
        """
        Shortcut for [`OAuth2App.revoke_token()`][rblxopencloud.OAuth2App.revoke_token] to revoke the access token.
        
        Raises:
            InvalidKey: The client ID or client secret is invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response.
        
        !!! warning
            Revoking an access token or refresh token will also invalidate it's pair, so you should only revoke a token once you're completely done with it.
        """
        self.app.revoke_token(self.token)

class AccessToken(PartialAccessToken):
    """
    Represents access via OAuth2 consent. It allows access to all resources authorized by the user.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`OAuth2App.exchange_code()`][rblxopencloud.OAuth2App.exchange_code], and [`OAuth2App.refresh_token()`][rblxopencloud.OAuth2App.refresh_token].

    Attributes:
        app (OAuth2App): The app this access token belongs to.
        token (str): The string access token. It can be used with [`OAuth2App.from_access_token_string`][rblxopencloud.OAuth2App.from_access_token_string]
        refresh_token (str): The access token's refresh token. This can be used with [`OAuth2App.refresh_token`][rblxopencloud.OAuth2App.refresh_token] to fetch a new refresh token after this access token expires.
        scope (list[str]): A list of scopes that were granted.
        expires_at (datetime.datetime): The estimated timestamp the access token will expire at.
        user (Optional[User]): If `openid` scope is granted, then this will be the user object. there's rare circumstances where this will be `None` even with the `openid` scope.
    """

    def __init__(self, app, payload, id_token) -> None:
        super().__init__(app, payload["access_token"])
        self.refresh_token: str = payload["refresh_token"]
        self.scope: list[str] = payload["scope"].split(" ")
        self.expires_at: datetime = datetime.datetime.now() + datetime.timedelta(payload["expires_in"])
        if id_token:
            self.user: Optional[User] = User(id_token.get("id") or id_token.get("sub"), f"Bearer {self.token}")
            self.user.username: str = id_token.get("preferred_username")
            self.user.display_name: str = id_token.get("nickname")
            self.user.headshot_uri: Optional[str] = id_token.get("picture")
            self.user.created_at: datetime.datetime = datetime.datetime.fromtimestamp(id_token["created_at"]) if id_token.get("created_at") else None
        else: self.user: Optional[User] = None

    def __repr__(self) -> str:
        return f"rblxopencloud.AccessToken(token=\"{self.token[:15]}...\", user={self.user})"
    
    def revoke_refresh_token(self):
        """
        Shortcut for [`OAuth2App.revoke_token()`][rblxopencloud.OAuth2App.revoke_token] to revoke the refresh token.
        
        Raises:
            InvalidKey: The client ID or client secret is invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response.
        
        !!! warning
            Revoking an access token or refresh token will also invalidate it's pair, so you should only revoke a token once you're completely done with it.
        """
        self.app.revoke_token(self.refresh_token)

class OAuth2App():
    """
    Represents an OAuth2 app. It is used to exchange codes, refresh tokens, and access the API for authenticated users.

    Args:
        id: The app's client ID.
        secret: The app's client secret.
        redirect_uri: The redirect URI that is being used for authorization. If you need to use multiple, you must make seperate objects.
        openid_certs_cache_seconds: The number of seconds to cache Roblox's OpenID certs. You can ignore this if you don't know what it does.

    Attributes:
        id (int): The app's client ID.
        redirect_uri (str): The app's redirect URI.
        openid_certs_cache_seconds (int): The number of seconds to cache the OpenID certs.
    """

    def __init__(self, id: int, secret: str, redirect_uri: str, openid_certs_cache_seconds: int = 3600):
        self.id: int = id
        self.redirect_uri: str = redirect_uri
        self.__secret: str = secret

        self.openid_certs_cache_seconds: int = openid_certs_cache_seconds
        self.__openid_certs_cache = None
        self.__openid_certs_cache_updated = None
    
    def __repr__(self) -> str:
        return f"rblxopencloud.OAuth2App(id={self.id}, redirect_uri=\"{self.redirect_uri}\")"

    def generate_code_verifier(self, length: Optional[int]=128) -> str:
        """
        Generates a code verifier which can be provided [`OAuth2App.generate_uri()`][rblxopencloud.OAuth2App.generate_uri] and [`OAuth2App.exchange_code()`][rblxopencloud.OAuth2App.exchange_code] to add extra security to the OAuth2 flow. If a code verifier is used, it must be provided to both methods, and it should also be unique.
        
        Args:
            length: How long the code verifier should be.
        
        Returns:
            A random string consisting of characters a-z, A-Z, 0-9, `-`, `.`, `_`, and `~`.
        """

        return ''.join(secrets.choice(f"{string.ascii_letters}{string.digits}-._~") for _ in range(length))

    def generate_uri(self, scope: Union[str, list[str]], state: Optional[str]=None, generate_code: Optional[bool]=True, code_verifier: Optional[str] = None) -> str:
        """
        Creates an authorization URI to redirect users to with the client information prefilled.
        
        Args:
            scope: A string, or list of strings specifying the scopes for authorization. For example `['openid', 'profile']`
            state: A string that will be returned on the otherside of authorization. It isn't required, but is recommend for security.
            generate_code: Wether to generate a code on return.
            code_verifier: The optional code verifier generated using [`OAuth2App.generate_code_verifier()`][rblxopencloud.OAuth2App.generate_code_verifier]
        
        Returns:
            A URI string starting with `https://apis.roblox.com/oauth/v1/authorize` and the generated parameters.
        """

        params = {
            "client_id": self.id,
            "scope": " ".join(scope) if type(scope) == list else scope,
            "state": state,
            "redirect_uri": self.redirect_uri,
            "response_type": "code" if generate_code else "none",
            "code_challenge": base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).replace(b"=", b"").decode() if code_verifier else None,
            "code_challenge_method": "S256" if code_verifier else None
        }
        return f"https://apis.roblox.com/oauth/v1/authorize?{parse.urlencode({key: value for key, value in params.items() if value is not None})}"

    def from_access_token_string(self, access_token: str) -> PartialAccessToken:
        """
        Creates a [`rblxopencloud.PartialAccessToken`][rblxopencloud.PartialAccessToken] from an access token string, fairly useless due to these tokens expiring after 15 minutes.

        It is also advised the refresh token instead of the access token, and refresh the token each time you need to access information instead of the access token to improve security.
        
        Args:
            access_token: The access token string.

        Returns:
            The Access Token without any metadata such as the scopes, user object, or the refresh token.
        """

        return PartialAccessToken(self, access_token)

    def exchange_code(self, code: str, code_verifier: Optional[str]=None) -> AccessToken:
        """
        Creates a [`rblxopencloud.AccessToken`][rblxopencloud.AccessToken] from an authorization code returned from Roblox.
        
        Args:
            code: The code from the authorization server.
            code_verifier: The string for this OAuth2 flow generated by [`OAuth2App.generate_code_verifier()`][rblxopencloud.OAuth2App.generate_code_verifier].
        
        Returns:
            An Access Token with all metadata including the user object.
        
        Raises:
            InvalidKey: The client ID, secret or redirect URI is invalid.
            InvalidCode: The code is invalid, or the code verifier is missing/invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response, or you have jwt installed.
        """
        response = request_session.post("https://apis.roblox.com/oauth/v1/token", data={
            "client_id": self.id,
            "client_secret": self.__secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "code": code
        }, headers={"user-agent": user_agent})
        id_token = None
        if response.json().get("id_token"):
            if not self.__openid_certs_cache or time.time() - self.__openid_certs_cache_updated > self.openid_certs_cache_seconds:
                certs = request_session.get("https://apis.roblox.com/oauth/v1/certs", headers={"user-agent": user_agent})
                if not certs.ok: raise ServiceUnavailable("Failed to retrieve OpenID certs.")

                self.__openid_certs_cache = []
                for cert in certs.json()["keys"]:
                    self.__openid_certs_cache.append(load_der_public_key(ec.EllipticCurvePublicNumbers(
                        int.from_bytes(base64.urlsafe_b64decode(cert['x'] + '=='), 'big'),
                        int.from_bytes(base64.urlsafe_b64decode(cert['y'] + '=='), 'big'),
                        ec.SECP256R1()
                    ).public_key(default_backend()).public_bytes(
                        Encoding.DER,
                        PublicFormat.SubjectPublicKeyInfo
                    ), default_backend()))
                self.__openid_certs_cache_updated = time.time()

            for cert in self.__openid_certs_cache:
                try:
                    id_token = jwt.decode(response.json()["id_token"], cert,  algorithms=['ES256'], audience=str(self.id))
                    break
                except(AttributeError): raise rblx_opencloudException("jwt conflicts with PyJWT. Please uninstall jwt to fix this issue.")
                except(jwt.exceptions.PyJWTError): pass

        if response.ok: return AccessToken(self, response.json(), id_token)
        elif response.status_code == 400: raise InvalidKey(response.json().get("error_description", "The client id, client secret, or redirect uri is invalid."))
        elif response.status_code == 401: raise InvalidCode(response.json().get("error_description", "The code is invalid, or has been used."))
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def refresh_token(self, refresh_token: str) -> AccessToken:
        """
        Creates a [`rblxopencloud.AccessToken`][rblxopencloud.AccessToken] from a refresh token which is returned in a previous authorization code.
        
        Args:
            refresh_token: The refresh token to be used.
        
        Returns:
            An Access Token with all metadata including the user object.
        
        Raises:
            InvalidKey: The client ID, secret or redirect URI is invalid.
            InvalidCode: The code is invalid, or the code verifier is missing/invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response, or you have jwt installed.
        
        !!! warning
            After refreshing a token, you will get a new refresh token in the [`rblxopencloud.AccessToken`][rblxopencloud.AccessToken] that you need to save.
        """

        response = request_session.post("https://apis.roblox.com/oauth/v1/token", data={
            "client_id": self.id,
            "client_secret": self.__secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }, headers={"user-agent": user_agent})
        if response.ok: return AccessToken(self, response.json(), None)
        elif response.status_code == 400: raise InvalidKey(response.json().get("error_description", "The code, client id, client secret, or redirect uri is invalid."))
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def revoke_token(self, token: str):
        """
        Revokes the authorization for a given access token or refresh token.

        Args:
            token: The access token or refresh token to revoke.
        
        Raises:
            InvalidKey: The client ID or client secret is invalid.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox gave an unexpected response.
        
        !!! warning
            Revoking an access token or refresh token will also invalidate it's pair, so you should only revoke a token once you're completely done with it.
        
        !!! tip
            Both [`AccessToken`][rblxopencloud.AccessToken] and [`PartialAccessToken`][rblxopencloud.PartialAccessToken] have shortcuts for this method. So instead, for exmaple, you could use [`AccessToken.revoke()`][rblxopencloud.AccessToken.revoke] to revoke the token.
        """
        response = request_session.post("https://apis.roblox.com/oauth/v1/token/revoke", data={
            "token": token,
            "client_id": self.id,
            "client_secret": self.__secret
        }, headers={"user-agent": user_agent})
        if response.ok: return
        elif response.status_code == 400: raise InvalidKey("The code, client id, client secret, or redirect uri is invalid.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
