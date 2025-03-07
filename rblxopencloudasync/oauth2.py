# MIT License

# Copyright (c) 2022-2024 treeben77

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import datetime
import hashlib
import secrets
import string
import time
from typing import Optional, Union
from urllib import parse

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_der_public_key,
)

from .exceptions import BaseException, HttpException, InvalidCode
from .experience import Experience
from .group import Group
from .http import send_request
from .user import User

__all__ = (
    "Resources",
    "AccessTokenInfo",
    "PartialAccessToken",
    "AccessToken",
    "OAuth2App",
)


class AccessTokenInfo:
    """
    Contains information about a access token.

    Attributes:
        active: Wether this access token has not yet expired. Will be `True` \
        even if the authorization has been revoked by the user.
        id: The unique ID for this access token.
        client_id: The ID of the application that the access token belongs to.
        user_id: The ID of the user that the access token belongs to.
        scope: A list of string scopes that were authorized for this access \
        token.
        expires_at: The time this token will expire at, usually 15 minutes \
        after `issued_at`.
        issued_at: The time this token was created by either exchanging a \
        code or refreshing the refresh token.
    """

    def __init__(self, data: dict):
        self.active: bool = data["active"]
        self.id: str = data["jti"]
        self.client_id: int = int(data["client_id"])
        self.user_id: int = data["sub"]
        self.scope: list[str] = data["scope"].split(" ")
        self.expires_at: datetime.datetime = datetime.datetime.fromtimestamp(
            data["exp"]
        )
        self.issued_at: datetime.datetime = datetime.datetime.fromtimestamp(
            data["iat"]
        )

    def __repr__(self) -> str:
        return f'<rblxopencloud.AccessTokenInfo \
id="{self.id}" user_id={self.user_id}>'


class Resources:
    """
    Contains the authorized users, groups, and experiences for the \
    authorization.

    Attributes:
        experiences: A list of authorized \
        [`Experience`][rblxopencloud.Experience] objects.
        accounts: A list of authorized [`User`][rblxopencloud.User] and \
        [`Group`][rblxopencloud.Group] objects for asset uploading.
    """

    def __init__(self, experiences, accounts):
        self.experiences: list[Experience] = experiences
        self.accounts: list[Union[User, Group]] = accounts

    def __repr__(self) -> str:
        return f"<rblxopencloud.Resources \
experiences={self.experiences} accounts={self.accounts}>"


class PartialAccessToken:
    """
    Represents an access token via OAuth2 consent without all information. It \
    allows access to all resources authorized by the user, but not other \
    information like the refresh token.

    Attributes:
        app: The app which this access token belongs to.
        token: The string token which can be stored in a database and later \
        used with [`OAuth2App.from_access_token_string`\
        ][rblxopencloud.OAuth2App.from_access_token_string] to access the \
        resources again.
    """

    def __init__(self, app, access_token) -> None:
        self.app: OAuth2App = app
        self.token: str = access_token

    def __repr__(self) -> str:
        return f'<rblxopencloud.PartialAccessToken \
    token="{self.token[:15]}...">'

    async def fetch_userinfo(self) -> User:
        """
        Fetches user information for this access token.

        Returns:
            The user information with the access token to access authorized \
            apis (such as uploading files).
        """

        _, data, _ = await send_request(
            "GET",
            "oauth/v1/userinfo",
            authorization=f"Bearer {self.token}",
            expected_status=[200],
        )

        user = User(data.get("id") or data.get("sub"), f"Bearer {self.token}")
        user.username = data.get("preferred_username")
        user.display_name = data.get("nickname")
        user.headshot_uri = data.get("picture")
        user.created_at = (
            datetime.datetime.fromtimestamp(data["created_at"])
            if data.get("created_at")
            else None
        )

        return user

    async def fetch_resources(self) -> Resources:
        """
        Fetches the authorized accounts (users and groups) and experiences.

        Returns:
            The objects for authorized accounts and experiences.
        """

        status, data, _ = await send_request(
            "POST",
            "oauth/v1/token/resources",
            expected_status=[200],
            data={
                "token": self.token,
                "client_id": self.app.id,
                "client_secret": self.app._OAuth2App__secret,
            },
        )

        experiences = []
        accounts = []

        api_key = f"Bearer {self.token}"

        for resource in data["resource_infos"]:
            owner = resource["owner"]
            if resource["resources"].get("universe"):
                for experience_id in resource["resources"]["universe"]["ids"]:
                    experience = Experience(experience_id, api_key)
                    if owner["type"] == "User":
                        experience.owner = User(owner["id"], api_key)
                    elif owner["type"] == "Group":
                        experience.owner = Group(owner["id"], api_key)
                    experiences.append(experience)

            if resource["resources"].get("creator"):
                for creator_id in resource["resources"]["creator"]["ids"]:
                    if creator_id == "U":
                        accounts.append(User(owner["id"], api_key))
                    elif creator_id.startswith("U"):
                        accounts.append(User(creator_id[1:], api_key))
                    elif creator_id.startswith("G"):
                        accounts.append(Group(creator_id[1:], api_key))

        return Resources(experiences=experiences, accounts=accounts)

    async def fetch_token_info(self) -> AccessTokenInfo:
        """
        Fetches token information such as the user's id, the authorized \
        scope, and it's expiry time.

        Returns:
            The information about the access token.
        """

        _, data, _ = await send_request(
            "POST",
            "oauth/v1/token/introspect",
            expected_status=[200],
            data={
                "token": self.token,
                "client_id": self.app.id,
                "client_secret": self.app._OAuth2App__secret,
            },
        )

        return AccessTokenInfo(data)

    def revoke(self):
        """
        Shortcut to revoke the access token.
        """
        self.app.revoke_token(self.token)


