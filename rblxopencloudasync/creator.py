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

import io
import json
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Union

import urllib3
from dateutil import parser

from .exceptions import (
    Forbidden,
    HttpException,
    InvalidFile,
    ModeratedText,
    NotFound,
)
from .http import Operation, iterate_request, send_request

if TYPE_CHECKING:
    from .experience import Experience
    from .group import Group, GroupRole
    from .user import User

__all__ = (
    "AssetType",
    "ModerationStatus",
    "AssetPrivacy",
    "AssetSocialLink",
    "AssetDeliveryLocation",
    "Asset",
    "AssetVersion",
    "Creator",
    "CreatorStoreProduct",
    "Money",
    "ProductRestriction",
    "AssetPermissionSubjectType",
    "AssetPermissionSubject",
    "AssetPermissionAction",
    "AssetPermissionRequest",
    "AssetPermissionResult",
    "AssetPermissionResultError",
    "ToolboxAssetSubtype",
    "ToolboxAsset",
    "ToolboxSearchSortCategory",
    "InstanceType",
    "MusicChartType",
    "ToolboxSearchContext",
)


class AssetType(Enum):
    """
    Enum denoting an [`Asset`][rblxopencloud.Asset]'s asset type.

    Attributes:
        Unknown (0): The asset type is unknown/unsupported.
        Decal (1):
        Audio (2):
        Model (3):
        Plugin (4): Only for fetching assets; does not support uploading.
        FontFamily (5): Only for fetching assets; does not support uploading.
        MeshPart (6): Only for fetching assets; does not support uploading.
        Video (7): Only for fetching assets; does not support uploading.
        Animation (8): Only for fetching assets; does not support uploading.
        Image (9): Only for fetching assets; does not support uploading.
        Place (10): Only for fetching assets; does not support uploading.
        StorePreviewVideo (11): A special type of video for store preview \
        videos. Only for fetching assets; does not support uploading.
        ClassicTShirt (100): Only for fetching assets; does not support uploading.
        Hat (101): Only for fetching assets; does not support uploading.
        ClassicShirt (102): Only for fetching assets; does not support uploading.
        ClassicPants (103): Only for fetching assets; does not support uploading.
        ClassicHead (104): Only for fetching assets; does not support uploading.
        Face (105): Only for fetching assets; does not support uploading.
        Gear (106): Only for fetching assets; does not support uploading.
        Torso (107): Only for fetching assets; does not support uploading.
        RightArm (108): Only for fetching assets; does not support uploading.
        LeftArm (109): Only for fetching assets; does not support uploading.
        LeftLeg (110): Only for fetching assets; does not support uploading.
        RightLeg (111): Only for fetching assets; does not support uploading.
        Package (112): Only for fetching assets; does not support uploading.
        HairAccessory (113): Only for fetching assets; does not support uploading.
        FaceAccessory (114): Only for fetching assets; does not support uploading.
        NeckAccessory (115): Only for fetching assets; does not support uploading.
        ShoulderAccessory (116): Only for fetching assets; does not support uploading.
        FrontAccessory (117): Only for fetching assets; does not support uploading.
        BackAccessory (118): Only for fetching assets; does not support uploading.
        WaistAccessory (119): Only for fetching assets; does not support uploading.
        ClimbAnimation (120): Only for fetching assets; does not support uploading.
        DeathAnimation (121): Only for fetching assets; does not support uploading.
        FallAnimation (122): Only for fetching assets; does not support uploading.
        IdleAnimation (123): Only for fetching assets; does not support uploading.
        JumpAnimation (124): Only for fetching assets; does not support uploading.
        RunAnimation (125): Only for fetching assets; does not support uploading.
        SwimAnimation (126): Only for fetching assets; does not support uploading.
        WalkAnimation (127): Only for fetching assets; does not support uploading.
        PoseAnimation (128): Only for fetching assets; does not support uploading.
        EmoteAnimation (129): Only for fetching assets; does not support uploading.
        TShirtAccessory (130): Only for fetching assets; does not support uploading.
        ShirtAccessory (131): Only for fetching assets; does not support uploading.
        PantsAccessory (132): Only for fetching assets; does not support uploading.
        JacketAccessory (133): Only for fetching assets; does not support uploading.
        SweaterAccessory (134): Only for fetching assets; does not support uploading.
        ShortsAccessory (135): Only for fetching assets; does not support uploading.
        LeftShoeAccessory (136): Only for fetching assets; does not support uploading.
        RightShoeAccessory (137): Only for fetching assets; does not support uploading.
        DressSkirtAccessory (138): Only for fetching assets; does not support uploading.
        EyebrowAccessory (140): Only for fetching assets; does not support uploading.
        EyelashAccessory (141): Only for fetching assets; does not support uploading.
        MoodAnimation (142): Only for fetching assets; does not support uploading.
        DynamicHead (143): Only for fetching assets; does not support uploading.
    """

    Unknown = 0
    Decal = 1
    Audio = 2
    Model = 3
    Plugin = 4
    FontFamily = 5
    MeshPart = 6
    Video = 7
    Animation = 8
    Image = 9
    Place = 10

    StorePreviewVideo = 11

    ClassicTShirt = 100
    Hat = 101
    ClassicShirt = 102
    ClassicPants = 103
    ClassicHead = 104
    Face = 105
    Gear = 106
    Torso = 107
    RightArm = 108
    LeftArm = 109
    LeftLeg = 110
    RightLeg = 111
    Package = 112
    HairAccessory = 113
    FaceAccessory = 114
    NeckAccessory = 115
    ShoulderAccessory = 116
    FrontAccessory = 117
    BackAccessory = 118
    WaistAccessory = 119
    ClimbAnimation = 120
    DeathAnimation = 121
    FallAnimation = 122
    IdleAnimation = 123
    JumpAnimation = 124
    RunAnimation = 125
    SwimAnimation = 126
    WalkAnimation = 127
    PoseAnimation = 128
    EmoteAnimation = 129
    TShirtAccessory = 130
    ShirtAccessory = 131
    PantsAccessory = 132
    JacketAccessory = 133
    SweaterAccessory = 134
    ShortsAccessory = 135
    LeftShoeAccessory = 136
    RightShoeAccessory = 137
    DressSkirtAccessory = 138
    EyebrowAccessory = 140
    EyelashAccessory = 141
    MoodAnimation = 142
    DynamicHead = 143

    EarAccessory = 144
    EyeAccessory = 145
    FaceMakeup = 146
    LipMakeup = 147
    EyeMakeup = 148

    Lua = 200
    Badge = 201
    GamePass = 202


ASSET_TYPE_ENUMS = {
    "Decal": AssetType.Decal,
    "Audio": AssetType.Audio,
    "Model": AssetType.Model,
    "Plugin": AssetType.Plugin,
    "FontFamily": AssetType.FontFamily,
    "MeshPart": AssetType.MeshPart,
    "Video": AssetType.Video,
    "Animation": AssetType.Animation,
    "Image": AssetType.Image,
    "ASSET_TYPE_DECAL": AssetType.Decal,
    "ASSET_TYPE_AUDIO": AssetType.Audio,
    "ASSET_TYPE_MODEL": AssetType.Model,
    "Place": AssetType.Place,
    "ClassicTShirt": AssetType.ClassicTShirt,
    "Hat": AssetType.Hat,
    "ClassicShirt": AssetType.ClassicShirt,
    "ClassicPants": AssetType.ClassicPants,
    "ClassicHead": AssetType.ClassicHead,
    "Face": AssetType.Face,
    "Gear": AssetType.Gear,
    "Torso": AssetType.Torso,
    "RightArm": AssetType.RightArm,
    "LeftArm": AssetType.LeftArm,
    "LeftLeg": AssetType.LeftLeg,
    "RightLeg": AssetType.RightLeg,
    "Package": AssetType.Package,
    "HairAccessory": AssetType.HairAccessory,
    "FaceAccessory": AssetType.FaceAccessory,
    "NeckAccessory": AssetType.NeckAccessory,
    "ShoulderAccessory": AssetType.ShoulderAccessory,
    "FrontAccessory": AssetType.FrontAccessory,
    "BackAccessory": AssetType.BackAccessory,
    "WaistAccessory": AssetType.WaistAccessory,
    "ClimbAnimation": AssetType.ClimbAnimation,
    "DeathAnimation": AssetType.DeathAnimation,
    "FallAnimation": AssetType.FallAnimation,
    "IdleAnimation": AssetType.IdleAnimation,
    "JumpAnimation": AssetType.JumpAnimation,
    "RunAnimation": AssetType.RunAnimation,
    "SwimAnimation": AssetType.SwimAnimation,
    "WalkAnimation": AssetType.WalkAnimation,
    "PoseAnimation": AssetType.PoseAnimation,
    "EmoteAnimation": AssetType.EmoteAnimation,
    "TShirtAccessory": AssetType.TShirtAccessory,
    "ShirtAccessory": AssetType.ShirtAccessory,
    "PantsAccessory": AssetType.PantsAccessory,
    "JacketAccessory": AssetType.JacketAccessory,
    "SweaterAccessory": AssetType.SweaterAccessory,
    "ShortsAccessory": AssetType.ShortsAccessory,
    "LeftShoeAccessory": AssetType.LeftShoeAccessory,
    "RightShoeAccessory": AssetType.RightShoeAccessory,
    "DressSkirtAccessory": AssetType.DressSkirtAccessory,
    "EyebrowAccessory": AssetType.EyebrowAccessory,
    "EyelashAccessory": AssetType.EyelashAccessory,
    "MoodAnimation": AssetType.MoodAnimation,
    "DynamicHead": AssetType.DynamicHead,
    "EarAccessory": AssetType.EarAccessory,
    "EyeAccessory": AssetType.EyeAccessory,
    "FaceMakeup": AssetType.FaceMakeup,
    "LipMakeup": AssetType.LipMakeup,
    "EyeMakeup": AssetType.EyeMakeup,
    "StorePreviewVideo": AssetType.StorePreviewVideo,
}


