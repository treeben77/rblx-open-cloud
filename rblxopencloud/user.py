from .exceptions import rblx_opencloudException, InvalidKey, PermissionDenied, NotFound, RateLimited, ServiceUnavailable
from .creator import Creator
from .exceptions import rblx_opencloudException, InvalidKey, NotFound, RateLimited, ServiceUnavailable
import datetime

from typing import Optional, Iterable, Union, TYPE_CHECKING
from enum import Enum
from . import user_agent, request_session

if TYPE_CHECKING:
    from .group import GroupMember

__all__ = (
    "User",
    "InventoryAssetType",
    "InventoryItemState",
    "InventoryItem",
    "InventoryAsset",
    "InventoryBadge",
    "InventoryGamePass",
    "InventoryPrivateServer"
)

class InventoryAssetType(Enum):
    """
    Enum denoting what type a [`rblxopencloud.InventoryAsset`][rblxopencloud.InventoryAsset] is.

    Attributes:
        Unknown (0): The asset type is unknown.
        ClassicTShirt (1):
        Audio (2):
        Hat (3):
        Model (4):
        ClassicShirt (5):
        ClassicPants (6):
        Decal (7):
        ClassicHead (8):
        Face (9):
        Gear (10):
        Animation (11):
        Torso (12):
        RightArm (13):
        LeftArm (14):
        LeftLeg (15):
        RightLeg (16):
        Package (17):
        Plugin (18):
        MeshPart (19):
        HairAccessory (20):
        FaceAccessory (21):
        NeckAccessory (22):
        ShoulderAccessory (23):
        FrontAccessory (24):
        BackAccessory (25):
        WaistAccessory (26):
        ClimbAnimation (27):
        DeathAnimation (28):
        FallAnimation (29):
        IdleAnimation (30):
        JumpAnimation (31):
        RunAnimation (32):
        SwimAnimation (33):
        WalkAnimation (34):
        PoseAnimation (35):
        EmoteAnimation (36):
        Video (37):
        TShirtAccessory (38):
        ShirtAccessory (39):
        PantsAccessory (40):
        JacketAccessory (41):
        SweaterAccessory (42):
        ShortsAccessory (43):
        LeftShoeAccessory (44):
        RightShoeAccessory (45):
        DressSkirtAccessory (46):
        EyebrowAccessory (47):
        EyelashAccessory (48):
        MoodAnimation (49):
        DynamicHead (50):
        CreatedPlace (51):
        PurchasedPlace (52):
    """
    Unknown = 0
    ClassicTShirt = 1
    Audio = 2
    Hat = 3
    Model = 4
    ClassicShirt = 5
    ClassicPants = 6
    Decal = 7
    ClassicHead = 8
    Face = 9
    Gear = 10
    Animation = 11
    Torso = 12
    RightArm = 13
    LeftArm = 14
    LeftLeg = 15
    RightLeg = 16
    Package = 17
    Plugin = 18
    MeshPart = 19
    HairAccessory = 20
    FaceAccessory = 21
    NeckAccessory = 22
    ShoulderAccessory = 23
    FrontAccessory = 24
    BackAccessory = 25
    WaistAccessory = 26
    ClimbAnimation = 27
    DeathAnimation = 28
    FallAnimation = 29
    IdleAnimation = 30
    JumpAnimation = 31
    RunAnimation = 32
    SwimAnimation = 33
    WalkAnimation = 34
    PoseAnimation = 35
    EmoteAnimation = 36
    Video = 37
    TShirtAccessory = 38
    ShirtAccessory = 39
    PantsAccessory = 40
    JacketAccessory = 41
    SweaterAccessory = 42
    ShortsAccessory = 43
    LeftShoeAccessory = 44
    RightShoeAccessory = 45
    DressSkirtAccessory = 46
    EyebrowAccessory = 47
    EyelashAccessory = 48
    MoodAnimation = 49
    DynamicHead = 50
    CreatedPlace = 51
    PurchasedPlace = 52

