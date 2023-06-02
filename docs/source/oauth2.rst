OAuth2
=============================

.. currentmodule:: rblx-open-cloud

.. class:: OAuth2App(id, secret, redirect_uri, openid_certs_cache_seconds=3600)

   Class for interacting with the API for an OAuth2 app.

   .. versionadded:: 1.3

   :param int id: The app's client ID.
   :param str secret: The app's client secret. *this should be kept safe*
   :param str redirect_uri: The redirect URI that is being used for authorization. If you need to use multiple, you must make seperate :class:`rblx-open-cloud.OAuth2` objects.
   :param int openid_certs_cache_seconds: The number of seconds to cache the openid certs. This defaults to 1 hour, and you can ignore this if you dont know what it does.

   .. attribute:: id 

      The app's client ID

      :type: int
      
   .. attribute:: redirect_uri 

      The app's redirect_uri.

      :type: str

   .. attribute:: openid_certs_cache_seconds

      The number of seconds to cache the openid certs.

      :type: int
   
   .. method:: generate_uri(scope, state=None, generate_code=True)

         Creates an authorization uri with the client information prefilled. It looks nicer than having the authorization uri pasted in.

         :param Union[str, list[str]] scope: A string, or list of strings specifying the scopes for authorization. For example ``['openid', 'profile']``
         :param str state: A string that will be returned on the otherside of authorization. It isn't required, but is recommend for security.
         :param bool generate_code: Wether to generate a code on return. Defaults to ``True``.

         :returns: str
         
   .. method:: from_access_token_string(access_token)

         Creates an :class:`rblx-open-cloud.PartialAccessToken` from an access token string, fairly useless due to these tokens expiring after 15 minutes.

         It is also advised the refresh token instead of the access token, and refresh the token each time you need to access information instead of the access_token to improve security.

         :param str access_token: The access token string.

         :returns: :class:`rblx-open-cloud.PartialAccessToken`
         
   .. method:: exchange_code(code)

         Creates an :class:`rblx-open-cloud.AccessToken` from an authorization code.

         :param str code: The code from the authorization server.

         :returns: :class:`rblx-open-cloud.AccessToken`
         :raises rblx-open-cloud.InvalidKey: The client's ID, secret or redirect uri is invalid.
         :raises rblx-open-cloud.InvalidCode: The authorization is not valid, or has already been exchanged.
         :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
         :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

   .. method:: refresh_token(refresh_token)

         Creates an :class:`rblx-open-cloud.AccessToken` from a refresh token. The new access token will have a different refresh token, and you should store the new refresh token.

         :param str refresh_token: The refresh token to refresh.

         :returns: :class:`rblx-open-cloud.AccessToken`
         :raises rblx-open-cloud.InvalidKey: The client's ID, secret or redirect uri is invalid.
         :raises rblx-open-cloud.InvalidCode: The authorization is not valid, or has already been exchanged.
         :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
         :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

   .. method:: revoke_token(token)

         Revokes the authorization for a given access token or refresh token string.

         :param str token: The refresh token to refresh.

         :returns: None
         :raises rblx-open-cloud.InvalidKey: The client's ID, secret or redirect uri is invalid.
         :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
         :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

         .. warning::

            If the revoking an access token will also revoke it's refresh token, and the same the other way around. Only revoke authorization if you won't need it anymore.

