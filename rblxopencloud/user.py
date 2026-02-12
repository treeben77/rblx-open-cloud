# MIT License

# Copyright (c) 2022-2026 treeben77

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
from collections.abc import Iterable
from enum import Enum
from typing import TYPE_CHECKING, Literal, Optional, Union, cast

from dateutil import parser

from .creator import Creator, ASSET_TYPE_ENUMS, AssetType
from .http import Operation, iterate_request, send_request

if TYPE_CHECKING:
    from .group import GroupMember, Group

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
    "AssetQuota",
    "AssetQuotaType",
    "AssetQuotaPeriod",
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

ASSET_TYPE_STRINGS_REVERSE = {v: k for k, v in ASSET_TYPE_STRINGS.items()}


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
        added_at (Optional[datetime]): The time the item was added to the \
        inventory. Currently not present for game passes.
    """

    def __init__(self, id, timestamp) -> None:
        self.id: int = id
        self.added_at: Optional[datetime.datetime] = (
            parser.parse(timestamp) if timestamp else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryItem id={self.id}>"


class InventoryAsset(InventoryItem):
    """
    Represents an asset in a user's inventory such as clothing and \
    development items.

    Attributes:
        id (int): The ID of the asset.
        added_at (Optional[datetime]): The time the asset was added to the \
        inventory.
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

    def __init__(self, data: dict, add_time: Optional[str]) -> None:
        super().__init__(data["assetId"], add_time)
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
        added_at (Optional[datetime]): The time the badge was awarded.
    """

    def __init__(self, data, add_time: Optional[str]) -> None:
        super().__init__(data["badgeId"], add_time)

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryBadge id={self.id}>"


class InventoryGamePass(InventoryItem):
    """
    Represents a game pass in a user's inventory.

    Attributes:
        id (int): The ID of the game pass.
    """

    def __init__(self, data, add_time: Optional[str]) -> None:
        super().__init__(data["gamePassId"], add_time)

    def __repr__(self) -> str:
        return f"<rblxopencloud.InventoryGamePass id={self.id}>"


class InventoryPrivateServer(InventoryItem):
    """
    Represents a game pass in a user's inventory.

    Attributes:
        id (int): The ID of the private server.
        added_at (Optional[datetime]): The time the private server was \
        purchased.
    """

    def __init__(self, data, add_time: Optional[str]) -> None:
        super().__init__(data["privateServerId"], add_time)

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


class AssetQuotaType(Enum):
    """
    Enum denoting the type of an asset quota.

    Attributes:
        Unknown (0): An unknown, unspecified, or unspecified quota type.
        Upload (1): The quota is a ratelimit for uploading assets.
        CreatorStoreDistribution (2): The quota is a ratelimit for \
        distributing assets on the creator store.
    """

    Unknown = 0
    Upload = 1
    CreatorStoreDistribution = 2


ASSET_QUOTA_TYPE_ENUMS = {
    "ASSET_QUOTA_TYPE_UNSPECIFIED": AssetQuotaType.Unknown,
    "RATE_LIMIT_UPLOAD": AssetQuotaType.Upload,
    "RATE_LIMIT_CREATOR_STORE_DISTRIBUTE": AssetQuotaType.CreatorStoreDistribution,
}

QUOTA_TYPE_STRINGS = {
    AssetQuotaType.Unknown: "ASSET_QUOTA_TYPE_UNSPECIFIED",
    AssetQuotaType.Upload: "RateLimitUpload",
    AssetQuotaType.CreatorStoreDistribution: "RateLimitCreatorStoreDistribute",
}


class AssetQuotaPeriod(Enum):
    """
    Enum denoting the period of an asset quota.

    Attributes:
        Unknown (0): An unknown, unspecified, or unspecified quota period.
        Day (1): The quota resets daily.
        Month (2): The quota resets monthly.
    """

    Unknown = 0
    Day = 1
    Month = 2


ASSET_QUOTA_PERIOD_ENUMS = {
    "PERIOD_UNSPECIFIED": AssetQuotaPeriod.Unknown,
    "DAY": AssetQuotaPeriod.Day,
    "MONTH": AssetQuotaPeriod.Month,
}


class AssetQuota:
    """
    Represents the quota of an asset type for a user indicating how many \
    assets can be uploaded or distributed on the creator store.

    Attributes:
        asset_type (AssetType): The type of asset this quota applies to.
        quota_type (AssetQuotaType): Whether the quota is for uploading or \
        distributing on the creator store.
        capacity (int): The maximum number of assets that can be uploaded or \
        distributed on the creator store in the given period.
        usage (int): The number of assets that have been uploaded or \
        distributed on the creator store in the given period.
        remaining (int): The number of assets that can still be uploaded or \
        distributed on the creator store in the given period. This is \
        equivalent to `capacity - usage`.
        period (AssetQuotaPeriod): The period for which this quota applies.
        resets_at (Optional[datetime]): The time at which this quota will \
        reset. This may be `None` if none of the limit has been used yet.
    """

    def __init__(self, data, user, api_key):
        self.__api_key = api_key

        self.asset_type: AssetType = ASSET_TYPE_ENUMS.get(
            data.get("assetType"), AssetType.Unknown
        )
        self.quota_type: AssetQuotaType = ASSET_QUOTA_TYPE_ENUMS.get(
            data.get("quotaType"), AssetQuotaType.Unknown
        )
        self.capacity: int = int(data.get("capacity", 0))
        self.usage: int = int(data.get("usage", 0))
        self.remaining: int = self.capacity - self.usage
        self.period: AssetQuotaPeriod = ASSET_QUOTA_PERIOD_ENUMS.get(
            data.get("period"), AssetQuotaPeriod.Unknown
        )
        self.resets_at: Optional[datetime.datetime] = (
            parser.parse(data["usageResetAt"])
            if data.get("usageResetAt")
            else None
        )

    def __repr__(self) -> str:
        return (
            f"<rblxopencloud.AssetQuota asset_type={self.asset_type} \
quota_type={self.quota_type} remaining={self.remaining} period={self.period}"
            + (f" resets_at={self.resets_at}>" if self.resets_at else ">")
        )


class User(Creator):
    """
    Represents a user on Roblox. It is used to provide information about a \
    user in OAuth2, and to upload assets to a user.
    
    Args:
        id (int): The user's ID.
        api_key (str): Your API key created from \
        [Creator Dashboard](https://create.roblox.com/credentials) with \
        access to this user.

    Attributes:
        id (int): The user's ID.
        username (Optional[str]): The user's username
        name (Optional[str]): An alias for `username`.
        display_name (Optional[str]): The non-unqiue display name for the user.
        profile_uri (Optional[str]): A URI to the user's rendered profile.
        headshot_uri (Optional[str]): For [`AccessToken`][rblxopencloud.AccessToken],\
            a URI to the user's Roblox avatar profile picture. For other \
            purposes, see [`generate_headshot`][rblxopencloud.User.generate_headshot].
        created_at (Optional[datetime.datetime]): The timestamp the user's \
        account was created at.
        about (Optional[str]): The user's about me description.
        locale (Optional[str]): The user's currently selected IETF language \
            code.
        premium (Optional[bool]): Whether the user has Roblox premium.
        id_verified (Optional[bool]): Whether the user has verified a \
            non-VOIP phone number or governement ID. Requires the scope \
            `user.advanced:read`.
        social_links (Optional[UserSocialLinks]): The user's social links. \
            Requires the scope `user.social:read`.
        verified (Optional[bool]): Whether the user has a verified badge. \
            This is not populated by `fetch_info()`, but is populated for \
            users returned by the group audit logs and toolbox endpoints.
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
        self.verified: Optional[bool] = None

        self.__api_key = api_key

        super().__init__(id, api_key, "User")

    @property
    def name(self) -> Optional[str]:
        return self.username

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

    def fetch_managing_groups(self) -> list["Group"]:
        """
        Fetches the groups that the authenticated user can manage.
        
        Requires `legacy-group:manage` on an API Key or OAuth2 authorization.

        Returns:
            A list of groups that the authenticated user can manage with \
            `name` and `id` resolved.

        !!! bug "Legacy API"
            This endpoint uses the legacy Develop API. Roblox has noted [in \
this DevForum post](https://devforum.roblox.com/t/3106190) that these \
endpoints may change without notice and break your application. Therefore, \
they should be used with caution.

            Please report issues with this endpoint on the [GitHub issue \
tracker](https://github.com/treeben77/rblx-open-cloud/issues) or the [Discord \
server](https://discord.gg/zW36pJGFnh).

        !!! Warning
            Irrespective of requested user, this will always return the groups \
            that the authenticated user can manage (e.g. \
        [`ApiKey.authorized_user`][rblxopencloud.ApiKey]).

        """

        from .group import Group

        _, data, _ = send_request(
            "GET",
            f"legacy-develop/v1/user/groups/canmanage",
            authorization=self.__api_key,
            expected_status=[200],
        )

        groups = []

        for data in data.get("data", []):
            group = Group(data["id"], self.__api_key)
            group.name = data.get("name")
            groups.append(group)

        return groups

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
        limit: Optional[int] = None,
        only_collectibles: bool = False,
        assets: Optional[
            Union[list[InventoryAssetType], list[int], bool]
        ] = None,
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
        Iterates [`InventoryItem`][rblxopencloud.InventoryItem] for items in \
        the user's inventory. If `only_collectibles`, `assets`, `badges`, \
        `game_passes`, and `private_servers` are `False`, then all inventory \
        items are returned.

        Args:
            limit (Optional[int]): The maximum number of inventory items to iterate. \
            This can be `None` to return all items.
            only_collectibles (bool): Whether the only inventory assets \
            returned are collectibles (limited items).
            assets (Optional[Union[list[InventoryAssetType], list[int], bool]]): If \
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
        elif (
            isinstance(assets, list) and assets
        ):  # Do nothing if the list is empty
            filter_by_type = all(
                isinstance(asset, InventoryAssetType) for asset in assets
            )
            filter_by_id = all(isinstance(asset, int) for asset in assets)

            if not filter_by_type and not filter_by_id:
                raise ValueError(
                    (
                        "'assets' must be either a list of InventoryAssetType objects, a list of integers, a boolean, or None. "
                        "You cannot mix InventoryAssetType objects and integers."
                    )
                )

            if filter_by_type:
                asset_types: list[str] = []
                # this is validated by the above code, but the typechecker doesn't know that, so we cast
                assets = cast(list[InventoryAssetType], assets)
                for asset_type in assets:
                    asset_types.append(ASSET_TYPE_STRINGS_REVERSE[asset_type])
                filter["inventoryItemAssetTypes"] = ",".join(asset_types)
            elif filter_by_id:
                # this is validated by the above code, but the typechecker doesn't know that, so we cast
                assets = cast(list[int], assets)
                filter["assetIds"] = ",".join([str(id) for id in assets])

        if badges is True:
            filter["badges"] = "true"
        elif isinstance(badges, list):
            filter["badgeIds"] = ",".join([str(id) for id in badges])

        if game_passes is True:
            filter["gamePasses"] = "true"
        elif isinstance(game_passes, list):
            filter["gamePassIds"] = ",".join([str(id) for id in game_passes])

        if private_servers is True:
            filter["privateServers"] = "true"
        elif isinstance(private_servers, list):
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
            max_yields=limit,
        ):
            if "assetDetails" in entry.keys():
                yield InventoryAsset(
                    entry["assetDetails"], entry.get("addTime")
                )
            elif "badgeDetails" in entry.keys():
                yield InventoryBadge(
                    entry["badgeDetails"], entry.get("addTime")
                )
            elif "gamePassDetails" in entry.keys():
                yield InventoryGamePass(
                    entry["gamePassDetails"], entry.get("addTime")
                )
            elif "privateServerDetails" in entry.keys():
                yield InventoryPrivateServer(
                    entry["privateServerDetails"], entry.get("addTime")
                )

    def fetch_experience_followings(self) -> list["UserExperienceFollowing"]:
        """
        Fetches the list of experiences the user is following.

        Requires `legacy-universe.following:read` on an API Key or OAuth2 \
        authorization. The requested user must be the authenticated user \
        to fetch this information.

        ??? example
            Fetches the experiences the user is following and finds the \
            oldest one. The year they followed it is then printed along with \
            the experience name.
            ```python
            followings = user.fetch_experience_followings()
            for following in followings:
                if not oldest_follow or following.followed_at < oldest_follow.followed_at:
                    oldest_follow = following

            oldest_follow.experience.fetch_info()
            print(f"The user's oldest experience follow is {oldest_follow.experience.name} since {oldest_follow.followed_at.year}")
            >>> "The user's oldest experience follow is Natural Disaster Survival since 2018"
            ```
        
        Returns:
            A list of experiences the user is following, and the time they \
            followed at. `can_follow`, `following_count`, and \
            `following_limit` will all be `None`.

        !!! bug "Legacy API"
            This endpoint uses the legacy Followings API. Roblox has noted [in \
this DevForum post](https://devforum.roblox.com/t/3106190) that these \
endpoints may change without notice and break your application. Therefore, \
they should be used with caution.

            Please report issues with this endpoint on the [GitHub issue \
tracker](https://github.com/treeben77/rblx-open-cloud/issues) or the [Discord \
server](https://discord.gg/zW36pJGFnh).
        """

        _, data, _ = send_request(
            "GET",
            f"legacy-followings/v2/users/{self.id}/universes",
            authorization=self.__api_key,
            expected_status=[200],
        )

        followings = []

        for k, v in data["followedSources"].items():
            followings.append(
                UserExperienceFollowing(self.__api_key, k, v, None)
            )

        return followings

    def fetch_experience_following_status(
        self, experience_id: int
    ) -> UserExperienceFollowing:
        """
        Fetches the following status of the requested experience for the user.

        Requires `legacy-universe.following:read` on an API Key or OAuth2 \
        authorization. The requested user must be the authenticated user \
        to fetch this information.

        Args:
            experience_id: The ID of the experience to fetch status for; not \
            to be confused with a place ID.
        
        Returns:
           The following status object with `followed_at` being `None`.

        !!! bug "Legacy API"
            This endpoint uses the legacy Followings API. Roblox has noted [in \
this DevForum post](https://devforum.roblox.com/t/3106190) that these \
endpoints may change without notice and break your application. Therefore, \
they should be used with caution.

            Please report issues with this endpoint on the [GitHub issue \
tracker](https://github.com/treeben77/rblx-open-cloud/issues) or the [Discord \
server](https://discord.gg/zW36pJGFnh).
        """

        _, data, _ = send_request(
            "GET",
            f"legacy-followings/v1/users/{self.id}/universes/\
{experience_id}/status",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return UserExperienceFollowing(
            self.__api_key, experience_id, None, data
        )

    def follow_experience(self, experience_id: int):
        """
        Follows the requested experience for the user. This means the user \
        will recieve updates and notifications for the experience.

        Requires `legacy-universe.following:write` on an API Key or OAuth2 \
        authorization. The requested user must be the authenticated user \
        to use this endpoint.

        Args:
            experience_id: The ID of the experience to follow; not to be \
            confused with a place ID.

        !!! bug "Legacy API"
            This endpoint uses the legacy Followings API. Roblox has noted [in \
this DevForum post](https://devforum.roblox.com/t/3106190) that these \
endpoints may change without notice and break your application. Therefore, \
they should be used with caution.

            Please report issues with this endpoint on the [GitHub issue \
tracker](https://github.com/treeben77/rblx-open-cloud/issues) or the [Discord \
server](https://discord.gg/zW36pJGFnh).
        """

        send_request(
            "POST",
            f"legacy-followings/v1/users/{self.id}/universes/\
{experience_id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

    def unfollow_experience(self, experience_id: int):
        """
        Unfollows the requested experience for the user. This means the user \
        will no longer recieve updates and notifications for the experience.

        Requires `legacy-universe.following:write` on an API Key or OAuth2 \
        authorization. The requested user must be the authenticated user \
        to use this endpoint.

        Args:
            experience_id: The ID of the experience to unfollow; not to be \
            confused with a place ID.

        !!! bug "Legacy API"
            This endpoint uses the legacy Followings API. Roblox has noted [in \
this DevForum post](https://devforum.roblox.com/t/3106190) that these \
endpoints may change without notice and break your application. Therefore, \
they should be used with caution.

            Please report issues with this endpoint on the [GitHub issue \
tracker](https://github.com/treeben77/rblx-open-cloud/issues) or the [Discord \
server](https://discord.gg/zW36pJGFnh).
        """

        send_request(
            "DELETE",
            f"legacy-followings/v1/users/{self.id}/universes/\
{experience_id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

    def list_asset_quotas(
        self,
        limit: Optional[int] = None,
        quota_type: Optional[AssetQuotaType] = None,
        asset_type: Optional[AssetType] = None,
    ) -> Iterable[AssetQuota]:
        """
        Iterates the user's asset quotas, indicating how many assets can be \
        uploaded or distributed on the creator store for each type over a \
        given time period.

        Requires `assets:read` on an API Key or OAuth2 authorization.

        ??? example
            Fetches the asset quota for uploading audio assets. It uses a \
            limit of 1 since there should only be one quota for this type. \
            Due to the API, however, it is still returned as an iterable so \
            it is condensed into a list and the first item is accessed to get \
            the quota information.
            ```python
            quotas = list(
                user.list_asset_quotas(
                    quota_type=AssetQuotaType.Upload,
                    asset_type=AssetType.Audio,
                    limit=1,
                )
            )

            if quotas and quotas[0].remaining > 0:
                print("You can upload more audio assets!")
            elif quotas and quotas[0].resets_at:
                print(f"You cannot upload more audio assets until {quotas[0].resets_at}.")
            ```

        Args:
            limit (Optional[int]): The maximum number of asset quotas to \
            iterate. This can be `None` to return all asset quotas.
        
        Yields:
            Asset quota information for each type of asset.
        """

        filter = {}

        if asset_type:
            filter["assetType"] = asset_type.name

        if quota_type:
            filter["quotaType"] = QUOTA_TYPE_STRINGS.get(quota_type)

        for entry in iterate_request(
            "GET",
            f"/users/{self.id}/asset-quotas",
            params={
                "maxPageSize": limit if limit and limit <= 100 else 100,
                "filter": " && ".join(
                    [f"{k} == {v}" for k, v in filter.items()]
                ),
            },
            authorization=self.__api_key,
            data_key="assetQuotas",
            cursor_key="pageToken",
            expected_status=[200],
            max_yields=limit,
        ):
            yield AssetQuota(entry, self, self.__api_key)