class InventoryItemState(Enum):
    """
    Enum representing wether the collectable item is in hold, or if the user can sell it.
    
    Attributes:
        Unknown (1): The current state is unknown.
        Available (2): The user could list the collectable for sale if they have premium.
        Hold (3): The user recently purchased the collectable and can't be sold yet. 
    """

    Unknown = 0
    Available = 1
    Hold = 2

asset_type_strings = {
    "INVENTORY_ITEM_ASSET_TYPE_UNSPECIFIED": InventoryAssetType.Unknown,
    "CLASSIC_TSHIRT": InventoryAssetType.ClassicTShirt,
    "AUDIO": InventoryAssetType.Audio,
    "HAT": InventoryAssetType.Hat,
    "MODEL": InventoryAssetType.Model,
    "CLASSIC_SHIRT": InventoryAssetType.ClassicShirt,
    "CLASSIC_PANTS": InventoryAssetType.ClassicPants,
    "DECAL": InventoryAssetType.Decal,
    "CLASSIC_HEAD": InventoryAssetType.ClassicHead,
    "FACE": InventoryAssetType.Face,
    "GEAR": InventoryAssetType.Gear,
    "ANIMATION": InventoryAssetType.Animation,
    "TORSO": InventoryAssetType.Torso,
    "RIGHT_ARM": InventoryAssetType.RightArm,
    "LEFT_ARM": InventoryAssetType.LeftArm,
    "LEFT_LEG": InventoryAssetType.LeftLeg,
    "RIGHT_LEG": InventoryAssetType.RightLeg,
    "PACKAGE": InventoryAssetType.Package,
    "PLUGIN": InventoryAssetType.Plugin,
    "MESH_PART": InventoryAssetType.MeshPart,
    "HAIR_ACCESSORY": InventoryAssetType.HairAccessory,
    "FACE_ACCESSORY": InventoryAssetType.FaceAccessory,
    "NECK_ACCESSORY": InventoryAssetType.NeckAccessory,
    "SHOULDER_ACCESSORY": InventoryAssetType.ShoulderAccessory,
    "FRONT_ACCESSORY": InventoryAssetType.FrontAccessory,
    "BACK_ACCESSORY": InventoryAssetType.BackAccessory,
    "WAIST_ACCESSORY": InventoryAssetType.WaistAccessory,
    "CLIMB_ANIMATION": InventoryAssetType.ClimbAnimation,
    "DEATH_ANIMATION": InventoryAssetType.DeathAnimation,
    "FALL_ANIMATION": InventoryAssetType.FallAnimation,
    "IDLE_ANIMATION": InventoryAssetType.IdleAnimation,
    "JUMP_ANIMATION": InventoryAssetType.JumpAnimation,
    "RUN_ANIMATION": InventoryAssetType.RunAnimation,
    "SWIM_ANIMATION": InventoryAssetType.SwimAnimation,
    "WALK_ANIMATION": InventoryAssetType.WalkAnimation,
    "POSE_ANIMATION": InventoryAssetType.PoseAnimation,
    "EMOTE_ANIMATION": InventoryAssetType.EmoteAnimation,
    "VIDEO": InventoryAssetType.Video,
    "TSHIRT_ACCESSORY": InventoryAssetType.TShirtAccessory,
    "SHIRT_ACCESSORY": InventoryAssetType.ShirtAccessory,
    "PANTS_ACCESSORY": InventoryAssetType.PantsAccessory,
    "JACKET_ACCESSORY": InventoryAssetType.JacketAccessory,
    "SWEATER_ACCESSORY": InventoryAssetType.SweaterAccessory,
    "SHORTS_ACCESSORY": InventoryAssetType.ShortsAccessory,
    "LEFT_SHOE_ACCESSORY": InventoryAssetType.LeftShoeAccessory,
    "RIGHT_SHOE_ACCESSORY": InventoryAssetType.RightShoeAccessory,
    "DRESS_SKIRT_ACCESSORY": InventoryAssetType.DressSkirtAccessory,
    "EYEBROW_ACCESSORY": InventoryAssetType.EyebrowAccessory,
    "EYELASH_ACCESSORY": InventoryAssetType.EyelashAccessory,
    "MOOD_ANIMATION": InventoryAssetType.MoodAnimation,
    "DYNAMIC_HEAD": InventoryAssetType.DynamicHead,
    "CREATED_PLACE": InventoryAssetType.CreatedPlace,
    "PURCHASED_PLACE": InventoryAssetType.PurchasedPlace
}