.. class:: AccessToken

    Object that access a user's account.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`OAuth2App.exchange_code` and :meth:`OAuth2App.refresh_token`.

    .. attribute:: app 

        :type: rblx-open-cloud.OAuth2App
    
    .. attribute:: token 

        The access token string. It can be stored in a database, and then turned back into a usable object using :meth:`OAuth2App.from_access_token_string`.

        However, due to the short life span of an access token, and to improve security, it is recommend to only store the refresh token, and use :meth:`OAuth2App.refresh_token` instead.

        :type: str
    
    .. attribute:: refresh_token 

        The authorization's refresh token. It can be converted to a brand new access token when the old access token expires after 15 minutes using :meth:`OAuth2App.refresh_token`.

        :type: str
    
    .. attribute:: scope 

        A list of authorized scopes.

        :type: list[str]
    
    .. attribute:: expires_at 

        The estimated timestamp the access token will expire at.

        :type: datetime.datetime
    
    .. attribute:: user 

        The user who is authorized the application. In some rare occasions, this may be None even though the ``openid`` and ``profile`` scopes were provided. If it is ``None`` you should try :meth:`AccessToken.fetch_userinfo`.

        :type: Optional[rblx-open-cloud.User]
   
    .. method:: fetch_userinfo()

        Returns a :class:`rblx-open-cloud.User` object for this authorization. You can use this object to directly access user resources (like uploading files), if it was authorized.

        :returns: Iterable[:class:`rblx-open-cloud.User`]
        :raises rblx-open-cloud.InsufficientScope: The ``openid`` and/or ``profile`` scopes weren't authorized.
        :raises rblx-open-cloud.InvalidKey: This access token is invalid, expired or has been revoked.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
   
    .. method:: fetch_resources()

        Fetches the authorized accounts (users and groups), and experiences.

        :returns: Iterable[:class:`rblx-open-cloud.Resources`]
        :raises rblx-open-cloud.InsufficientScope: The required scopes weren't authorized.
        :raises rblx-open-cloud.InvalidKey: This access token is invalid, expired or has been revoked.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
   
    .. method:: fetch_token_info()

        Fetches information the token such as the user's id, the authorized scope, and it's expiry time.

        :returns: Iterable[:class:`rblx-open-cloud.AccessTokenInfo`]
        :raises rblx-open-cloud.InsufficientScope: The required scopes weren't authorized.
        :raises rblx-open-cloud.InvalidKey: This access token is invalid, expired or has been revoked.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: PartialAccessToken

    A partial access token, only returned when converted from a string using :meth:`OAuth2App.from_access_token_string`.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`OAuth2App.from_access_token_string`.

    .. attribute:: app 

        :type: rblx-open-cloud.OAuth2App
    
    .. attribute:: token 

        The access token string. It can be stored in a database, and then turned back into a usable object using :meth:`OAuth2.from_access_token_string`.

        However, due to the short life span of an access token, and to improve security, it is recommend to only store the refresh token, and use :meth:`OAuth2.refresh_token` instead.

        :type: Union[datetime.datetime, None]
   
    .. method:: fetch_userinfo()

        Returns a :class:`rblx-open-cloud.User` object for this authorization. You can use this object to directly access user resources (like uploading files), if it was authorized.

        :returns: Iterable[:class:`rblx-open-cloud.User`]
        :raises rblx-open-cloud.InsufficientScope: The ``openid`` and/or ``profile`` scopes weren't authorized.
        :raises rblx-open-cloud.InvalidKey: This access token is invalid, expired or has been revoked.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
   
    .. method:: fetch_resources()

        Fetches the authorized accounts (users and groups), and experiences.

        :returns: Iterable[:class:`rblx-open-cloud.Resources`]
        :raises rblx-open-cloud.InsufficientScope: The required scopes weren't authorized.
        :raises rblx-open-cloud.InvalidKey: This access token is invalid, expired or has been revoked.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
   
    .. method:: fetch_token_info()

        Fetches information the token such as the user's id, the authorized scope, and it's expiry time.

        :returns: Iterable[:class:`rblx-open-cloud.AccessTokenInfo`]
        :raises rblx-open-cloud.InsufficientScope: The required scopes weren't authorized.
        :raises rblx-open-cloud.InvalidKey: This access token is invalid, expired or has been revoked.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
        
.. class:: Resources

    Object that contains all the authorized objects.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`AccessToken.fetch_resources` and :meth:`PartialAccessToken.fetch_resources`.

    .. attribute:: experiences

        A list of experiences authorized for the experience scopes.

        :type: list[rblx-open-cloud.Experience]
    
    .. attribute:: experiences

        A list of accounts (users and groups) authorized for the account scopes.

        :type: list[rblx-open-cloud.User, rblx-open-cloud.Group]

.. class:: AccessTokenInfo

      Object providing information about this access token.

      .. warning::

        This class is not designed to be created by users. It is returned by :meth:`AccessToken.fetch_token_info` and :meth:`PartialAccessToken.fetch_token_info`.

      .. attribute:: active

        Wether the token is still active.

        :type: bool

      .. attribute:: id

        A special string, unique for every authorization and user.

        :type: str

      .. attribute:: client_id

        The App's client ID.

        :type: int

      .. attribute:: user_id

        The authorizing user's ID.

        :type: int

      .. attribute:: scope

        The list of authorized scopes.

        :type: list[str]

      .. attribute:: expires_at

        The timestamp the access token expires at.

        :type: datetime.datetime

      .. attribute:: issued_at

        The timestamp the access token was issued at.

        :type: datetime.datetime