LEGACY_ASSET_TYPE_ENUMS = {
    1: AssetType.Image,
    2: AssetType.ClassicTShirt,
    3: AssetType.Audio,
    4: AssetType.MeshPart,
    5: AssetType.Lua,
    8: AssetType.Hat,
    9: AssetType.Place,
    10: AssetType.Model,
    11: AssetType.ClassicTShirt,
    12: AssetType.ClassicPants,
    13: AssetType.Decal,
    17: AssetType.ClassicHead,
    18: AssetType.Face,
    19: AssetType.Gear,
    21: AssetType.Badge,
    24: AssetType.Animation,
    27: AssetType.Torso,
    28: AssetType.RightArm,
    29: AssetType.LeftArm,
    30: AssetType.LeftLeg,
    31: AssetType.RightLeg,
    32: AssetType.Package,
    34: AssetType.GamePass,
    38: AssetType.Plugin,
    40: AssetType.MeshPart,
    41: AssetType.HairAccessory,
    42: AssetType.FaceAccessory,
    43: AssetType.NeckAccessory,
    44: AssetType.ShoulderAccessory,
    45: AssetType.FrontAccessory,
    46: AssetType.BackAccessory,
    47: AssetType.WaistAccessory,
    48: AssetType.ClimbAnimation,
    49: AssetType.DeathAnimation,
    50: AssetType.FallAnimation,
    51: AssetType.IdleAnimation,
    52: AssetType.JumpAnimation,
    53: AssetType.RunAnimation,
    54: AssetType.SwimAnimation,
    55: AssetType.WalkAnimation,
    56: AssetType.PoseAnimation,
    57: AssetType.EarAccessory,
    58: AssetType.EyeAccessory,
    61: AssetType.EmoteAnimation,
    62: AssetType.Video,
    64: AssetType.TShirtAccessory,
    65: AssetType.ShirtAccessory,
    66: AssetType.PantsAccessory,
    67: AssetType.JacketAccessory,
    68: AssetType.SweaterAccessory,
    69: AssetType.ShortsAccessory,
    70: AssetType.LeftShoeAccessory,
    71: AssetType.RightShoeAccessory,
    72: AssetType.DressSkirtAccessory,
    73: AssetType.FontFamily,
    76: AssetType.EyebrowAccessory,
    77: AssetType.EyelashAccessory,
    78: AssetType.MoodAnimation,
    79: AssetType.DynamicHead,
    88: AssetType.FaceMakeup,
    89: AssetType.LipMakeup,
    90: AssetType.EyeMakeup,
}


class ModerationStatus(Enum):
    """
    Enum denoting the current moderation status of an asset.

    Attributes:
        Unknown (0): The current moderation status is unknown.
        Reviewing (1): The asset has not completed moderation yet.
        Rejected (2): The asset failed moderation.
        Approved (3): The asset passed moderation.
    """

    Unknown = 0
    Reviewing = 1
    Rejected = 2
    Approved = 3


MODERATION_STATUS_ENUMS = {
    "Reviewing": ModerationStatus.Reviewing,
    "Rejected": ModerationStatus.Rejected,
    "Approved": ModerationStatus.Approved,
    "MODERATION_STATE_REVIEWING": ModerationStatus.Reviewing,
    "MODERATION_STATE_REJECTED": ModerationStatus.Rejected,
    "MODERATION_STATE_APPROVED": ModerationStatus.Approved,
}


class AssetPrivacy(Enum):
    """
    Enum denoting the privacy setting of an asset.

    Attributes:
        Unknown (0): An unknown privacy setting.
        Default (1): The default privacy setting for the asset set by Roblox.
        Restricted (2): The asset can only be used by the creator and those \
        with permission.
        OpenUse (3): Anyone on Roblox can use the asset.
    """

    Unknown = 0
    Default = 1
    Restricted = 2
    OpenUse = 3


ASSET_PRIVACY_ENUMS = {
    AssetPrivacy.Default: "default",
    AssetPrivacy.Restricted: "restricted",
    AssetPrivacy.OpenUse: "openUse",
}


class AssetSocialLink:
    """
    Represents a social link on an asset.

    Args:
        title: The text displayed for the social link.
        uri: The URI of the social link.

    Attributes:
        title: The text displayed for the social link.
        uri: The URI of the social link.
    """

    def __init__(self, uri: str, title: Optional[str] = None) -> None:
        self.title: Optional[str] = title
        self.uri: str = uri

    def __repr__(self) -> str:
        return f'<rblxopencloud.AssetSocialLink uri="{self.uri}">'


class AssetDeliveryLocation:
    """
    Represents a location to download an asset from Roblox.

    Attributes:
        uri: The URI to download the asset from.
        is_archived: Whether the asset has been archived.
        is_recordable: Whether the asset can be recorded in screen recordings.
        size_bytes: The size of the asset in bytes.
    """

    def __init__(self, data: dict) -> None:
        assert (
            type(data.get("location")) is str
        ), "Asset location data must contain a location."

        self.uri: str = data["location"]

        self.is_recordable: bool = data.get("isRecordable", False)
        self.is_archived: bool = data.get("isArchived", False)
        self.size_bytes: Optional[int] = None

        for metadata in data.get("assetMetadatas", []):
            if metadata.get("metadataType") == 1:
                self.size_bytes = int(metadata.get("value"))
                break

    def __repr__(self) -> str:
        return f'<rblxopencloud.AssetDeliveryLocation uri="{self.uri}">'

    def download(self) -> io.BytesIO:
        """
        Downloads the asset.

        Returns:
            A stream containing the asset file.
        """

        _, response, _ = send_request(
            method="GET",
            path=self.uri,
            expected_status=[200],
        )

        return io.BytesIO(response)


