Creator
=============================

.. currentmodule:: rblx-open-cloud

.. class:: Creator()

    Class for interacting with the API to upload assets to a user or group.

    .. versionadded:: 1.1

    .. warning::

        This class is not designed to be created by users. It a inherited by :class:`rblx-open-cloud.User` and :class:`rblx-open-cloud.Group`.

    .. attribute:: id 

        The Creator's ID

        :type: int

    .. method:: upload_asset(file, asset_type, name, description, expected_robux_price=0)

        Uploads an asset onto Roblox.
        
        :param io.BytesIO file: The file opened in bytes to be uploaded.
        :param rblx-open-cloud.AssetType: The type of asset you're uploading.
        :param str: The name of your asset.
        :param str: The description of your asset.

        :returns: Union[:class:`rblx-open-cloud.Asset`, :class:`rblx-open-cloud.PendingAsset`]
        :raises rblx-open-cloud.InvalidAsset: The file is not a supported, or is corrupted
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. danger::

            Assets are uploaded under your name, and can get your account banned! Be very careful what assets you choose to upload.

        .. note::
            
            Only `Decal`, `Audio`, and `Model` (as `fbx`) are supported right now.

    .. method:: update_asset(asset_id, file)

        Updates an existing asset on Roblox.
        
        :param int asset_id: The ID of the asset to update.
        :param io.BytesIO file: The file opened in bytes to be uploaded.

        :returns: Union[:class:`rblx-open-cloud.Asset`, :class:`rblx-open-cloud.PendingAsset`]
        :raises rblx-open-cloud.InvalidAsset: The file is not a supported, or is corrupted
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. danger::

            Assets are uploaded under your name, and can get your account banned! Be very careful what assets you choose to upload.

        .. note::
            
            Only `Model` (as `fbx`) can be updated right now.

.. class:: Asset()

    Contains data about an asset, such as it's id, name, and type.

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

    Class for assets which aren't processed yet.

    .. versionadded:: 1.1

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`Creator.upload_asset` and :meth:`Creator.update_asset`.

    .. method:: fetch_operation()

        Fetches the asset info, if completed processing.

        :returns: Optional[:class:`rblx-open-cloud.Asset`]
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: AssetType()

    Enum to denote what type an asset is.

    .. versionadded:: 1.1

    .. attribute:: Unkown 

        An unkown asset type (e.g. an unimplemented type)

    .. attribute:: Decal 

        An decal asset type
    
    .. attribute:: Audio 

        An audio asset type
    
    .. attribute:: Model 

        An model asset type (fbx)