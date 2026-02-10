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

from datetime import datetime
from enum import Enum
from typing import Optional, Union

from dateutil import parser

from .creator import (
    Asset,
    AssetType,
    Creator,
    CreatorStoreProduct,
    LEGACY_ASSET_TYPE_ENUMS,
)
from .group import Group
from .user import User


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


class ModelSubtypeEnum(Enum):
    Unknown = 0
    Ad = 1
    MaterialPack = 2
    Package = 3


MODEL_SUBTYPE_ENUMS = {
    "Ad": ModelSubtypeEnum.Ad,
    "MaterialPack": ModelSubtypeEnum.MaterialPack,
    "Package": ModelSubtypeEnum.Package,
}


class ToolboxAsset:

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

        # TODO: socialLinks, previewAssets

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

        self.model_subtypes: list[ModelSubtypeEnum] = []

        for subtype in data.get("asset", {}).get("subTypes", []):
            self.model_subtypes.append(
                MODEL_SUBTYPE_ENUMS.get(subtype, ModelSubtypeEnum.Unknown)
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

        {
            # "voting": {
            #     "showVotes": True,
            #     "upVotes": 0,
            #     "downVotes": 0,
            #     "canVote": True,
            #     "hasVoted": False,
            #     "voteCount": 0,
            #     "upVotePercent": 0,
            # },
            # "creator": {
            #     "creator": "user/287113233",
            #     "userId": 287113233,
            #     "name": "TreeBen77",
            #     "verified": True,
            # },
            # "creatorStoreProduct": {
            #     "purchasePrice": {
            #         "currencyCode": "USD",
            #         "quantity": {"significand": 0, "exponent": 0},
            #     },
            #     "purchasable": True,
            # },
            "asset": {
                "subTypes": [],
                # "hasScripts": False,
                # "scriptCount": 0,
                # "objectMeshSummary": {"triangles": 552, "vertices": 912},
                # "instanceCounts": {
                #     "script": 0,
                #     "meshPart": 1,
                #     "animation": 0,
                #     "decal": 0,
                #     "audio": 0,
                #     "tool": 0,
                # },
                # "id": 14903722621,
                # "name": "firehydrant",
                # "description": "A simple fire hydrant to keep the flames away!",
                # "assetTypeId": 10,
                "socialLinks": [],
                "previewAssets": {
                    "imagePreviewAssets": [],
                    "videoPreviewAssets": [],
                },
                # "createTime": "2023-09-28T08:23:05.447Z",
                # "updateTime": "2025-12-11T11:41:07.2773289Z",
            },
        }

    def __repr__(self):
        return f"<rblxopencloud.ToolBoxAsset asset_id={self.asset_id}>"


# class ToolboxModelAsset(ToolboxAsset):
