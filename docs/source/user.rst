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

        The ``openid`` scope is required if authorized via `OAuth2 </oauth2>`__.

        :type: int

    .. attribute:: username 

        The user's username. This will always be ``None``, unless it is from :doc:`oauth2`

        The ``openid`` and ``profile`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        :type: Optional[str]

    .. attribute:: display_name 

        The user's display name. This will always be ``None``, unless it is from :doc:`oauth2`

        The ``openid`` and ``profile`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        :type: Optional[str]

    .. attribute:: headshot_uri 

        The URI of the user's avatar headshot. This will always be ``None``, unless it is from :doc:`oauth2`

        The ``openid`` and ``profile`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        :type: Optional[str]

    .. attribute:: created_at 

        The time when user's account was created. This will always be ``None``, unless it is from :doc:`oauth2`

        The ``openid`` and ``profile`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        :type: datetime.datetime

    .. attribute:: profile_uri 

        A link to the user's profile.

        The ``openid`` scope is required if authorized via `OAuth2 </oauth2>`__.

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

    .. method:: list_inventory(limit=None, only_collectibles=False, assets=False, badges=False, game_passes=False, private_servers=False)

        Interates :class:`rblx-open-cloud.InventoryItem` for items in the user's inventory. If ``only_collectibles``, ``assets``, ``badges``, ``game_passes``, and ``private_servers`` are ``False``, then all inventory items are returned.
        
        The example below would iterate through every item in the user's inventory.
        
        .. code:: python

            for item in experience.list_inventory():
                print(item)
        
        The ``user.inventory-item:read`` scope is required if authorized via `OAuth2 </oauth2>`__.

        .. versionadded:: 1.5

        :param Optional[int] limit: The maximum number of inventory items to iterate. This can be ``None`` to return all items.
        :param Optional[bool] only_collectibles: Wether the only inventory assets iterated are collectibles (limited items).
        :param Optional[Union[list[InventoryAssetType], list[int], bool]] assets: If this is ``True``, then it will return all assets, if it is a list of IDs, it will only return assets with the provided IDs, and if it is a list of :class:`rblx-open-cloud.InventoryAssetType` then it will only return assets of these types.
        :param Optional[Union[list[int], bool]] badges: If this is ``True``, then it will return all badges, but if it is a list of IDs, it will only return badges with the provided IDs.
        :param Optional[Union[list[int], bool]] game_passes: If this is ``True``, then it will return all game passes, but if it is a list of IDs, it will only return game passes with the provided IDs.
        :param Optional[Union[list[int], bool]] private_servers: If this is ``True``, then it will return all private servers, but if it is a list of IDs, it will only return private servers with the provided IDs.

        :returns: Iterable[Union[:class:`rblx-open-cloud.InventoryAsset`, :class:`rblx-open-cloud.InventoryBadge`, :class:`rblx-open-cloud.InventoryGamePass`, :class:`rblx-open-cloud.InventoryPrivateServer`]]
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to list data stores.
        :raises rblx-open-cloud.PermissionDenied: The user's inventory is not public.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. note::

            You can access anyone's inventory if it is public. Otherwise, you must use OAuth2 to obtain consent.

.. class:: InventoryItem()

    Represents an inventory item.

    .. versionadded:: 1.5

    .. warning::

        This class is not designed to be created by users. It is inherited by :class:`rblx-open-cloud.InventoryAsset`, :class:`rblx-open-cloud.InventoryBadge`, :class:`rblx-open-cloud.InventoryGamePass`, and :class:`rblx-open-cloud.InventoryPrivateServer`.
    
    .. attribute:: id 

        The item's ID

        :type: int

.. class:: InventoryAsset()

    Represents an asset in the user's inventory.
    
    .. versionadded:: 1.5

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`User.list_inventory`.

    .. attribute:: id 

        The asset's ID

        :type: int

    .. attribute:: type 

        The item asset type.

        :type: :class:`rblx-open-cloud.InventoryAssetType`
    
    .. attribute:: instance_id 

        A unique ID that identifies the specific "copy" of the item.

        :type: int
    
    .. attribute:: serial_number  

        The serial number of a collectable.

        :type: int
    
    .. attribute:: collectable_state

        Wether the collectable is in the holding period or not.

        :type: Optional[InventoryItemState]

    .. attribute:: collectable_item_id 

        The collectable's asset ID. This is not the same as :attr:`InventoryAsset.id`.

        :type: Optional[str]
        
    .. attribute:: collectable_instance_id 

        The collectable's instance ID. This is not the same as :attr:`InventoryAsset.instance_id`.

        :type: Optional[str]

.. class:: InventoryBadge()

    Represents a badge in a user's inventory.
    
    .. versionadded:: 1.5

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`User.list_inventory`.

    .. attribute:: id 

        The badge's ID

        :type: int

.. class:: InventoryGamePass()

    Represents a gamepass in a user's inventory.
    
    .. versionadded:: 1.5

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`User.list_inventory`.

    .. attribute:: id 

        The game pass's ID

        :type: int

.. class:: InventoryPrivateServer()

    Represents a private server in a user's inventory.
    
    .. versionadded:: 1.5

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`User.list_inventory`.

    .. attribute:: id 

        The private server's ID

        :type: int

.. class:: InventoryAssetType()

    Enum to denote what type an asset is.
    
    .. versionadded:: 1.5

    .. attribute:: Unknown

        An unknown asset type (e.g. an unimplemented type)

    .. attribute:: ClassicTShirt

    .. attribute:: Audio

    .. attribute:: Hat

    .. attribute:: Model

    .. attribute:: ClassicShirt

    .. attribute:: ClassicPants

    .. attribute:: Decal

    .. attribute:: ClassicHead

    .. attribute:: Face

    .. attribute:: Gear

    .. attribute:: Animation

    .. attribute:: Torso

    .. attribute:: RightArm

    .. attribute:: LeftArm

    .. attribute:: LeftLeg

    .. attribute:: RightLeg

    .. attribute:: Package

    .. attribute:: Plugin

    .. attribute:: MeshPart

    .. attribute:: HairAccessory

    .. attribute:: FaceAccessory

    .. attribute:: NeckAccessory

    .. attribute:: ShoulderAccessory

    .. attribute:: FrontAccessory

    .. attribute:: BackAccessory

    .. attribute:: WaistAccessory

    .. attribute:: ClimbAnimation

    .. attribute:: DeathAnimation

    .. attribute:: FallAnimation

    .. attribute:: IdleAnimation

    .. attribute:: JumpAnimation

    .. attribute:: RunAnimation

    .. attribute:: SwimAnimation

    .. attribute:: WalkAnimation

    .. attribute:: PoseAnimation

    .. attribute:: EmoteAnimation

    .. attribute:: Video

    .. attribute:: TShirtAccessory

    .. attribute:: ShirtAccessory

    .. attribute:: PantsAccessory

    .. attribute:: JacketAccessory

    .. attribute:: SweaterAccessory

    .. attribute:: ShortsAccessory

    .. attribute:: LeftShoeAccessory

    .. attribute:: RightShoeAccessory

    .. attribute:: DressSkirtAccessory

    .. attribute:: EyebrowAccessory

    .. attribute:: EyelashAccessory

    .. attribute:: MoodAnimation

    .. attribute:: DynamicHead

    .. attribute:: CreatedPlace

    .. attribute:: PurchasedPlace

.. class:: InventoryItemState()

    Enum to denote wether a collectable is avaliable to be sold or is still in the holding period.
    
    .. versionadded:: 1.5

    .. attribute:: Unknown

        The item state is currently unknown.

    .. attribute:: Available

    .. attribute:: Hold