class Asset:
    """
    Represents an asset uploaded by a [`Creator`][rblxopencloud.Creator].

    Attributes:
        id: The asset's ID.
        name: The filtered name of the asset.
        description: The filtered description of the asset.
        type: The asset's type.
        creator: The user, group, or creator which uploaded the asset.
        moderation_status: The asset's current moderation status.
        revision_id: The ID of the current revision of the asset. *Will be \
        `None` if the asset type does not support updating.*
        revision_time: The time the current revision of the asset was \
        created. *Will be `None` if the asset type does not support updating.*
        is_archived: Whether the asset has been archived.
        icon_asset_id: The image asset ID of the asset's icon.
        preview_asset_ids: A list of asset IDs for the asset's preview images \
        and videos.
        facebook_social_link: The asset's Facebook social link.
        twitter_social_link: The asset's Twitter social link.
        youtube_social_link: The asset's YouTube social link.
        twitch_social_link: The asset's Twitch social link.
        discord_social_link: The asset's Discord social link.
        github_social_link: The asset's GitHub social link.
        roblox_social_link: The asset's Roblox social link.
        guilded_social_link: The asset's Guilded social link.
        devforum_social_link: The asset's DevForum social link.
        try_place_id: The place ID set for the asset's 'Try in Roblox' button.
    """

    def __init__(self, data: dict, creator, api_key) -> None:
        self.id: int = int(data.get("assetId"))
        self.name: str = data.get("displayName")
        self.description: str = data.get("description")
        self.is_archived: bool = (
            data.get("state") and data["state"] != "Active"
        )

        self.preview_asset_ids: Optional[list[int]] = None

        if data.get("previews"):
            self.preview_asset_ids = []
            for preview in data["previews"]:
                if preview.get("asset"):
                    self.preview_asset_ids.append(
                        int(preview["asset"].split("/")[1])
                    )

        self.__api_key = api_key

        from .group import Group
        from .user import User

        if (
            creatorid := data.get("creationContext", {})
            .get("creator", {})
            .get("userId")
        ):
            data_creator = User(creatorid, self.__api_key)
        else:
            data_creator = Group(
                data.get("creationContext", {}).get("creator", {})["groupId"],
                self.__api_key,
            )

        if (
            type(creator) in (Creator, User, Group)
            and data_creator.id == creator.id
        ):
            self.creator: Union[Creator, User, Group] = creator
        else:
            self.creator: Union[User, Group] = data_creator

        self.type: AssetType = ASSET_TYPE_ENUMS.get(
            data.get("assetType"), AssetType.Unknown
        )

        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            data.get("moderationResult", {}).get("moderationState"),
            ModerationStatus.Unknown,
        )

        self.icon_asset_id: Optional[int] = (
            int(data["icon"].split("/")[1]) if data.get("icon") else None
        )

        self.revision_id: Optional[int] = data.get("revisionId")
        self.revision_time: Optional[datetime] = (
            parser.parse(data["revisionCreateTime"])
            if data.get("revisionCreateTime")
            else None
        )

        self.facebook_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["facebookSocialLink"].get("title"),
                data["facebookSocialLink"].get("uri"),
            )
            if data.get("facebookSocialLink")
            else None
        )

        self.twitter_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["twitterSocialLink"].get("title"),
                data["twitterSocialLink"].get("uri"),
            )
            if data.get("twitterSocialLink")
            else None
        )
        self.youtube_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["youtubeSocialLink"].get("title"),
                data["youtubeSocialLink"].get("uri"),
            )
            if data.get("youtubeSocialLink")
            else None
        )
        self.twitch_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["twitchSocialLink"].get("title"),
                data["twitchSocialLink"].get("uri"),
            )
            if data.get("twitchSocialLink")
            else None
        )
        self.discord_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["discordSocialLink"].get("title"),
                data["discordSocialLink"].get("uri"),
            )
            if data.get("discordSocialLink")
            else None
        )
        self.github_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["githubSocialLink"].get("title"),
                data["githubSocialLink"].get("uri"),
            )
            if data.get("githubSocialLink")
            else None
        )
        self.roblox_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["robloxSocialLink"].get("title"),
                data["robloxSocialLink"].get("uri"),
            )
            if data.get("robloxSocialLink")
            else None
        )
        self.guilded_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["guildedSocialLink"].get("title"),
                data["guildedSocialLink"].get("uri"),
            )
            if data.get("guildedSocialLink")
            else None
        )
        self.devforum_social_link: AssetSocialLink = (
            AssetSocialLink(
                data["devForumSocialLink"].get("title"),
                data["devForumSocialLink"].get("uri"),
            )
            if data.get("devForumSocialLink")
            else None
        )

        self.try_place_id: Optional[int] = (
            int(data["tryAssetSocialLink"]["uri"])
            if data.get("tryAssetSocialLink", {}).get("uri")
            else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.Asset id={self.id} type={self.type}>"

    def fetch_delivery_location(
        self, version_number: Optional[int] = None
    ) -> AssetDeliveryLocation:
        """
        Fetches the download location for this asset using Asset Delivery.

        Requires the `legacy-assets:manage` API key permission.

        Args:
            version_number: The version number of the asset to fetch the \
                location for. If not provided, the latest version will be used.

        Returns:
            An [`AssetDeliveryLocation`][rblxopencloud.AssetDeliveryLocation] containing \
            information on downloading the asset.
        """

        return self.creator.fetch_asset_delivery_location(
            self.id,
            version_number=version_number,
            expected_asset_type=self.type,
        )

    async def fetch_creator_store_product(self) -> "CreatorStoreProduct":
        """
        Fetches the creator store product information for this asset, if it \
            is on the creator store.

        Returns:
            An [`CreatorStoreProduct`][rblxopencloud.CreatorStoreProduct] \
                representing the asset as a prodct.
        """

        return await self.creator.fetch_creator_store_product(
            self.type, self.id
        )

    async def fetch_creator_store_prodcut(self) -> "CreatorStoreProduct":
        # Retained as misspelling of fetch_creator_store_product in prior version.
        return await self.fetch_creator_store_product()

    async def fetch_toolbox_asset(self) -> "ToolboxAsset":
        """
        Fetches the toolbox information about the asset. This will also update \
        the current asset object with any information fetched, such as name, \
        description, type, social links, and try place ID.

        Requires `creator-store-product:read` on an API key. OAuth2 authorization \
        is not supported. No authorization is supported (i.e. `api_key` is `None`).

        Returns:
            The asset information for the toolbox asset.
        """

        toolbox_asset = await self.creator.fetch_toolbox_asset(self.id)

        self.name = toolbox_asset.name or self.name
        self.description = toolbox_asset.description or self.description
        self.type = toolbox_asset.asset_type or self.type

        self.facebook_social_link = (
            toolbox_asset.facebook_social_link or self.facebook_social_link
        )
        self.twitter_social_link = (
            toolbox_asset.twitter_social_link or self.twitter_social_link
        )
        self.youtube_social_link = (
            toolbox_asset.youtube_social_link or self.youtube_social_link
        )
        self.twitch_social_link = (
            toolbox_asset.twitch_social_link or self.twitch_social_link
        )
        self.discord_social_link = (
            toolbox_asset.discord_social_link or self.discord_social_link
        )
        self.github_social_link = (
            toolbox_asset.github_social_link or self.github_social_link
        )
        self.guilded_social_link = (
            toolbox_asset.guilded_social_link or self.guilded_social_link
        )
        self.roblox_social_link = (
            toolbox_asset.roblox_social_link or self.roblox_social_link
        )
        self.devforum_social_link = (
            toolbox_asset.devforum_social_link or self.devforum_social_link
        )
        self.try_place_id = toolbox_asset.try_place_id or self.try_place_id
        self.preview_asset_ids = (
            (toolbox_asset.preview_image_asset_ids or [])
            + (toolbox_asset.preview_video_asset_ids or [])
        ) or self.preview_asset_ids

        toolbox_asset.asset = self

        return toolbox_asset

    async def fetch_version(self, version_number: int) -> "AssetVersion":
        """
        Fetches a specific version of the asset.

        Args:
            version_number: The version number of the asset to fetch.

        Returns:
            An [`AssetVersion`][rblxopencloud.AssetVersion] representing the \
            specified version of the asset.
        """

        return await self.creator.fetch_asset_version(self.id, version_number)

    async def list_versions(
        self, limit: int = None
    ) -> AsyncGenerator[Any, "AssetVersion"]:
        """
        Iterates all avaliable versions of the asset, providing the latest \
        version first.

        Args:
            limit: The maximum number of versions to return.
        
        Yields:
            An asset version for each version of the asset.
        """

        async for version in self.creator.list_asset_versions(self.id, limit):
            yield version

    async def rollback(self, version_number: int) -> "AssetVersion":
        """
        Rolls back the asset to restore a previous version.

        Args:
            version_number: The version number of the asset to roll back to.

        Returns:
            An [`AssetVersion`][rblxopencloud.AssetVersion] representing the \
            rolled back version of the asset.
        """

        return await self.creator.rollback_asset(self.id, version_number)

    async def archive(self) -> "Asset":
        """
        Archives the asset so it cannot be seen on the website or used in \
        experiences.

        Returns:
            The updated asset information.
        """

        _, data, _ = await send_request(
            "POST",
            f"assets/v1/assets/{self.id}:archive",
            authorization=self.__api_key,
            expected_status=[200],
        )

        self.__init__(data, self, self.__api_key)

        return self

    async def restore(self) -> "Asset":
        """
        Unarchives an archived asset.

        Returns:
            The updated asset information.
        """

        _, data, _ = await send_request(
            "POST",
            f"assets/v1/assets/{self.id}:restore",
            authorization=self.__api_key,
            expected_status=[200],
        )

        self.__init__(data, self, self.__api_key)

        return self


class AssetVersion:
    """
    Represents a version of an asset uploaded on to Roblox.

    Attributes:
        version_number: This asset version's revision ID.
        asset_id: The asset's ID.
        creator: The user, group, or creator which uploaded the asset.
        moderation_status: The moderation status of this version.
    """

    def __init__(self, data, creator) -> None:
        self.version_number: int = data["path"].split("/")[3]
        self.asset_id: int = data["path"].split("/")[1]

        self.creator: Union[Creator, User, Group] = creator

        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            data.get("moderationResult", {}).get("moderationState"),
            ModerationStatus.Unknown,
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.AssetVersion \
asset_id={self.asset_id} version_number={self.version_number}>"


class ProductRestriction(Enum):
    Unknown = 0
    Unspecified = 1
    ItemRestricted = 2
    SellerTemporarilyRestricted = 3
    SellerPermanentlyRestricted = 4
    SellerNoLongerActive = 5


RESTRICTION_ENUMS = {
    "RESTRICTION_UNSPECIFIED": ProductRestriction.Unspecified,
    "SOLD_ITEM_RESTRICTED": ProductRestriction.ItemRestricted,
    "SELLER_TEMPORARILY_RESTRICTED": (
        ProductRestriction.SellerTemporarilyRestricted
    ),
    "SELLER_PERMANENTLY_RESTRICTED": (
        ProductRestriction.SellerPermanentlyRestricted
    ),
    "SELLER_NO_LONGER_ACTIVE": ProductRestriction.SellerNoLongerActive,
}


class Money:
    """
    Represents a price on the Roblox platform, such as on the creator store.

    Arguments:
        currency: The [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) \
            currency code for this price.
        quantity: The quantity of the currency. For instance, `4.99` would be \
            four dollars and ninety-nine cents in USD.

    Attributes:
        currency: The [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) \
            currency code for this price. Crypto and virtual \
            currencies will begin with `X-`. 
        quantity: The quantity of the currency. For instance, `4.99` would be \
            four dollars and ninety-nine cents in USD.

    **Supported Operations:**

    | Operator | Description |
    | -------- | ----------- |
    | `==`     | Whether two [`Money`][rblxopencloud.Money] have the same \
        currency and quantity or `quantity` equals the [`float`][float]. |
    | `<`      | Whether the `quantity` is less than the `quantity` of \
        another [`Money`][rblxopencloud.Money] with the same currency or a \
        [`float`][float]. Also supports `<=`. |
    | `>`      | Whether the `quantity` is greater than the `quantity` of \
        another [`Money`][rblxopencloud.Money] with the same currency or a \
        [`float`][float]. Also supports `>=`. |
    """

    def __init__(self, currency: str, quantity: float) -> None:
        self.currency: str = currency
        self.quantity: float = quantity

    def __repr__(self) -> str:
        return f'<rblxopencloud.Money currency="{self.currency}" \
quantity={self.quantity}>'

    def __eq__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            return NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity == value.quantity

        return self.quantity == value

    def __lt__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            return NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity < value.quantity

        return self.quantity < value

    def __gt__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            return NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity > value.quantity

        return self.quantity > value

    def __le__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            return NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity <= value.quantity

        return self.quantity <= value

    def __gt__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            return NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity >= value.quantity

        return self.quantity >= value

    def to_scientific_notation(self) -> dict:
        """
        Converts the quantity to a dict containing a significand and exponent \
        used internally for Roblox's API.

        Returns:
            A dictionary with `significand` and `exponent` values \
                representing the quantity.
        """

        num_str = f"{self.quantity:.15g}"
        decimal_places = len(num_str.split(".")[1]) if "." in num_str else 0

        return {
            "significand": int(self.quantity * (10**decimal_places)),
            "exponent": -decimal_places,
        }


CREATOR_STORE_ASSET_ID_KEYS = {
    AssetType.Unknown: "assetId",
    AssetType.Model: "modelAssetId",
    AssetType.Plugin: "pluginAssetId",
    AssetType.Audio: "audioAssetId",
    AssetType.Decal: "decalAssetId",
    AssetType.MeshPart: "meshPartAssetId",
    AssetType.Video: "videoAssetId",
    AssetType.FontFamily: "fontFamilyAssetId",
}

class CreatorStoreProduct:
    """
    Represents an asset as a product on the creator store.

    Attributes:
        asset_id (int): The ID of the product's asset.
        asset_type (AssetType): The product's asset type.
        creator (Union[User, Group]): The user or group who created the asset.
        purchasable (bool): Whether the product can be purchased.
        published (bool): Whether the product is considered published from \
            the creator's perspective.
        restrictions (list[ProductRestriction]): A list of restrictions \
            applied to the product.
        base_price (Money): The base price set by the creator.
        purchase_price (Money): The price of the asset to the user, factoring \
        locale-specific considerations.
    """

    def __init__(self, data: dict, api_key) -> None:

        self.asset_id: int = None
        self.asset_type: AssetType = AssetType.Unknown

        for asset_id_key, type in CREATOR_STORE_ASSET_ID_KEYS.items():
            if asset_id := data.get(asset_id_key):
                self.asset_id: int = int(asset_id)
                self.asset_type: AssetType = type
                break

        from .group import Group
        from .user import User

        if creatorid := data.get("userSeller"):
            self.creator: Union[User, Group] = User(creatorid, api_key)
        else:
            self.creator: Union[User, Group] = User(
                data["groupSeller"], api_key
            )

        self.purchasable: bool = data.get("purchasable")
        self.published: bool = data.get("published")

        restrictions = []

        for restriction in data.get("restrictions", []):
            restrictions.append(
                RESTRICTION_ENUMS.get(restriction, ProductRestriction.Unknown)
            )

        self.restrictions: list[ProductRestriction] = restrictions

        self.base_price: Money = (
            Money(
                data["purchasePrice"]["currencyCode"],
                data["basePrice"]["quantity"]["significand"]
                * 10 ** data["basePrice"]["quantity"]["exponent"],
            )
            if data.get("basePrice")
            else None
        )

        self.purchase_price: Money = (
            Money(
                data["purchasePrice"]["currencyCode"],
                data["purchasePrice"]["quantity"]["significand"]
                * 10 ** data["purchasePrice"]["quantity"]["exponent"],
            )
            if data.get("purchasePrice")
            else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.CreatorStoreProduct \
asset_id={self.asset_id} asset_type={self.asset_type}>"

    async def fetch_asset(self) -> Asset:
        """
        Fetches the asset information for this product.

        Returns:
            An [`Asset`][rblxopencloud.Asset] representing the product's asset.
        """

        return await self.creator.fetch_asset(self.asset_id)


ASSET_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "flac": "audio/flac",
    "png": "image/png",
    "jpeg": "image/jpeg",
    "bmp": "image/bmp",
    "tga": "image/tga",
    "fbx": "model/fbx",
    "gltf": "model/gltf+json",
    "glb": "model/gltf-binary",
    "rbxm": "model/x-rbxm",
    "rbxmx": "model/x-rbxm",
    "mp4": "video/mp4",
    "mov": "video/mov",
}


class AssetPermissionSubjectType(Enum):
    """
    Enum denoting a permission subject type for an asset.

    Attributes:
        Unknown (0): An unknown or invalid asset permission subject type.
        All (1): Everyone on Roblox.
        User (2): A specific user on Roblox.
        Group (3): A specific group on Roblox.
        Experience (4): A specific experience on Roblox.
    """

    Unknown = 0
    All = 1
    User = 2
    Group = 3
    GroupRole = 4
    Experience = 5


class AssetPermissionSubject:
    """
    Data class representing a subject that can be granted permissions for an \
    asset. For instance, a user, group, group role, experience, or everyone. \
    When using `All`, the `id` field should be omitted; otherwise, it should \
    be the ID of the user, group, group role, or experience.

    Where this class is used, a [`User`][rblxopencloud.User],
    [`Group`][rblxopencloud.Group], [`GroupRole`][rblxopencloud.GroupRole], or
    [`Experience`][rblxopencloud.Experience] object can also be used in its \
    place.

    Args:
        type (AssetPermissionSubjectType): The type of subject.
        id (Optional[int]): The ID of the subject, if applicable.
    """

    def __init__(
        self,
        type: AssetPermissionSubjectType,
        id: Optional[int] = None,
    ):
        self.type: AssetPermissionSubjectType = type
        self.id: Optional[int] = id


class AssetPermissionAction(Enum):
    """
    Enum denoting a permission access action for an asset subject.

    Attributes:
        Unknown (0): An unknown or invalid asset permission action.
        Edit (1): The subject can edit the asset.
        Use (2): The subject can use the asset.
        Download (3): The subject can download the asset.
        CopyFromRcc (4): The subject use `AssetService:CreatePlaceAsync()` \
            with this asset.
        UpdateFromRcc (5): The subject can use `AssetService:UpdatePlaceAsync()` \
            with this asset.
    
    **Allowed Asset Actions**

    | Asset Type | Subject Type | Actions |
    | --- | --- | --- |
    | Animation, Audio, Mesh Part, Video | Group, Use, Experience | Use |
    | Decal, Image, Mesh | All, Group, Use, Experience | Use |
    | Model | Use | Use, Edit |
    | Model | Group, Experience | Use |
    | Place | All | Download |
    | Place | Experience | CopyFromRcc, UpdateFromRcc |

    - Enabling Download for All on a Place *uncopylooks* the place.
    - Allowing All on a Decal, Image, or Mesh means the asset is Open Use.
    """

    Unknown = 0
    Edit = 1
    Use = 2
    Download = 3
    CopyFromRcc = 4
    UpdateFromRcc = 5


class AssetPermissionRequest:
    """
    Data class representing an asset in a permission grant request.

    Args:
        asset_id (int): The ID of the asset being granted permissions.
        grant_dependencies (bool): Whether to also grant permissions for \
            the asset's dependencies.
        version_number (Optional[int]): The version number of the asset to \
            use when granting permission to dependencies.
    """

    def __init__(
        self,
        asset_id: int,
        grant_dependencies: bool = False,
        version_number: Optional[int] = None,
    ) -> None:
        self.asset_id = asset_id
        self.grant_dependencies = grant_dependencies
        self.version_number = version_number

    def __repr__(self):
        return f"<rblxopencloud.AssetPermissionRequest asset_id={self.asset_id} \
grant_dependencies={self.grant_dependencies} version_number={self.version_number}>"


class AssetPermissionResultError(Enum):
    """
    Enum denoting a failure reason for an asset permission grant request.

    Attributes:
        Unknown (0): An unknown or invalid asset permission action.
        InvalidRequest (1): The request was invalid.
        AssetNotFound (2): The specified asset could not be found.
        CannotManageAsset (3): The asset cannot be managed.
        PublicAssetCannotBeGrantedTo (4): The asset is already Open Use.
        CannotManageSubject (5): The subject cannot be managed.
        SubjectNotFound (6): The specified subject could not be found.
        AssetTypeNotEnabled (7): The asset type is not enabled for permissions.
        PermissionLimitReached (8): The permission limit has been reached.
        DependenciesLimitReached (9): The dependencies limit has been reached.
    """

    Unknown = 0
    InvalidRequest = 1
    AssetNotFound = 2
    CannotManageAsset = 3
    PublicAssetCannotBeGrantedTo = 4
    CannotManageSubject = 5
    SubjectNotFound = 6
    AssetTypeNotEnabled = 7
    PermissionLimitReached = 8
    DependenciesLimitReached = 9


class AssetPermissionResult:
    """
    Represents the result of an asset permission grant request.

    Attributes:
        granted_asset_ids (list[int]): A list of asset IDs for which \
            permissions were successfully granted.
        failed_asset_ids (dict[int, AssetPermissionResultError]): A mapping \
            of asset IDs to their corresponding failure reasons for assets \
            that failed to have permissions granted.
    """

    def __init__(self, data: dict) -> None:
        self.granted_asset_ids: list[int] = data.get("successAssetIds", [])
        self.failed_asset_ids: dict[int, AssetPermissionResultError] = {}

        for error in data.get("errors", []):
            self.failed_asset_ids[error["assetId"]] = (
                AssetPermissionResultError.__members__.get(
                    error["code"], AssetPermissionResultError.Unknown
                )
            )

    def __repr__(self) -> str:
        return f"<rblxopencloud.AssetPermissionResult \
granted_asset_ids={self.granted_asset_ids} \
failed_asset_ids={self.failed_asset_ids}>"


class Creator:
    """
    Represents an object that can upload assets, such as a user or a group.

    Attributes:
        id (int): The ID of the creator.
    """

    def __init__(self, id, api_key, type) -> None:
        self.id: int = id
        self.__api_key = api_key
        self.__creator_type = type

    def __repr__(self) -> str:
        return f"<rblxopencloud.Creator id={self.id}>"

    async def fetch_asset(self, asset_id: int) -> Asset:
        """
        Fetches an asset uploaded to Roblox.

        Args:
            asset_id: The ID of the asset to fetch.

        Returns:
            An [`Asset`][rblxopencloud.Asset] representing the asset.
        """

        from .apikey import ApiKey

        asset = await ApiKey(self.__api_key).fetch_asset(asset_id)

        if (
            asset.creator.id == self.id
            and asset.creator.__class__.__name__ == self.__creator_type
        ):
            asset.creator = self

        return asset

    async def upload_asset(
        self,
        file: io.BytesIO,
        asset_type: Union[AssetType, str],
        name: str,
        description: str,
        expected_robux_price: int = 0,
        asset_privacy: AssetPrivacy = AssetPrivacy.Default,
    ) -> Operation[Asset]:
        """
        Uploads the file to Roblox as an asset and returns an \
        [`Operation`][rblxopencloud.Operation]. The following asset types are \
        currently supported:

        | Asset Type | File Formats |
        | --- | --- |
        | Decal | `.png`, `.jpeg`, `.bmp`, `.tga` |
        | Audio | `.mp3`, `.ogg`, `.wav`, `.flac` |
        | Model | `.fbx`, `.gltf`, `.glb`, `.rbxm`, `.rbxmx` |
        | Video | `.mp4`, `.mov` |
        | Animation | `.rbxm`, `.rbxmx` |

        According to Roblox staff [in this DevForum \
        post](https://devforum.roblox.com/t/3308172/11), the maximum file \
        size using the API is 30MB.

        Args:
            file: The file opened in bytes to be uploaded.
            asset_type: The [`AssetType`][rblxopencloud.AssetType] for the \
            asset type you're uploading.
            name: The name of your asset.
            description: The description of your asset.
            expected_robux_price: The amount of robux expected to upload this \
            asset. Will fail if lower than the actual price.
            asset_privacy: Whether the asset is restricted or open use.

        Returns:
            Returns a [`Operation`][rblxopencloud.Operation] for the asset \
            upload operation where `T` is an [`Asset`][rblxopencloud.Asset].
        
        !!! danger
            Avoid uploading assets to Roblox that you don't have full control \
            over, such as AI generated assets or content created by unknown \
            people. Assets uploaded that break Roblox's Terms of Services can \
            get your account moderated.

            For OAuth2 developers, it has been confirmed by Roblox staff [in \
            this DevForum post](https://devforum.roblox.com/t/2401354/36), \
            that your app will not be punished if a malicious user uses it to \
            upload Terms of Service violating content, and instead the \
            authorizing user's account will be punished.
        """

        payload = {
            "assetType": (
                asset_type.name
                if type(asset_type) == AssetType
                else asset_type
            ),
            "creationContext": {
                "assetPrivacy": ASSET_PRIVACY_ENUMS.get(
                    asset_privacy, "default"
                ),
                "creator": (
                    {
                        "userId": str(self.id),
                    }
                    if self.__creator_type == "User"
                    else {"groupId": str(self.id)}
                ),
                "expectedPrice": expected_robux_price,
            },
            "displayName": name,
            "description": description,
        }

        body, contentType = urllib3.encode_multipart_formdata(
            {
                "request": json.dumps(payload),
                "fileContent": (
                    file.name,
                    file.read(),
                    ASSET_MIME_TYPES.get(file.name.split(".")[-1]),
                ),
            }
        )

        status, data, _ = await send_request(
            "POST",
            "assets/v1/assets",
            authorization=self.__api_key,
            expected_status=[200, 400],
            headers={"content-type": contentType},
            data=body,
        )

        if status == 400:
            if data["message"] == '"InvalidImage"':
                raise InvalidFile(status, body)

            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(status, body)

            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(status, body)

            raise HttpException(status, data)

        return Operation(
            f"assets/v1/{data['path']}",
            self.__api_key,
            Asset,
            creator=self,
            api_key=self.__api_key,
        )

    async def update_asset(
        self,
        asset_id: int,
        file: io.BytesIO = None,
        name: str = None,
        description: str = None,
        expected_robux_price: int = 0,
        facebook_social_link: Optional[Union[AssetSocialLink, None]] = None,
        twitter_social_link: Optional[Union[AssetSocialLink, None]] = None,
        youtube_social_link: Optional[Union[AssetSocialLink, None]] = None,
        twitch_social_link: Optional[Union[AssetSocialLink, None]] = None,
        discord_social_link: Optional[Union[AssetSocialLink, None]] = None,
        github_social_link: Optional[Union[AssetSocialLink, None]] = None,
        roblox_social_link: Optional[Union[AssetSocialLink, None]] = None,
        guilded_social_link: Optional[Union[AssetSocialLink, None]] = None,
        devforum_social_link: Optional[Union[AssetSocialLink, None]] = None,
        try_place_id: Optional[Union[int, bool]] = None,
    ) -> Operation[Asset]:
        """
        Updates an asset on Roblox with the provided file. The following \
        asset types are currently supported for file uploading:

        | Asset Type | File Formats |
        | --- | --- |
        | Model | `.fbx` |

        Args:
            asset_id: The ID of the asset to update.
            file: The file opened in bytes to upload. The asset must be one \
            of the supported file formats above.
            name: The new name of the asset.
            description: The new description for the asset.
            expected_robux_price: The amount of robux expected to update this \
            asset. Will fail if lower than the actual price.
            facebook_social_link: The new Facebook social link for the asset, \
            or `False` to remove the social link.
            twitter_social_link: The new Twitter social link for the asset, \
            or `False` to remove the social link.
            youtube_social_link: The new YouTube social link for the asset, \
            or `False` to remove the social link.
            twitch_social_link: The new Twitch social link for the asset, \
            or `False` to remove the social link.
            discord_social_link: The new Discord social link for the asset, \
            or `False` to remove the social link.
            github_social_link: The new GitHub social link for the asset, \
            or `False` to remove the social link.
            roblox_social_link: The new Roblox social link for the asset, \
            or `False` to remove the social link.
            guilded_social_link: The new Guilded social link for the asset, \
            or `False` to remove the social link.
            devforum_social_link: The new DevForum social link for the asset, \
            or `False` to remove the social link.
            try_place_id: A place ID to set for the asset's 'Try in Roblox' \
            button. Set to `False` to remove the Try in Roblox button.

        Returns:
            Returns a [`Operation`][rblxopencloud.Operation] for the asset \
            update operation where `T` is an [`Asset`][rblxopencloud.Asset].
        """

        payload, field_mask = {
            "assetId": asset_id,
            "creationContext": {"expectedPrice": expected_robux_price},
            "displayName": name,
            "description": description,
        }, []

        if name:
            field_mask.append("displayName")
        if description:
            field_mask.append("description")

        for platform, value in {
            "facebook": facebook_social_link,
            "twitter": twitter_social_link,
            "youtube": youtube_social_link,
            "twitch": twitch_social_link,
            "discord": discord_social_link,
            "guilded": guilded_social_link,
            "github": github_social_link,
            "roblox": roblox_social_link,
            "devforum": devforum_social_link,
        }.items():
            # ignore parameters with a value of None
            if value is not None:
                if value is True:
                    raise ValueError(
                        f"{platform}_social_link should be either \
                    AssetSocialLink or False."
                    )

                if platform == "devforum":
                    platform = "devForum"

                if type(value) == AssetSocialLink:
                    payload[f"{platform}SocialLink"] = {
                        "title": value.title,
                        "uri": value.uri,
                    }
                    field_mask.append(f"{platform}SocialLink")
                else:
                    # any social link is being removed
                    field_mask.append(f"{platform}SocialLink")

        if try_place_id is not None:
            if try_place_id is not False:
                payload["tryAssetSocialLink"] = {"uri": str(try_place_id)}
            field_mask.append("tryAssetSocialLink")

        if file:
            body, contentType = urllib3.encode_multipart_formdata(
                {
                    "request": json.dumps(payload),
                    "fileContent": (
                        file.name,
                        file.read(),
                        ASSET_MIME_TYPES.get(file.name.split(".")[-1]),
                    ),
                }
            )
        else:
            body, contentType = urllib3.encode_multipart_formdata(
                {"request": json.dumps(payload)}
            )

        status, data, _ = await send_request(
            "PATCH",
            f"assets/v1/assets/{asset_id}",
            authorization=self.__api_key,
            expected_status=[200, 400],
            headers={"content-type": contentType},
            data=body,
            params={"updateMask": ",".join(field_mask)},
        )

        if status == 400:
            if data["message"] == '"InvalidImage"':
                raise InvalidFile(status, body)

            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(status, body)

            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(status, body)

            raise HttpException(status, data)

        return Operation(
            f"assets/v1/{data['path']}",
            self.__api_key,
            Asset,
            creator=self,
            api_key=self.__api_key,
        )

    async def list_asset_versions(
        self, asset_id: int, limit: int = None
    ) -> AsyncGenerator[Any, AssetVersion]:
        """
        Iterates all avaliable versions of the asset, providing the latest \
        version first.

        Args:
            asset_id: The ID of the asset to find versions for.
            limit: The maximum number of versions to return.
        
        Yields:
            An asset version for each version of the asset.
        """

        async for entry in iterate_request(
            "GET",
            f"assets/v1/assets/{asset_id}/versions",
            params={
                "maxPageSize": limit if limit and limit <= 50 else 50,
            },
            authorization=self.__api_key,
            expected_status=[200],
            data_key="assetVersions",
            cursor_key="pageToken",
        ):
            yield AssetVersion(entry, self)

    async def fetch_asset_version(
        self, asset_id: int, version_number: int
    ) -> AssetVersion:
        """
        Fetches the version for a specific version number of the asset.

        Args:
            asset_id: The ID of the asset to find the version for.
            version_number: The version number to find.

        Returns:
            The found asset version.
        """

        _, data, _ = await send_request(
            "GET",
            f"assets/v1/assets/{asset_id}/versions/{version_number}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return AssetVersion(data, self)

    async def rollback_asset(
        self, asset_id: int, version_number: int
    ) -> AssetVersion:
        """
        Reverts the asset to a previous version specified.

        Args:
            asset_id: The ID of the asset to rollback.
            version_number: The version number to rollback to.

        Returns:
            The new asset version.
        """

        _, data, _ = await send_request(
            "POST",
            f"assets/v1/assets/{asset_id}/versions:rollback",
            authorization=self.__api_key,
            expected_status=[200],
            json={
                "assetVersion": f"assets/{asset_id}/versions/{version_number}"
            },
        )

        return AssetVersion(data, self)

    async def archive_asset(self, asset_id: int) -> Asset:
        """
        Archives the asset so it cannot be seen on the website or used in \
        experiences.

        Args:
            asset_id: The ID of the asset to archive.

        Returns:
            The updated asset information.
        """

        _, data, _ = await send_request(
            "POST",
            f"assets/v1/assets/{asset_id}:archive",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return Asset(data, self, self.__api_key)

    async def restore_asset(self, asset_id: int) -> Asset:
        """
        Unarchives an archived asset.

        Args:
            asset_id: The ID of the archived asset to unarchive.

        Returns:
            The updated asset information.
        """

        _, data, _ = await send_request(
            "POST",
            f"assets/v1/assets/{asset_id}:restore",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return Asset(data, self, self.__api_key)

    async def fetch_asset_delivery_location(
        self,
        asset_id: int,
        version_number: Optional[int] = None,
        expected_asset_type: Optional[Union[AssetType, str]] = None,
    ) -> AssetDeliveryLocation:
        """
        Fetches the download location for this asset using Asset Delivery.

        Requires the `legacy-assets:manage` API key permission.

        Args:
            asset_id: The ID of the asset to fetch the location for.
            version_number: The specific version number of the asset to \
            fetch the location for. Defaults to the latest version.
            expected_asset_type: The expected type of the asset. If provided, \
            the request will fail if the asset is not of the provided type.


        Returns:
            An [`AssetDeliveryLocation`][rblxopencloud.AssetDeliveryLocation] containing \
            information on downloading the asset.
        """

        if isinstance(expected_asset_type, AssetType):
            expected_asset_type = expected_asset_type.name

        path_suffix = f"assetId/{asset_id}"

        if version_number is not None:
            path_suffix += f"/version/{version_number}"

        _, data, _ = await send_request(
            "GET",
            f"asset-delivery-api/v1/{path_suffix}",
            authorization=self.__api_key,
            expected_status=[200],
            headers={
                "AssetType": expected_asset_type,
            },
        )

        assert isinstance(data, dict), "Received invalid response from Roblox."

        if isinstance(data.get("errors"), list):
            if any(error.get("code") == 404 for error in data["errors"]):
                raise NotFound(status=404, body=data)
            elif any(error.get("code") == 409 for error in data["errors"]):
                raise Forbidden(status=409, body=data)
            else:
                raise HttpException(
                    status=200,
                    body=data,
                )

        return AssetDeliveryLocation(data)

    async def fetch_creator_store_product(
        self, asset_type: Union[AssetType, str], product_id: int
    ) -> CreatorStoreProduct:
        """
        Fetches information about an asset on the creator store.

        Args:
            asset_type: The type of asset the product is.
            product_id: The ID of the asset to fetch.

        Returns:
            A [`CreatorStoreProduct`][rblxopencloud.CreatorStoreProduct] \
            representing the asset.

        Tip:
            If the asset type is unknown or other information such as the \
            description is required, use the \
            [`fetch_asset`][rblxopencloud.ApiKey.fetch_asset].
        """

        from .apikey import ApiKey

        product = await ApiKey(self.__api_key).fetch_creator_store_product(
            asset_type, product_id
        )

        if (
            product.creator.id == self.id
            and product.creator.__class__.__name__ == self.__creator_type
        ):
            product.creator = self

        return product

    async def fetch_toolbox_asset(self, asset_id: int) -> "ToolboxAsset":
        """
        Fetches information about an asset in the toolbox.

        Requires `creator-store-product:read` on an API key. OAuth2 authorization \
        is not supported. No authorization is supported (i.e. `api_key` is `None`).

        Args:
            asset_id: The ID of the asset to fetch.

        Returns:
            The asset information for the toolbox asset. The current creator \
            object (e.g. user or group) will also be updated with resolved \
            information such as name and verified status.
        
        !!! tip
            To search for assets in the toolbox, use \
            [`ApiKey.search_toolbox`][rblxopencloud.ApiKey.search_toolbox].
        """

        _, data, _ = await send_request(
            "GET",
            f"toolbox-service/v2/assets/{asset_id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return ToolboxAsset(data, self, self.__api_key)

    async def grant_assets_permission(
        self,
        action: AssetPermissionAction,
        subject: Union[
            AssetPermissionSubject, "Experience", "User", "Group", "GroupRole"
        ],
        assets: list[Union[int, Asset, AssetPermissionRequest]],
    ) -> AssetPermissionResult:
        """
        Grants permission to the subject to perform the specified action \
        on the provided assets. See the table in \
        [`AssetPermissionAction`][rblxopencloud.AssetPermissionAction] for \
        allowed actions per asset and subject type.

        Args:
            action: The action to grant permission for.
            subject: The subject to grant the permission to.
            assets: The asset IDs or assets to grant permission for. Use \
                [`AssetPermissionRequest`][rblxopencloud.AssetPermissionRequest] \
                to specify additional options per asset.
        
        Returns:
            The results of each asset permission grant request. Do not expect \
            the function to raise an exceptions for errors, instead check the \
            `failed_asset_ids` attribute.
        
        !!! warning
            Once permission is granted to a subject, it cannot be revoked \
            using the API. It may also not be able to be revoked using the \
            website, depending on the asset type and subject type. For \
            instance, granting Open Use to All on a decal sets it as Open Use \
            which cannot be revoked; however, granting Download to All on a \
            place can be revoked on the Creator Dashboard.
        
        Examples:
            Setting the root place of an experience to be *uncopylocked.*
            ```python
            from rblxopencloud import Experience, AssetPermissionAction, \
            AssetPermissionSubject, AssetPermissionSubjectType
            
            experience = Experience(00000000, "...") # initialise with ID and API key
            experience.fetch_info() # Fetch root place

            # grant download permission to everyone on Roblox
            experience.creator.grant_assets_permission(
                action=AssetPermissionAction.Download,
                subject=AssetPermissionSubject(
                    type=AssetPermissionSubjectType.All
                ),
                assets=[experience.root_place.get_asset()]
            )
            >>> <rblxopencloud.AssetPermissionResult \
granted_asset_ids=[00000000] failed_asset_ids={}>
            ```

            Setting an asset to be Open Use.
            ```python
            from rblxopencloud import User, AssetPermissionAction, \
            AssetPermissionSubject, AssetPermissionSubjectType, \
            AssetPermissionRequest

            creator = User(00000000, "...") # initialise with user ID and API key

            creator.grant_assets_permission(
                action=AssetPermissionAction.Use,
                subject=AssetPermissionSubject(
                    type=AssetPermissionSubjectType.All
                ),
                assets=[
                    AssetPermissionRequest(
                        asset_id=00000000, # ID of the asset to grant permission for
                        grant_dependencies=True
                    )
                ]
            )
            >>> <rblxopencloud.AssetPermissionResult \
granted_asset_ids=[00000000] failed_asset_ids={}>
            ```

            Granting a specific user permission to use an asset.
            ```python
            from rblxopencloud import User, AssetPermissionAction, \
            AssetPermissionSubject, AssetPermissionSubjectType, \
            AssetPermissionRequest

            creator = User(00000000, "...") # initialise with user ID and API key

            creator.grant_assets_permission(
                action=AssetPermissionAction.Use,
                subject=AssetPermissionSubject( # subject can also be a User or Group object
                    type=AssetPermissionSubjectType.User,
                    id=00000000 # ID of the user to grant permission to
                ),
                assets=[
                    AssetPermissionRequest(
                        asset_id=00000000, # ID of the asset to grant permission for
                        grant_dependencies=True
                    )
                ]
            )
            >>> <rblxopencloud.AssetPermissionResult \
granted_asset_ids=[00000000] failed_asset_ids={}>
            ```
        """

        from .experience import Experience
        from .group import Group, GroupRole
        from .user import User

        if isinstance(subject, AssetPermissionSubject):
            subject_type = subject.type.name
        elif isinstance(subject, Experience):
            subject_type = AssetPermissionSubjectType.Experience.name
        elif isinstance(subject, User):
            subject_type = AssetPermissionSubjectType.User.name
        elif isinstance(subject, Group):
            subject_type = AssetPermissionSubjectType.Group.name
        elif isinstance(subject, GroupRole):
            subject_type = AssetPermissionSubjectType.GroupRole.name
        else:
            raise ValueError("Invalid subject type provided.")

        if subject_type == AssetPermissionSubjectType.Experience.name:
            subject_type = "Universe"
        elif subject_type == AssetPermissionSubjectType.GroupRole.name:
            subject_type = "GroupRoleset"

        requests = []

        for asset in assets:
            if isinstance(asset, int):
                requests.append({"assetId": asset})
            elif isinstance(asset, Asset):
                requests.append({"assetId": asset.id})
            elif isinstance(asset, AssetPermissionRequest):
                requests.append(
                    {
                        "assetId": asset.asset_id,
                        "grantDependencies": asset.grant_dependencies,
                        "versionNumber": asset.version_number,
                    }
                )
            else:
                raise ValueError("Invalid asset type provided.")

        _, data, _ = await send_request(
            "PATCH",
            "asset-permissions-api/v1/assets/permissions",
            expected_status=[200],
            authorization=self.__api_key,
            json={
                "subjectType": subject_type,
                "subjectId": subject.id,
                "action": action.name,
                "requests": requests,
            },
        )

        return AssetPermissionResult(data)


class ToolboxAssetSubtype(Enum):
    """
    Enum denoting the subtype of a model in the toolbox.

    Attributes:
        Unknown (0): An unknown or invalid model subtype.
        Ad (1): A model is an ad subtype relating to immersive advertising.
        MaterialPack (2): A model is a material pack subtype.
        Package (3): A model is a package meaning it supports dynamic \
        auto updating in experiences.
    """

    Unknown = 0
    Ad = 1
    MaterialPack = 2
    Package = 3


MODEL_SUBTYPE_ENUMS = {
    "Ad": ToolboxAssetSubtype.Ad,
    "MaterialPack": ToolboxAssetSubtype.MaterialPack,
    "Package": ToolboxAssetSubtype.Package,
}

TOOLBOX_SOCIAL_LINK_TYPE = {
    "facebook": 1,
    "twitter": 2,
    "youtube": 3,
    "twitch": 4,
    "discord": 5,
    "github": 6,
    "guilded": 7,
    "roblox": 8,
    "devForum": 9,
    "tryAsset": 10,
}


class ToolboxAsset:
    """
    Represents an asset in the toolbox.

    Attributes:
        creator (Union[Creator, User, Group]): The creator of the asset.
        asset_id (int): The ID of the asset.
        asset_type (AssetType): The type of the asset.
        name (str): The name of the asset.
        description (str): The description of the asset.
        category_path (Optional[str]): The category path of the asset as \
        returned by Roblox. For instance, `3d__props-and-decor`.
        preview_image_asset_ids (Optional[list[int]]): A list of asset IDs for \
        the preview images of the asset.
        preview_video_asset_ids (Optional[list[int]]): A list of asset IDs for \
        the preview videos of the asset.
        created_at (datetime): When the asset was created.
        updated_at (datetime): When the asset was last updated.
        asset (Asset): The asset object. `moderation_result`, `is_archived`, \
        `icon_asset_id`, and revision information is not present. Allows \
        using asset APIs such as asset delivery.
        creator_store_product (CreatorStoreProduct): The creator store product \
        associated with this asset. Contains pricing information. `published`, \
        `restrictions`, `base_price` are not present in the toolbox response.
        try_place_id (Optional[int]): The place ID set for the asset's 'Try in Roblox' button.
        votes_shown (bool): Whether votes are shown for the asset.
        up_votes (int): The number of up votes for the asset.
        down_votes (int): The number of down votes for the asset.
        can_vote (bool): Whether the authenticated user can vote for the asset.
        has_voted (bool): Whether the authenticated user has voted for the asset.
        total_vote_count (int): The total number of votes for the asset.
        up_vote_percentage (int): The percentage of up votes for the asset between 0 and 100.
        subtypes (list[ToolboxAssetSubtype]): For models, the subtypes of the model.
        has_scripts (bool): Whether the asset contains scripts.
        script_count (int): The number of scripts in the model.
        triangle_count (int): For models, the number of triangles in the model.
        vertex_count (int): For models, the number of vertices in the model.
        mesh_part_count (int): For models, the number of mesh parts in the model.
        animation_count (int): For models, the number of animations in the model.
        decal_count (int): For models, the number of decals in the model.
        audio_count (int): For models, the number of audios in the model.
        tool_count (int): For models, the number of tools in the model.
        duration_seconds (Optional[int]): For audio assets, the duration of \
        the audio in seconds.
        artist (Optional[str]): For audio assets, the artist of the audio.
        album (Optional[str]): For audio assets, the album of the audio.
        title (Optional[str]): For audio assets, the title of the audio.
        genre (Optional[str]): For audio assets, the genre of the audio.
        category (Optional[str]): For sound effects, the category of the sound effect.
        subcategory (Optional[str]): For sound effects, the subcategory of the sound effect.
        mesh_asset_id (Optional[int]): For mesh parts, the asset ID of the mesh.
        texture_asset_id (Optional[int]): For mesh parts, the asset ID of the texture.
        facebook_social_link (Optional[AssetSocialLink]): The Facebook social link of the asset.
        twitter_social_link (Optional[AssetSocialLink]): The Twitter social link of the asset.
        youtube_social_link (Optional[AssetSocialLink]): The YouTube social link of the asset.
        twitch_social_link (Optional[AssetSocialLink]): The Twitch social link of the asset.
        discord_social_link (Optional[AssetSocialLink]): The Discord social link of the asset.
        github_social_link (Optional[AssetSocialLink]): The GitHub social link of the asset.
        guilded_social_link (Optional[AssetSocialLink]): The Guilded social link of the asset.
        roblox_social_link (Optional[AssetSocialLink]): The Roblox social link of the asset.
        devforum_social_link (Optional[AssetSocialLink]): The DevForum social link of the asset.
    """

    def __init__(self, data, creator, api_key):
        self.__api_key = api_key

        self.votes_shown: bool = data.get("voting", {}).get("showVotes")
        self.up_votes: int = data.get("voting", {}).get("upVotes")
        self.down_votes: int = data.get("voting", {}).get("downVotes")
        self.can_vote: bool = data.get("voting", {}).get("canVote")
        self.has_voted: bool = data.get("voting", {}).get("hasVoted")
        self.total_vote_count: int = data.get("voting", {}).get("voteCount")
        self.up_vote_percentage: int = data.get("voting", {}).get(
            "upVotePercent"
        )

        if creatorid := data.get("creator", {}).get("userId"):
            data_creator = User(creatorid, self.__api_key)
            data_creator.username = data.get("creator", {}).get("name")
            data_creator.verified = data.get("creator", {}).get("verified")
        elif creatorid := data.get("creator", {}).get("groupId"):
            data_creator = Group(
                creatorid,
                self.__api_key,
            )
            data_creator.name = data.get("creator", {}).get("name")
            data_creator.verified = data.get("creator", {}).get("verified")
        else:
            data_creator = None

        from .group import Group
        from .user import User

        if (not data_creator and creator) or (
            type(creator) in (Creator, User, Group)
            and data_creator.id == creator.id
            and type(data_creator) == type(creator)
        ):
            if (
                data_creator
                and isinstance(creator, (User, Group))
                and not creator.verified
            ):
                creator.verified = data_creator.verified
            if (
                data_creator
                and isinstance(creator, Group)
                and not creator.name
            ):
                creator.name = data_creator.name
            if (
                data_creator
                and isinstance(creator, User)
                and not creator.username
            ):
                creator.username = data_creator.username

            self.creator: Union[Creator, User, Group] = creator
        else:
            self.creator: Union[Creator, User, Group] = data_creator

        self.asset_id: int = (
            int(data["asset"]["id"])
            if data.get("asset", {}).get("id")
            else None
        )
        self.asset_type: AssetType = LEGACY_ASSET_TYPE_ENUMS.get(
            data.get("asset", {}).get("assetTypeId"), AssetType.Unknown
        )

        self.name: str = data.get("asset", {}).get("name")
        self.description: str = data.get("asset", {}).get("description")
        self.category_path: Optional[str] = data.get("asset", {}).get(
            "categoryPath"
        )

        self.preview_image_asset_ids: list[int] = (
            data.get("asset", {})
            .get("previewAssets", {})
            .get("imagePreviewAssets", [])
        )
        self.preview_video_asset_ids: list[int] = (
            data.get("asset", {})
            .get("previewAssets", {})
            .get("videoPreviewAssets", [])
        )

        self.created_at: datetime = (
            parser.parse(data["asset"]["createTime"])
            if data.get("asset", {}).get("createTime")
            else None
        )
        self.updated_at: datetime = (
            parser.parse(data["asset"]["updateTime"])
            if data.get("asset", {}).get("updateTime")
            else None
        )

        creator_store_product = data.get("creatorStoreProduct", {})

        if type(self.creator) == User:
            creator_store_product["userSeller"] = self.creator.id
        elif type(self.creator) == Group:
            creator_store_product["groupSeller"] = self.creator.id

        creator_store_key = CREATOR_STORE_ASSET_ID_KEYS.get(
            self.asset_type, "assetId"
        )
        creator_store_product[creator_store_key] = self.asset_id

        self.creator_store_product: CreatorStoreProduct = CreatorStoreProduct(
            creator_store_product, self.__api_key
        )

        self.creator_store_product.creator = self.creator

        self.subtypes: list[ToolboxAssetSubtype] = []

        for subtype in data.get("asset", {}).get("subTypes", []):
            self.subtypes.append(
                MODEL_SUBTYPE_ENUMS.get(subtype, ToolboxAssetSubtype.Unknown)
            )

        self.has_scripts: bool = data.get("asset", {}).get("hasScripts")
        self.script_count: int = data.get("asset", {}).get("scriptCount")
        self.triangle_count: int = (
            data.get("asset", {}).get("objectMeshSummary", {}).get("triangles")
        )
        self.vertex_count: int = (
            data.get("asset", {}).get("objectMeshSummary", {}).get("vertices")
        )
        self.mesh_part_count: int = (
            data.get("asset", {}).get("instanceCounts", {}).get("meshPart")
        )
        self.animation_count: int = (
            data.get("asset", {}).get("instanceCounts", {}).get("animation")
        )
        self.decal_count: int = (
            data.get("asset", {}).get("instanceCounts", {}).get("decal")
        )
        self.audio_count: int = (
            data.get("asset", {}).get("instanceCounts", {}).get("audio")
        )
        self.tool_count: int = (
            data.get("asset", {}).get("instanceCounts", {}).get("tool")
        )

        self.duration_seconds: Optional[int] = data.get("asset", {}).get(
            "durationSeconds"
        )

        self.artist: Optional[str] = data.get("asset", {}).get("artist")
        self.album: Optional[str] = data.get("asset", {}).get("album")
        self.title: Optional[str] = data.get("asset", {}).get("title")
        self.genre: Optional[str] = data.get("asset", {}).get("genre")

        self.category: Optional[str] = data.get("asset", {}).get("category")
        self.subcategory: Optional[str] = data.get("asset", {}).get(
            "subcategory"
        )

        self.mesh_asset_id: Optional[int] = data.get("asset", {}).get("meshId")
        self.texture_asset_id: Optional[int] = data.get("asset", {}).get(
            "textureId"
        )

        social_links = {}

        for social_link in data.get("asset", {}).get("socialLinks", []):
            link_type = TOOLBOX_SOCIAL_LINK_TYPE.get(social_link.get("type"))
            social_links[link_type] = AssetSocialLink(
                title=social_link.get("title"),
                uri=social_link.get("uri"),
            )

        self.facebook_social_link: Optional[AssetSocialLink] = (
            social_links.get(TOOLBOX_SOCIAL_LINK_TYPE.get("facebook"))
        )
        self.twitter_social_link: Optional[AssetSocialLink] = social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("twitter")
        )
        self.youtube_social_link: Optional[AssetSocialLink] = social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("youtube")
        )
        self.twitch_social_link: Optional[AssetSocialLink] = social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("twitch")
        )
        self.discord_social_link: Optional[AssetSocialLink] = social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("discord")
        )
        self.github_social_link: Optional[AssetSocialLink] = social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("github")
        )
        self.roblox_social_link: Optional[AssetSocialLink] = social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("roblox")
        )
        self.guilded_social_link: Optional[AssetSocialLink] = social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("guilded")
        )
        self.devforum_social_link: Optional[AssetSocialLink] = (
            social_links.get(TOOLBOX_SOCIAL_LINK_TYPE.get("devForum"))
        )

        self.try_place_id: Optional[int] = None

        if try_place_id := social_links.get(
            TOOLBOX_SOCIAL_LINK_TYPE.get("tryAsset")
        ):
            try:
                self.try_place_id = int(try_place_id)
            except (ValueError, IndexError):
                pass

        estimated_asset_data = {
            "assetId": self.asset_id,
            "displayName": self.name,
            "description": self.description,
            "creationContext": {
                "creator": {
                    (
                        "userId"
                        if isinstance(self.creator, User)
                        else (
                            "groupId"
                            if isinstance(self.creator, Group)
                            else "creatorId"
                        )
                    ): self.creator.id,
                }
            },
            "assetType": self.asset_type.name,
        }

        self.asset: Asset = Asset(
            estimated_asset_data, creator=self.creator, api_key=self.__api_key
        )

        self.asset.facebook_social_link = self.facebook_social_link
        self.asset.twitter_social_link = self.twitter_social_link
        self.asset.youtube_social_link = self.youtube_social_link
        self.asset.twitch_social_link = self.twitch_social_link
        self.asset.discord_social_link = self.discord_social_link
        self.asset.github_social_link = self.github_social_link
        self.asset.guilded_social_link = self.guilded_social_link
        self.asset.roblox_social_link = self.roblox_social_link
        self.asset.devforum_social_link = self.devforum_social_link
        self.asset.try_place_id = self.try_place_id

        self.asset.preview_asset_ids = (self.preview_image_asset_ids or []) + (
            self.preview_video_asset_ids or []
        )

    def __repr__(self):
        return f"<rblxopencloud.ToolboxAsset asset_id={self.asset_id}>"


