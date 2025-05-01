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

import datetime
from enum import Enum
from typing import TYPE_CHECKING, Iterable, Literal, Optional, Union

from dateutil import parser

from .creator import Creator
from .http import Operation, iterate_request, send_request

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
    "InventoryPrivateServer",
    "UserSocialLinks",
    "UserVisibility",
    "UserExperienceFollowing",
)


class InventoryAssetType(Enum):
    """
    Enum representing the type of an \
    [InventoryAsset][rblxopencloud.InventoryAsset].
    
    Attributes:
        Unknown(0): The asset type is unknown/unsupported.
        ClassicTShirt(1): 
        Audio(2): 
        Hat(3): 
        Model(4): 
        ClassicShirt(5): 
        ClassicPants(6): 
        Decal(7): 
        ClassicHead(8): 
        Face(9): 
        Gear(10): 
        Animation(11): 
        Torso(12): 
        RightArm(13): 
        LeftArm(14): 
        LeftLeg(15): 
        RightLeg(16): 
        Package(17): 
        Plugin(18): 
        MeshPart(19): 
        HairAccessory(20): 
        FaceAccessory(21): 
        NeckAccessory(22): 
        ShoulderAccessory(23): 
        FrontAccessory(24): 
        BackAccessory(25): 
        WaistAccessory(26): 
        ClimbAnimation(27): 
        DeathAnimation(28): 
        FallAnimation(29): 
        IdleAnimation(30): 
        JumpAnimation(31): 
        RunAnimation(32): 
        SwimAnimation(33): 
        WalkAnimation(34): 
        PoseAnimation(35): 
        EmoteAnimation(36): 
        Video(37): 
        TShirtAccessory(38): 
        ShirtAccessory(39): 
        PantsAccessory(40): 
        JacketAccessory(41): 
        SweaterAccessory(42): 
        ShortsAccessory(43): 
        LeftShoeAccessory(44): 
        RightShoeAccessory(45): 
        DressSkirtAccessory(46): 
        EyebrowAccessory(47): 
        EyelashAccessory(48): 
        MoodAnimation(49): 
        DynamicHead(50): 
        CreatedPlace(51): 
        PurchasedPlace(52): 
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


ASSET_TYPE_STRINGS = {
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
    "PURCHASED_PLACE": InventoryAssetType.PurchasedPlace,
}


class InventoryItemState(Enum):
    """
    Enum representing whether a collectable \
    [InventoryAsset][rblxopencloud.InventoryAsset] can be traded/ sold or is \
    currently on hold.
    
    Attributes:
        Unknown (0): The status is unknown.
        Available (1): The collectable can be traded and sold.
        Hold (2): The collectable cannot be traded or sold yet.
    """

    Unknown = 0
    Available = 1
    Hold = 2


STATE_TYPE_STRINGS = {
    "COLLECTIBLE_ITEM_INSTANCE_STATE_UNSPECIFIED": InventoryItemState.Unknown,
    "AVAILABLE": InventoryItemState.Available,
    "HOLD": InventoryItemState.Hold,
}


class InventoryItem:
    """
    Represents an asset, badge, or gamepass in the user's inventory.

    Attributes:
        id (int): The ID of the inventory item.
    """

    def __init__(self, id) -> None:
        self.id: int = id

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryItem id={self.id}>"


class InventoryAsset(InventoryItem):
    """
    Represents an asset in a user's inventory such as clothing and \
    development items.

    Attributes:
        id (int): The ID of the asset.
        type (InventoryAssetType): The asset's type.
        instance_id (int): The unique ID of this asset's instance.
        collectable_item_id (Optional[str]): A unique item UUID for \
        collectables.
        collectable_instance_id (Optional[str]): A unique instance UUID for \
        collectables.
        serial_number (Optional[int]): The serial number of the collectable.
        collectable_state (Optional[InventoryItemState]): Wether the item is \
        ready for sale or in hold.
    """

    def __init__(self, data: dict) -> None:
        super().__init__(data["assetId"])
        self.type: InventoryAssetType = InventoryAssetType(
            ASSET_TYPE_STRINGS.get(
                data["inventoryItemAssetType"], InventoryAssetType.Unknown
            )
        )
        self.instance_id: int = data["instanceId"]
        self.collectable_item_id: Optional[str] = data.get(
            "collectibleDetails", {}
        ).get("itemId", None)
        self.collectable_instance_id: Optional[str] = data.get(
            "collectibleDetails", {}
        ).get("instanceId", None)
        self.serial_number: Optional[int] = data.get(
            "collectibleDetails", {}
        ).get("serialNumber", None)

        collectable_state = data.get("collectibleDetails", {}).get(
            "instanceState", None
        )
        self.collectable_state: Optional[InventoryItemState] = (
            InventoryItemState(
                STATE_TYPE_STRINGS.get(
                    collectable_state, InventoryItemState.Unknown
                )
            )
            if collectable_state
            else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryAsset id={self.id} type={self.type}>"


class InventoryBadge(InventoryItem):
    """
    Represents a badge in a user's inventory.

    Attributes:
        id (int): The ID of the badge.
    """

    def __init__(self, data) -> None:
        super().__init__(data["badgeId"])

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryBadge id={self.id}>"


class InventoryGamePass(InventoryItem):
    """
    Represents a game pass in a user's inventory.

    Attributes:
        id (int): The ID of the game pass.
    """

    def __init__(self, data) -> None:
        super().__init__(data["gamePassId"])

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryGamePass id={self.id}>"


class InventoryPrivateServer(InventoryItem):
    """
    Represents a game pass in a user's inventory.

    Attributes:
        id (int): The ID of the private server.
    """

    def __init__(self, data) -> None:
        super().__init__(data["privateServerId"])

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryPrivateServer id={self.id}>"


class UserVisibility(Enum):
    """
    Enum denoting what visibility a resource has. Currently only applies to \
    social links.

    Attributes:
        Unknown (0): The visiblity type is unknown
        Noone (1): It is visible to no one.
        Friends (2): It is visible to only the user's friends.
        Following (3): It is visible to the user's friends and users they \
        follow.
        Followers (4): It is visible to the user's friends, users they \
        follow, and users that follow them.
        Everyone (5): It is visible to everyone.
    """

    Unknown = 0
    Noone = 1
    Friends = 2
    Following = 3
    Followers = 4
    Everyone = 5


user_visiblity_strings = {
    "NO_ONE": UserVisibility.Noone,
    "FRIENDS": UserVisibility.Friends,
    "FRIENDS_AND_FOLLOWING": UserVisibility.Following,
    "FRIENDS_FOLLOWING_AND_FOLLOWERS": UserVisibility.Followers,
    "EVERYONE": UserVisibility.Everyone,
}


class UserSocialLinks:
    """
    Data class storing information about a user's social links.

    Attributes:
        facebook_uri (str): Facebook profile URI, empty string if not provided.
        guilded_uri (str): Guilded profile URI, empty string if not provided.
        twitch_uri (str): Twitch profile URI, empty string if not provided.
        twitter_uri (str): Twitter profile URI, empty string if not provided.
        youtube_uri (str): YouTube profile URI, empty string if not provided.
        visibility (UserVisibility): The visiblity of these social links to \
        user's on the platform.
    """

    def __repr__(self) -> str:
        social_links_params = [
            "facebook_uri",
            "guilded_uri",
            "twitch_uri",
            "twitter_uri",
            "youtube_uri",
        ]
        social_links = []

        for param in social_links_params:
            if self.__getattribute__(param):
                social_links.append(
                    f'{param}="{self.__getattribute__(param)}"'
                )

        return f"<rblxopencloud.UserSocialLinks {' '.join(social_links)}\
{' ' if social_links else ''}visibility={self.visibility}>"

    def __init__(self, data):
        self.facebook_uri: str = data.get("facebook", "")
        self.guilded_uri: str = data.get("guilded", "")
        self.twitch_uri: str = data.get("twitch", "")
        self.twitter_uri: str = data.get("twitter", "")
        self.youtube_uri: str = data.get("youtube", "")
        self.visibility: UserVisibility = user_visiblity_strings.get(
            data.get("visibility", ""), UserVisibility.Unknown
        )


class UserExperienceFollowing:
    """
    Data class storing information about an experience followed by a user.

    Attributes:
        is_following (bool): Whether the experience is followed.
        experience (Experience): The experience that has been followed.
        followed_at (Optional[datetime]): The time that the user followed the \
        experience. Only present for when returned by \
        [`fetch_experience_followings()`\
        ][rblxopencloud.User.fetch_experience_followings]
        can_follow (Optional[bool]): Whether the user can follow this \
        experience. Only present for when returned by \
        [`fetch_experience_following_status()`\
        ][rblxopencloud.User.fetch_experience_following_status]
        following_count (Optional[int]): The number of experiences the user \
        is following [`fetch_experience_following_status()`\
        ][rblxopencloud.User.fetch_experience_following_status]
        following_limit (Optional[int]): The maximum number of experiences \
        the user can follow. Only present for when returned by \
        [`fetch_experience_following_status()`\
        ][rblxopencloud.User.fetch_experience_following_status]

    """

    def __init__(self, api_key, universe_id, timestamp, status_payload):
        from .experience import Experience

        self.experience: Experience = Experience(int(universe_id), api_key)
        self.followed_at: Optional[datetime.datetime] = (
            parser.parse(timestamp) if timestamp else None
        )
        self.is_following: bool = (
            True if not status_payload else status_payload["IsFollowing"]
        )
        self.can_follow: Optional[bool] = (
            True if not status_payload else status_payload["CanFollow"]
        )
        self.following_count: Optional[int] = (
            None
            if not status_payload
            else status_payload["FollowingCountByType"]
        )
        self.following_limit: Optional[int] = (
            None
            if not status_payload
            else status_payload["FollowingLimitByType"]
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.UserExperienceFollowing \
experience={self.experience}>"


class User(Creator):
    """
    Represents a user on Roblox. It is used to provide information about a \
    user in OAuth2, and to upload assets to a user.
    
    Attributes:
        id (int): The user's ID.
        api_key (str): Your API key created from \
        [Creator Dashboard](https://create.roblox.com/credentials) with \
        access to this user.
    """

    def __init__(self, id: int, api_key: str) -> None:
        self.username: Optional[str] = None
        self.id: int = id
        self.display_name: Optional[str] = None
        self.profile_uri: str = f"https://roblox.com/users/{self.id}/profile"
        self.headshot_uri: Optional[str] = None
        self.created_at: Optional[datetime.datetime] = None
        self.about: Optional[str] = None
        self.locale: Optional[str] = None
        self.premium: Optional[bool] = None
        self.id_verified: Optional[bool] = None
        self.social_links: Optional[UserSocialLinks] = None

        self.__api_key = api_key

        super().__init__(id, api_key, "User")

    def __repr__(self) -> str:
        return f"<rblxopencloud.User id={self.id}>"

    def fetch_info(self) -> "User":
        """
        Updates the empty attributes in the class with the user info.

        Returns:
            The class itself.
        """

        _, data, _ = send_request(
            "GET",
            f"/users/{self.id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        self.username = data["name"]
        self.display_name = data["displayName"]
        self.created_at = parser.parse(data["createTime"])
        self.about = data.get("about")
        self.locale = data["locale"]
        self.premium = data.get("premium")
        self.id_verified = data.get("idVerified")
        self.social_links = (
            UserSocialLinks(data["socialNetworkProfiles"])
            if data.get("socialNetworkProfiles")
            else None
        )

        return self

    def generate_headshot(
        self,
        size: Literal[48, 50, 60, 75, 100, 110, 150, 180, 352, 420, 720] = 420,
        format: Literal["png", "jpeg"] = "png",
        is_circular: bool = False,
    ) -> Operation[str]:
        """
        Fetches the user's thumbnail from Roblox and returns an \
        [`Operation`][rblxopencloud.Operation].

        Args:
            size (Literal[48, 50, 60, 75, 100, 110, 150, 180, 352, 420, \
            720]): The size in pixels of the generated headshot. Must be one \
            of: `48`, `50`, `60`, `75`, `100`, `110`, `150`, `180`, `352`, \
            `420` or `720`.
            format (Literal["png", "jpeg"]): The file format of the generated \
            image.
            is_circular (bool): Wether the generated thumbnail has a circular \
            cut out.

        Returns:
            The [`Operation`][rblxopencloud.Operation] to get the thumbnail. \
            In most cases, the final result will be cached and \
            returned immediately from \
            [`Operation.wait`][rblxopencloud.Operation.wait].
        """

        _, data, _ = send_request(
            "GET",
            f"/users/{self.id}:generateThumbnail",
            params={
                "shape": "SQUARE" if not is_circular else None,
                "size": size,
                "format": format.upper(),
            },
            authorization=self.__api_key,
            expected_status=[200],
        )

        return Operation(
            f"/{data['path']}",
            self.__api_key,
            lambda response: response["imageUri"],
            cached_response=data.get("response"),
        )

    def list_groups(self, limit: int = None) -> Iterable["GroupMember"]:
        """
        Iterates a [`GroupMember`][rblxopencloud.GroupMember] for every group \
        the user is in. Use [`GroupMember.group`][rblxopencloud.GroupMember] \
        to get the group.

        Args:
            limit (int): The max number of groups to iterate.

        Yields:
            [`GroupMember`][rblxopencloud.GroupMember] for every group the \
            user is in.
        """

        from .group import GroupMember

        for entry in iterate_request(
            "GET",
            "/groups/-/memberships",
            authorization=self.__api_key,
            params={
                "maxPageSize": limit if limit and limit <= 99 else 99,
                "filter": f"user == 'users/{self.id}'",
            },
            data_key="groupMemberships",
            cursor_key="nextPageToken",
            expected_status=[200],
        ):
            yield GroupMember(entry, self.__api_key)

    def list_inventory(
        self,
        limit: int = None,
        only_collectibles: bool = False,
        assets: Union[list[InventoryAssetType], list[int], bool] = None,
        badges: Union[list[int], bool] = False,
        game_passes: Union[list[int], bool] = False,
        private_servers: Union[list[int], bool] = False,
    ) -> Iterable[
        Union[
            InventoryAsset,
            InventoryBadge,
            InventoryGamePass,
            InventoryPrivateServer,
        ]
    ]:
        """
        Interates [`InventoryItem`][rblxopencloud.InventoryItem] for items in \
        the user's inventory. If `only_collectibles`, `assets`, `badges`, \
        `game_passes`, and `private_servers` are `False`, then all inventory \
        items are returned.
        
        Args:
            limit (bool): The maximum number of inventory items to iterate. \
            This can be `None` to return all items.
            only_collectibles (bool): Wether the only inventory assets \
            returned are collectibles (limited items).
            assets (Union[list[InventoryAssetType], list[int], bool]): If \
            `True`, then it will return all assets, if it is a list of IDs, \
            it will only return assets with the provided IDs, and if it is a \
            list of [`InventoryAssetType`][rblxopencloud.InventoryAssetType] \
            then it will only return assets of these types.
            badges (Union[list[int], bool]): If `True`, then it will return \
            all badges, but if it is a list of IDs, it will only return \
            badges with the provided IDs.
            game_passes (Union[list[int], bool]): If `True`, then it will \
            return all game passes, but if it is a list of IDs, it will only \
            return game passes with the provided IDs.
            private_servers (Union[list[int], bool]): If `True`, then it will \
            return all private servers, but if it is a list of IDs, it will \
            only return private servers with the provided IDs.
        """

        filter = {}

        if only_collectibles:
            filter["onlyCollectibles"] = only_collectibles
            if assets is None:
                assets = True

        if assets is True:
            filter["inventoryItemAssetTypes"] = "*"
        elif type(assets) == list and isinstance(
            assets[0], InventoryAssetType
        ):

            asset_types = []
            for asset_type in assets:
                asset_types.append(
                    list(ASSET_TYPE_STRINGS.keys())[
                        list(ASSET_TYPE_STRINGS.values()).index(asset_type)
                    ]
                )

            filter["inventoryItemAssetTypes"] = ",".join(asset_types)
        elif type(assets) == list:
            filter["assetIds"] = ",".join([str(id) for id in assets])

        if badges is True:
            filter["badges"] = "true"
        elif type(badges) == list:
            filter["badgeIds"] = ",".join([str(id) for id in badges])

        if game_passes is True:
            filter["gamePasses"] = "true"
        elif type(game_passes) == list:
            filter["gamePassIds"] = ",".join([str(id) for id in game_passes])

        if private_servers is True:
            filter["privateServers"] = "true"
        elif type(badges) == list:
            filter["privateServerIds"] = ",".join(
                [str(private_server) for private_server in private_servers]
            )

        for entry in iterate_request(
            "GET",
            f"/users/{self.id}/inventory-items",
            params={
                "maxPageSize": limit if limit and limit <= 100 else 100,
                "filter": ";".join([f"{k}={v}" for k, v in filter.items()]),
            },
            authorization=self.__api_key,
            data_key="inventoryItems",
            cursor_key="pageToken",
            expected_status=[200],
        ):
            if "assetDetails" in entry.keys():
                yield InventoryAsset(entry["assetDetails"])
            elif "badgeDetails" in entry.keys():
                yield InventoryBadge(entry["badgeDetails"])
            elif "gamePassDetails" in entry.keys():
                yield InventoryGamePass(entry["gamePassDetails"])
            elif "privateServerDetails" in entry.keys():
                yield InventoryPrivateServer(entry["privateServerDetails"])