class AccessToken(PartialAccessToken):
    """
    Represents access via OAuth2 consent. It allows access to all resources \
    authorized by the user.

    Attributes:
        app: The app which this access token belongs to.
        token: The string token which can be stored in a database and later \
        used with [`OAuth2App.from_access_token_string`\
        ][rblxopencloud.OAuth2App.from_access_token_string] to access the \
        resources again.
        refresh_token: The string token which can be stored in a database \
        and later used with [`OAuth2App.refresh_token`\
        ][rblxopencloud.OAuth2App.refresh_token] to get a new refresh token.
        scope: A list of the string scopes authorized for this access token.
        expires_at: The approximate time this access token will expire at.
        user: If `openid` was authorized, the user who granted access. 
    """

    def __init__(self, app, payload, id_token) -> None:
        super().__init__(app, payload["access_token"])
        self.refresh_token: str = payload["refresh_token"]
        self.scope: list[str] = payload["scope"].split(" ")
        self.expires_at: datetime = (
            datetime.datetime.now() + datetime.timedelta(payload["expires_in"])
        )

        if id_token:
            self.user: Optional[User] = User(
                id_token.get("id") or id_token.get("sub"),
                f"Bearer {self.token}",
            )
            self.user.username = id_token.get("preferred_username")
            self.user.display_name = id_token.get("nickname")
            self.user.headshot_uri = id_token.get("picture")
            self.user.created_at = (
                datetime.datetime.fromtimestamp(id_token["created_at"])
                if id_token.get("created_at")
                else None
            )
        else:
            self.user: Optional[User] = None

    def __repr__(self) -> str:
        return f'<rblxopencloud.AccessToken token="{self.token[:15]}..." \
user={self.user})'

    def revoke_refresh_token(self):
        """
        Shortcut to revoke the refresh token.
        """
        self.app.revoke_token(self.refresh_token)


