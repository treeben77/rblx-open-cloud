Creator
=============================

.. currentmodule:: rblx-open-cloud

.. class:: Creator()

    Represents an object that can upload assets, usually a user or a group.

    .. versionadded:: 1.1

    .. warning::

        This class is not designed to be created by users. It a inherited by :class:`rblx-open-cloud.User` and :class:`rblx-open-cloud.Group`.

    .. attribute:: id 

        The Creator's ID

        :type: int

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
        :param int expected_robux_price: The amount of robux expected to upload. Fails if lower than actual price.

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

.. class:: Asset()

    Represents an processed asset uploaded to Roblox.

    .. versionadded:: 1.1

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`Creator.upload_asset` and :meth:`Creator.update_asset`.

    .. attribute:: id 

        The asset's ID

        :type: int

    .. attribute:: name 

        The asset's name

        :type: str

    .. attribute:: description 

        The asset's description

        :type: str

    .. attribute:: creator 

        The asset's creator

        :type: Union[:class:`rblx-open-cloud.Creator`, :class:`rblx-open-cloud.User`, :class:`rblx-open-cloud.Group`]
    
    .. attribute:: revision_id 

        The ID of the asset's current version/revision

        :type: Optional[int]
    
    .. attribute:: revision_time

        The time the asset was last update

        :type: Optional[datetime.datetime]
    
    .. attribute:: type 

        The asset's type

        :type: :class:`rblx-open-cloud.AssetType`
    
.. class:: PendingAsset()

    Represents an asset uploaded to Roblox, but hasn't been processed yet.

    .. versionadded:: 1.1

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`Creator.upload_asset` and :meth:`Creator.update_asset`.

    .. method:: fetch_operation()

        Checks if the asset has finished proccessing, if so returns the :class:`rblx-open-cloud.Asset` object.

        :returns: Optional[:class:`rblx-open-cloud.Asset`]
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: AssetType()

    Enum to denote what type an asset is.

    .. versionadded:: 1.1

    .. attribute:: Unknown 

        An unknown asset type (e.g. an unimplemented type)

    .. attribute:: Decal 

        A decal asset type
    
    .. attribute:: Audio 

        An audio asset type
    
    .. attribute:: Model 

        A model asset type (fbx)