state_type_strings = {
    "COLLECTIBLE_ITEM_INSTANCE_STATE_UNSPECIFIED": InventoryItemState.Unknown,
    "AVAILABLE": InventoryItemState.Available,
    "HOLD": InventoryItemState.Hold
}

class InventoryItem():
    """
    Represents a base item in a user's inventory. This method is usually not returned, however it bases multiple other classes.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`User.list_inventory()`][rblxopencloud.User.list_inventory].

    Attributes:
        id (int): The ID of the inventory item.
    """

    def __init__(self, id) -> None:
        self.id: int = id

    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryItem(id={self.id}"

class InventoryAsset(InventoryItem):
    """
    Represents a basic inventory item, such as avatar items, and development items.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`User.list_inventory()`][rblxopencloud.User.list_inventory].

    Attributes:
        id (int): The ID of the inventory item.
        type (InventoryAssetType): The asset's type.
        instance_id (int): The unique ID of this asset's instance.
        collectable_item_id (Optional[str]): A unique item UUID for collectables.
        collectable_instance_id (Optional[str]): A unique instance UUID for collectables.
        serial_number (Optional[int]): The serial number of the collectable.
        collectable_state (Optional[InventoryItemState]): Wether the item is ready for sale or in hold.
    """

    def __init__(self, data) -> None:
        super().__init__(data["assetId"])
        self.type: InventoryAssetType = InventoryAssetType(asset_type_strings.get(data["inventoryItemAssetType"], InventoryAssetType.Unknown))
        self.instance_id: int = data["instanceId"]
        self.collectable_item_id: Optional[str] = data.get("collectibleDetails", {}).get("itemId", None)
        self.collectable_instance_id: Optional[str] = data.get("collectibleDetails", {}).get("instanceId", None)
        self.serial_number: Optional[int] = data.get("collectibleDetails", {}).get("serialNumber", None)

        collectable_state = data.get("collectibleDetails", {}).get("instanceState", None)
        self.collectable_state: Optional[InventoryItemState] = InventoryItemState(state_type_strings.get(collectable_state, InventoryItemState.Unknown)) if collectable_state else None

    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryAsset(id={self.id}, type={self.type})"

class InventoryBadge(InventoryItem):
    """
    Represents a badge in a user's inventory.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`User.list_inventory()`][rblxopencloud.User.list_inventory].

    Attributes:
        id (int): The ID of the badge.
    """

    def __init__(self, data) -> None:
        super().__init__(data["badgeId"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryBadge(id={self.id})"

class InventoryGamePass(InventoryItem):
    """
    Represents a game pass in a user's inventory.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`User.list_inventory()`][rblxopencloud.User.list_inventory].

    Attributes:
        id (int): The ID of the game pass.
    """

    def __init__(self, data) -> None:
        super().__init__(data["gamePassId"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryGamePass(id={self.id})"

class InventoryPrivateServer(InventoryItem):
    """
    Represents a private server in a user's inventory.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`User.list_inventory()`][rblxopencloud.User.list_inventory].

    Attributes:
        id (int): The ID of the private server item.
    """
    
    def __init__(self, data) -> None:
        super().__init__(data["privateServerId"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryPrivateServer(id={self.id})"

class User(Creator):
    """
    Represents a user on Roblox. It is used to provide information about a user in OAuth2, fetch information about a user, and access their resources.

    Args:
        id: The user's ID.
        api_key: The API key created on the [Creator Dashboard](https://create.roblox.com/credentials) with access to the user.
    
    Attributes:
        id (int): The user's ID. The `openid` scope is required for OAuth2 authorization.
        username (Optional[str]): The user's username, only avalible from OAuth2 with the `profile` scope.
        display_name (Optional[str]): The user's display name, only avalible from OAuth2 with the `profile` scope.
        profile_uri (str): A URL to the user's profile on Roblox. The `openid` scope is required for OAuth2 authorization.
        headshot_uri (Optional[str]): A URI to Roblox's CDN for the user's avatar headshot, only avalible from OAuth2 with the `profile` scope. Example value: `https://tr.rbxcdn.com/0f00ba3ab40808dbbbf3410a5a637d2e/150/150/AvatarHeadshot/Png`
        created_at (Optional[datetime.datetime]): The timestamp the user created their account, only avalible from OAuth2 with the `profile` scope.
    """

    def __init__(self, id: int, api_key: str) -> None:
        self.username: Optional[str] = None
        self.id: int = id
        self.display_name: Optional[str] = None
        self.profile_uri: str = f"https://roblox.com/users/{self.id}/profile"
        self.headshot_uri: Optional[str] = None
        self.created_at: Optional[datetime.datetime] = None

        self.__api_key = api_key

        super().__init__(id, api_key, "User")

    def list_groups(self, limit: Optional[int]=None) -> Iterable["GroupMember"]:
        """
        Returns an Iterable of [`rblxopencloud.GroupMember`][rblxopencloud.GroupMember] for every group the user is a member of.

        **The `openid` and `group:read` scopes are required for OAuth2 authorization.**

        Example:
            This will print every group the user is a member of, and their role ID in that group. 
            ```py
            for member in user.list_groups():
                print(member.group, member.role_id)
            ```
            If you'd like the keys in a list, you can use the list method:
            ```py
            list(user.list_groups())
            ```

        Args:
            limit: Will not return more groups than this number. Set to `None` for no limit.
        
        Returns:
            An Iterable of group memberships.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to list data store keys, or is from an invalid IP address.
            NotFound: The user does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """

        from .group import GroupMember

        filter = None

        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/-/memberships",
                headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent}, params={
                "maxPageSize": limit if limit and limit <= 99 else 99,
                "filter": f"user == 'users/{self.id}'",
                "pageToken": nextcursor if nextcursor else None
            })

            if response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
            elif response.status_code == 401: raise InvalidKey(response.text)
            elif response.status_code == 404: raise NotFound(response.json()["message"])
            elif response.status_code == 429: raise RateLimited("You're being rate limited!")
            elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
            
            data = response.json()
            for member in data["groupMemberships"]:
                yields += 1
                
                yield GroupMember(member, self.__api_key)
            nextcursor = data.get("nextPageToken")
            if not nextcursor: break

        pass
    
    def __repr__(self) -> str:
        return f"rblxopencloud.User({self.id})"

    def list_inventory(self, limit: Optional[int]=None, only_collectibles: Optional[bool]=False, assets: Optional[Union[list[InventoryAssetType], list[int], bool]]=None, badges: Optional[Union[list[int], bool]]=False, game_passes: Optional[Union[list[int], bool]]=False, private_servers: Optional[Union[list[int], bool]]=False) -> Iterable[Union[InventoryAsset, InventoryBadge, InventoryGamePass, InventoryPrivateServer]]:
        """
        Returns an Iterable of [`rblxopencloud.InventoryItem`][rblxopencloud.InventoryItem] for every item in the user's inventory. If `only_collectibles`, `assets`, `badges`, `game_passes`, and `private_servers` are all `False`/`None`, then all inventory items are returned.

        **The `openid` and `user.inventory-item:read` scopes are required for OAuth2 authorization.**

        Example:
            This will print every item in the user's inventory. 
            ```py
            for item in user.list_inventory():
                print(item)
            ```
            If you'd like the items in a list, you can use the list method:
            ```py
            list(user.list_inventory())
            ```

        Args:
            only_collectibles: Wether the only inventory assets iterated are collectibles (limited items). If `True` and `assets` is `None`, then `assets` will default to `True`.
            assets: If this is `True`, then it will return all assets, if it is a list of IDs, it will only return assets with the provided IDs, and if it is a list of [`rblxopencloud.InventoryAssetType`][rblxopencloud.InventoryAssetType] then it will only return assets of these types.
            badges: If this is `True`, then it will return all badges, but if it is a list of IDs, it will only return badges with the provided IDs.
            game_passes: If this is `True`, then it will return all game passes, but if it is a list of IDs, it will only return game passes with the provided IDs.
            private_servers: If this is `True`, then it will return all private servers, but if it is a list of IDs, it will only return private servers with the provided IDs.
            limit: Will not return more groups than this number. Set to `None` for no limit.
        
        Returns:
            An Iterable of all the items in the user's inventory.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to list data store keys, or is from an invalid IP address.
            PermissionDenied: The user's inventory is private, and you do not have authorization to access it.
            NotFound: The user does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.

        !!! note
            If the user's inventory is private, then you need to gain consent from either OAuth2, or by owning the API key. Otherwise, this method will raise [`rblxopencloud.PermissionDenied`][rblxopencloud.PermissionDenied]!
        """

        filter_dict = {}

        if only_collectibles:
            filter_dict["onlyCollectibles"] = only_collectibles
            if assets == None: assets = True

        if assets == True:
            filter_dict["inventoryItemAssetTypes"] = "*"
        elif type(assets) == list and isinstance(assets[0], InventoryAssetType):
            filter_dict["inventoryItemAssetTypes"] = ",".join([list(asset_type_strings.keys())[list(asset_type_strings.values()).index(asset_type)] for asset_type in assets])
        elif type(assets) == list:
            filter_dict["assetIds"] = ",".join([str(asset) for asset in assets])

        if badges == True:
            filter_dict["badges"] = "true"
        elif type(badges) == list:
            filter_dict["badgeIds"] = ",".join([str(badge) for badge in badges])
            
        if game_passes == True:
            filter_dict["gamePasses"] = "true"
        elif type(badges) == list:
            filter_dict["gamePassIds"] = ",".join([str(game_pass) for game_pass in game_passes])
            
        if private_servers == True:
            filter_dict["privateServers"] = "true"
        elif type(badges) == list:
            filter_dict["privateServerIds"] = ",".join([str(private_server) for private_server in private_servers])

        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/cloud/v2/users/{self.id}/inventory-items",
                headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent}, params={
                "maxPageSize": limit if limit and limit <= 100 else 100,
                "filter": ";".join([f"{k}={v}" for k, v in filter_dict.items()]),
                "pageToken": nextcursor if nextcursor else None
            })

            if response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
            elif response.status_code == 401: raise InvalidKey(response.text)
            elif response.status_code == 403: raise PermissionDenied(response.json()["message"])
            elif response.status_code == 404: raise NotFound(response.json()["message"])
            elif response.status_code == 429: raise RateLimited("You're being rate limited!")
            elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
            
            data = response.json()
            for item in data["inventoryItems"]:
                yields += 1
                if "assetDetails" in item.keys():
                    yield InventoryAsset(item["assetDetails"])
                elif "badgeDetails" in item.keys():
                    yield InventoryBadge(item["badgeDetails"])
                elif "gamePassDetails" in item.keys():
                    yield InventoryGamePass(item["gamePassDetails"])
                elif "privateServerDetails" in item.keys():
                    yield InventoryPrivateServer(item["privateServerDetails"])
                if limit != None and yields >= limit: break
            nextcursor = data.get("nextPageToken")
            if not nextcursor: break
