User
=============================

.. currentmodule:: rblx-open-cloud

.. class:: User()

    Represents a user on Roblox. It is used to provide information about a user in :doc:`oauth2`, and to upload assets to a user.

    .. versionadded:: 1.1

    .. versionchanged:: 1.3
        Added ``username``, ``display_name`` and ``created_at`` attributes which default to ``None``, unless it is from :doc:`oauth2`. Added ``profile_uri`` attribute which is always avaliable.

    :param int id: The user's ID.
    :param str api_key: Your API key created from `Creator Dashboard <https://create.roblox.com/credentials>`__ with access to this user.

    .. attribute:: id 

        The user's ID

        :type: int

    .. attribute:: username 

        The user's username. This will always be ``None``, unless it is from :doc:`oauth2`

        :type: Optional[str]

    .. attribute:: display_name 

        The user's display name. This will always be ``None``, unless it is from :doc:`oauth2`

        :type: Optional[str]

    .. attribute:: created_at 

        The time when user's account was created. This will always be ``None``, unless it is from :doc:`oauth2`

        :type: datetime.datetime

    .. attribute:: profile_uri 

        A link to the user's profile.

        :type: str

    .. method:: upload_asset(file, asset_type, name, description, expected_robux_price=0)

        Uploads the file onto roblox as an asset with the provided name and description. It will return :class:`rblx-open-cloud.Asset` if the asset is processed instantly, otherwise it will return :class:`rblx-open-cloud.PendingAsset`. The following asset types and file formats are accepted:

        .. list-table::
            :widths: 50 50
            :header-rows: 1

            * - Asset Type
              - File Formats
            * - :attr:`rblx-open-cloud.AssetType.Decal`
              - ``.png``, ``.jpeg``, ``.bmp``, ``.tga``
            * - :attr:`rblx-open-cloud.AssetType.Audio`
              - ``.mp3``, ``.ogg``
            * - :attr:`rblx-open-cloud.AssetType.Model`
              - ``.fbx``

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

            Assets uploaded with Open Cloud can still get your account moderated if they break the Terms of Service.

            For OAuth2 applications, please read `this post by Hooksmith <https://devforum.roblox.com/t/public-beta-building-your-applications-with-oauth-20/2401354/36>`__.

    .. method:: update_asset(asset_id, file)

        Updates the file for an existing assest on Roblox. It will return :class:`rblx-open-cloud.Asset` if the asset is processed instantly, otherwise it will return :class:`rblx-open-cloud.PendingAsset`. The following asset types and file formats can be updated:

        .. list-table::
            :widths: 50 50
            :header-rows: 1

            * - Asset Type
              - File Formats
            * - :attr:`rblx-open-cloud.AssetType.Model`
              - ``.fbx``

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

            Assets uploaded with Open Cloud can still get your account moderated if they break the Terms of Service.

            For OAuth2 applications, please read `this post by Hooksmith <https://devforum.roblox.com/t/public-beta-building-your-applications-with-oauth-20/2401354/36>`__.
