User
=============================

.. currentmodule:: rblx-open-cloud

.. class:: User()

    Class for interacting with the API for a specific user.

    .. versionadded:: 1.1

    .. versionchanged:: 1.3
        Added ``username``, ``display_name`` and ``created_at`` attributes which default to ``None``, unless it is from :ref:`OAuth2 <oauth2>`. Added ``profile_uri`` attribute which is always avaliable.

    :param int id: Your user ID. It appears in your profile URL
    :param str api_key: An API key created from `Creator Dashboard <https://create.roblox.com/credentials>`__. *this should be kept safe, as anyone with the key can use it!*

    .. attribute:: id 

        The user's ID

        :type: int

    .. attribute:: username 

        The user's username. This will always be ``None``, unless it is from :ref:`OAuth2 <oauth2>`

        :type: Optional[str]

    .. attribute:: display_name 

        The user's display name. This will always be ``None``, unless it is from :ref:`OAuth2 <oauth2>`

        :type: Optional[str]

    .. attribute:: created_at 

        The time when user's account was created. This will always be ``None``, unless it is from :ref:`OAuth2 <oauth2>`

        :type: datetime.datetime

    .. attribute:: profile_uri 

        A link to the user's profile.

        :type: str

    .. method:: upload_asset(file, asset_type, name, description, expected_robux_price=0)

        Uploads an asset onto Roblox.

        The ``asset:read`` and ``asset:write`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        .. versionchanged:: 1.3
            It can now raise :class:`rblx-open-cloud.ModeratedText` if the name or description is invalid. It used to raise :class:`rblx-open-cloud.InvalidAsset`.
      
        :param io.BytesIO file: The file opened in bytes to be uploaded.
        :param rblx-open-cloud.AssetType asset_type: The type of asset you're uploading.
        :param str name: The name of your asset.
        :param str description: The description of your asset.
        :param str expected_robux_price: The amount of robux expected to upload. Fails if lower than actual price.

        :returns: Union[:class:`rblx-open-cloud.Asset`, :class:`rblx-open-cloud.PendingAsset`]
        :raises rblx-open-cloud.InvalidAsset: The file is not a supported, or is corrupted
        :raises rblx-open-cloud.ModeratedText: The name or description was moderated by Roblox's chat filter.
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. danger::

            Assets uploaded with Open Cloud can still get your account banned if they're inappropriate.

            For OAuth2 applications, please read `this post by Hooksmith <https://devforum.roblox.com/t/public-beta-building-your-applications-with-oauth-20/2401354/36>`__.
        
        .. note::
            
            Only ``Decal``, ``Audio``, and ``Model`` (as ``fbx``) are supported right now.

    .. method:: update_asset(asset_id, file)

        Updates an existing asset on Roblox.

        The ``asset:read`` and ``asset:write`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        .. versionchanged:: 1.3
            It can now raise :class:`rblx-open-cloud.ModeratedText` if the name or description is invalid. It used to raise :class:`rblx-open-cloud.InvalidAsset`.
        
        :param int asset_id: The ID of the asset to update.
        :param io.BytesIO file: The file opened in bytes to be uploaded.

        :returns: Union[:class:`rblx-open-cloud.Asset`, :class:`rblx-open-cloud.PendingAsset`]
        :raises rblx-open-cloud.ModeratedText: The name or description was moderated by Roblox's chat filter.
        :raises rblx-open-cloud.InvalidAsset: The file is not a supported, or is corrupted
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. danger::

            Assets uploaded with Open Cloud can still get your account banned if they're inappropriate.

            For OAuth2 applications, please read `this post by Hooksmith <https://devforum.roblox.com/t/public-beta-building-your-applications-with-oauth-20/2401354/36>`__.

        .. note::
            
            Only ``Model`` (as ``fbx``) can be updated right now.

        .. danger::

            Assets uploaded with Open Cloud can still get your account banned if they're inappropriate.

        .. note::
            
            Only ``Model`` (as ``fbx``) can be updated right now.
