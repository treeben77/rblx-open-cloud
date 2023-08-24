from .exceptions import rblx_opencloudException, InvalidKey, PermissionDenied, NotFound, RateLimited, ServiceUnavailable
from .creator import Creator
import datetime
from typing import Optional, Union, Iterable
from enum import Enum
import requests
from . import user_agent

__all__ = (
    "User",
    "InventoryAssetType",
    "InventoryItem",
    "InventoryAsset",
    "InventoryBadge",
    "InventoryGamePass",
    "InventoryPrivateServer"
)

class InventoryAssetType(Enum):
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

class InventoryItem():
    def __init__(self, id) -> None:
        self.id: int = id

    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryItem(id={self.id}"

class InventoryAsset(InventoryItem):
    def __init__(self, data) -> None:
        super().__init__(data["assetId"])
        self.type: InventoryAssetType = InventoryAssetType(asset_type_strings.get(data["inventoryItemAssetType"], InventoryAssetType.Unknown))
        self.instance_id: int = data["instanceId"]
        self.collectable_item_id: Optional[str] = data.get("collectibleDetails", {}).get("itemId", None)
        self.collectable_instance_id: Optional[str] = data.get("collectibleDetails", {}).get("instanceId", None)
        self.serial_number: Optional[int] = data.get("serialNumber", None)

    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryAsset(id={self.id}, type={self.type})"

class InventoryBadge(InventoryItem):
    def __init__(self, data) -> None:
        super().__init__(data["badgeId"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryBadge(id={self.id})"

class InventoryGamePass(InventoryItem):
    def __init__(self, data) -> None:
        super().__init__(data["gamePassId"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryGamePass(id={self.id})"

class InventoryPrivateServer(InventoryItem):
    def __init__(self, data) -> None:
        super().__init__(data["privateServerId"])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.InventoryPrivateServer(id={self.id})"

class User(Creator):
    """
    Represents a user on Roblox. It is used to provide information about a user in OAuth2, and to upload assets to a user.
    ### Paramaters
    id: int - The user's ID.
    api_key: str - Your API key created from [Creator Dashboard](https://create.roblox.com/credentials) with access to this user.
    """
    def __init__(self, id: int, api_key: str) -> None:
        self.username: Optional[str] = None
        self.id: int = id
        self.display_name: Optional[str] = None
        self.profile_uri: str = f"https://roblox.com/users/{self.id}/profile"
        self.created_at: Optional[datetime.datetime] = None

        self.__api_key = api_key

        super().__init__(id, api_key, "User")
    
    def __repr__(self) -> str:
        return f"rblxopencloud.User({self.id})"

    def list_inventory(self, limit: Optional[int]=None, only_collectibles: Optional[bool]=False, assets: Optional[Union[list[InventoryAssetType], list[int], bool]]=False, badges: Optional[Union[list[int], bool]]=False, game_passes: Optional[Union[list[int], bool]]=False, private_servers: Optional[Union[list[int], bool]]=False) -> Iterable[Union[InventoryAsset, InventoryBadge, InventoryGamePass, InventoryPrivateServer]]:
        """
        Interates `rblx-open-cloud.InventoryItem` for items in the user's inventory. If `only_collectibles`, `assets`, `badges`, `game_passes`, and `private_servers` are `False`, then all inventory items are returned.
        
        The example below would iterate through every item in the user's inventory.
        
        ```py
            for item in user.list_inventory():
                print(item)
        ```
        
        The `user.inventory-item:read` scope is required if authorized via OAuth2`.
        ### Parameters
        limit: Optional[bool] - he maximum number of inventory items to iterate. This can be `None` to return all items.
        only_collectibles: Optional[bool] - Wether the only inventory assets iterated are collectibles (limited items).
        assets: Optional[Union[list[InventoryAssetType], list[int], bool]] - If this is `True`, then it will return all assets, if it is a list of IDs, it will only return assets with the provided IDs, and if it is a list of :class:`rblx-open-cloud.InventoryAssetType` then it will only return assets of these types.
        badges: Optional[Union[list[int], bool]] - If this is `True`, then it will return all badges, but if it is a list of IDs, it will only return badges with the provided IDs.
        game_passes: Optional[Union[list[int], bool]] - If this is `True`, then it will return all game passes, but if it is a list of IDs, it will only return game passes with the provided IDs.
        private_servers: Optional[Union[list[int], bool]] - If this is `True`, then it will return all private servers, but if it is a list of IDs, it will only return private servers with the provided IDs.
        """

        filter_dict = {}

        if only_collectibles:
            filter_dict["onlyCollectibles"] = only_collectibles

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
            response = requests.get(f"https://apis.roblox.com/cloud/v2/users/{self.id}/inventory-items",
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