class ToolboxSearchSortCategory(Enum):
    """
    Enum denoting the category to sort by when searching the toolbox.

    Attributes:
        Unknown (0): An unknown or invalid sort category. Not used.
        Relevance (1): Sort by relevance to the search query. This is the default sort category.
        Trending (2): Sort by how trending the asset is on Roblox.
        Top (3): Sort by the top rated assets on Roblox.
        AudioDuration (4): For audio assets, sort by the duration of the audio.
        CreateTime (5): Sort by when the asset was created.
        UpdateTime (6): Sort by when the asset was last updated.
    """

    Unknown = 0
    Relevance = 1
    Trending = 2
    Top = 3
    AudioDuration = 4
    CreateTime = 5
    UpdateTime = 6


class InstanceType(Enum):
    """
    Enum denoting instance type. Used for filtering in the toolbox search.

    Attributes:
        Unknown (0): An unknown or invalid instance type. Not used.
        Script (1): Represents a script instance type.
        MeshPart (2): Represents a mesh part instance type.
        Decal (3): Represents a decal instance type.
        Animation (4): Represents an animation instance type.
        Audio (5): Represents an audio instance type.
        Tool (6): Represents a tool instance type.
    """

    Unknown = 0
    Script = 1
    MeshPart = 2
    Decal = 3
    Animation = 4
    Audio = 5
    Tool = 6