class OAuth2App:
    """
    Represents an OAuth2 app. It is used to exchange codes, refresh tokens, \
    and access the API for authenticated users.

    Args:
        id (int): The app's client ID.
        secret (str): The app's client secret.
        redirect_uri (str): The redirect URI that is being used for \
        authorization. If you need to use multiple, you must make seperate \
        objects.
        openid_certs_cache_seconds (int): The number of seconds to cache the \
        OpenID certs. You can ignore this if you don't know what it does.

    Attributes:
        if (int): The app's client ID.
        secret (str): The app's client secret.
        redirect_uri (str): The redirect URI being used for authorization.
        openid_certs_cache_seconds (int): The number of seconds to cache the \
        OpenID certs.
    """

    def __init__(
        self,
        id: int,
        secret: str,
        redirect_uri: str,
        openid_certs_cache_seconds: int = 3600,
    ):
        self.id: int = id
        self.redirect_uri: str = redirect_uri
        self.__secret: str = secret

        self.openid_certs_cache_seconds: int = openid_certs_cache_seconds
        self.__openid_certs_cache = None
        self.__openid_certs_cache_updated = None

    def __repr__(self) -> str:
        return f'<rblxopencloud.OAuth2App(id={self.id} \
redirect_uri="{self.redirect_uri}")'

    async def __refresh_openid_certs_cache(self):
        certs_status, certs, _ = await send_request("GET", "oauth/v1/certs")
        self.__openid_certs_cache = []
        self.__openid_certs_cache_updated = time.time()

        if certs_status != 200:
            raise HttpException(certs_status, "Failed to fetch OpenID certs")

        for cert in certs["keys"]:
            public_key = (
                ec.EllipticCurvePublicNumbers(
                    int.from_bytes(
                        base64.urlsafe_b64decode(cert["x"] + "=="), "big"
                    ),
                    int.from_bytes(
                        base64.urlsafe_b64decode(cert["y"] + "=="), "big"
                    ),
                    ec.SECP256R1(),
                )
                .public_key(default_backend())
                .public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
            )

            self.__openid_certs_cache.append(load_der_public_key(public_key))

    def generate_code_verifier(self, length: Optional[int] = 128) -> str:
        """
        Generates a code verifier which can be provided to \
        [`OAuth2App.generate_uri`][rblxopencloud.OAuth2App.generate_uri] and \
        [`OAuth2App.exchange_code`][rblxopencloud.OAuth2App.exchange_code] \
        to add extra security to the OAuth2 flow.

        If a code verifier is used, it must be provided to both methods and \
        should also be unique.
        
        Args:
            length (Optional[int]): How long the code verifier should be.

        Returns:
            A string with a length of `length` containing cryptographically \
            generated characters from ascii letters (a-z, A-Z), digits (0-9), \
            `-`, `.`, `_`, and `~`.
        """

        return "".join(
            secrets.choice(f"{string.ascii_letters}{string.digits}-._~")
            for _ in range(length)
        )

    def generate_uri(
        self,
        scope: Union[str, list[str]],
        state: str = None,
        generate_code: bool = True,
        code_verifier: str = None,
    ) -> str:
        """
        Creates an authorization uri with the client information prefilled.
        
        Args:
            scope: A string, or list of strings specifying the scopes for \
            authorization. For example `['openid', 'profile']`
            state: A string that will be returned on the otherside of \
            authorization. It isn't required, but is recommend for security.
            generate_code: Wether to generate a code on return.
            code_verifier: The code verifier generated using \
            [`generate_code_verifier`\
            ][rblxopencloud.OAuth2App.generate_code_verifier]

        Returns:
            The authorization URI starting with \
            `https://apis.roblox.com/oauth/v1/authorize`
        """

        if code_verifier:
            code_challenge = (
                base64.urlsafe_b64encode(
                    hashlib.sha256(code_verifier.encode()).digest()
                )
                .replace(b"=", b"")
                .decode()
            )
        else:
            code_challenge = None

        params = {
            "client_id": self.id,
            "scope": " ".join(scope) if type(scope) == list else scope,
            "state": state,
            "redirect_uri": self.redirect_uri,
            "response_type": "code" if generate_code else "none",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256" if code_verifier else None,
        }

        params = parse.urlencode(
            {key: value for key, value in params.items() if value is not None}
        )

        return f"https://apis.roblox.com/oauth/v1/authorize?{params}"

    def from_access_token_string(
        self, access_token: str
    ) -> PartialAccessToken:
        """
        Creates a [`PartialAccessToken`][rblxopencloud.PartialAccessToken] \
        from an access token string, fairly useless due to these tokens \
        expiring after 15 minutes.

        It is also advised the refresh token instead of the access token, and \
        refresh the token each time you need to access information instead of \
        the access_token to improve security.

        Args:
            access_token: the access token string.

        Returns:
            A partial access token for the provided access token string.
        """

        return PartialAccessToken(self, access_token)

    async def exchange_code(
        self, code: str, code_verifier: Optional[str] = None
    ) -> AccessToken:
        """
        Exchanges an authorization code for an access token which can utilize \
        granted scopes.
        
        Attributes:
            code: The code from the authorization server.
            code_verifier: The code verifier string for this OAuth2 flow \
            generated by [`generate_code_verifier`\
            ][rblxopencloud.OAuth2App.generate_code_verifier]
        
        Returns:
            The access token created from the provided code.
        """

        status, data, _ = await send_request(
            "POST",
            "oauth/v1/token",
            expected_status=[200, 401],
            data={
                "client_id": self.id,
                "client_secret": self.__secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
                "code": code,
            },
        )

        if status == 401:
            raise InvalidCode(
                status, data.get("error_description", "The code is invalid")
            )

        id_token = None
        if data.get("id_token"):
            if (
                not self.__openid_certs_cache
                or time.time() - self.__openid_certs_cache_updated
                > self.openid_certs_cache_seconds
            ):
                await self.__refresh_openid_certs_cache()

            for cert in self.__openid_certs_cache:
                try:
                    id_token = jwt.decode(
                        data["id_token"],
                        cert,
                        algorithms=["ES256"],
                        audience=str(self.id),
                    )
                    break
                except AttributeError:
                    raise BaseException(
                        "jwt and PyJWT installed. Please uninstall jwt."
                    )
                except jwt.exceptions.PyJWTError:
                    pass

        return AccessToken(self, data, id_token)

    async def refresh_token(self, refresh_token: str) -> AccessToken:
        """
        Refrehes an access token for a new access token with a refresh token. \
        After refreshing, a new refresh token is provided to be stored.
        
        Attributes:
            refresh_token: The refresh token to refresh.

        Returns:
            The new access token from the refresh token.
        """

        _, data, _ = await send_request(
            "POST",
            "oauth/v1/token",
            expected_status=[200],
            data={
                "client_id": self.id,
                "client_secret": self.__secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

        return AccessToken(self, data, None)

    async def revoke_token(self, token: str):
        """
        Revokes the authorization for a given access or refresh token.

        Args:
            token: The access or refresh token to revoke.
        """

        await send_request(
            "POST",
            "oauth/v1/token/revoke",
            expected_status=[200],
            data={
                "client_id": self.id,
                "client_secret": self.__secret,
                "token": token,
            },
        )