class MusicChartType(Enum):
    """
    Enum denoting music chart type. Used for filtering in the toolbox search.

    Attributes:
        Unknown (0): An unknown or invalid music chart type. Not used.
        Current (1): Represents the current music chart on Roblox.
        Week (2): Represents the music chart for the past week on Roblox.
        Month (3): Represents the music chart for the past month on Roblox.
        Year (4): Represents the music chart for the past year on Roblox.
    """

    Unknown = 0
    Current = 1
    Week = 2
    Month = 3
    Year = 4


class ToolboxSearchContext:
    """
    Data class containing meta information about search results in the toolbox.

    Attributes:
        total_results (int): The total number of results for the search query.
        filtered_keyword (str): The keyword that was used for the search after \
        filtering by Roblox.
        applied_facets (list[str]): The list of facet filters that were applied to the search.
        available_facets (list[str]): The available facet filters that can be applied to the search.
    """

    def __init__(self, data):
        self.total_results: int = data.get("totalResults")
        self.filtered_keyword: str = data.get("filteredKeyword")
        self.applied_facets: list[str] = data.get("queryFacets", {}).get(
            "appliedFacets", []
        )
        self.available_facets: list[str] = data.get("queryFacets", {}).get(
            "availableFacets", []
        )

    def __repr__(self):
        return f"<rblxopencloud.ToolboxSearchContext total_results={self.total_results} filtered_keyword={self.filtered_keyword}>"
