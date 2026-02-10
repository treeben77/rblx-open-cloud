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

from base64 import urlsafe_b64encode
import datetime
from enum import Enum
import sys
from typing import Any, AsyncGenerator, Optional, TypedDict

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

from dateutil import parser

from .creator import Creator
from .http import iterate_request, send_request
from .user import User

__all__ = (
    "Group",
    "GroupMember",
    "GroupRole",
    "GroupRolePermissions",
    "GroupShout",
    "GroupJoinRequest",
    "GroupAuditLogEntry",
    "GroupAuditLogEntryDescription",
    "GroupAuditLogEntryActionType",
)


class GroupShout:
    """
    Represents a group shout.

    Attributes:
        content (str): The message content of the shout.
        user (User): The user who posted it.
        created_at (datetime.datetime): The timestamp the group shout was \
        posted.
        first_created_at (datetime.datetime): The timestamp the first group \
        shout was posted in this group.
    """

    def __init__(self, shout, api_key=None) -> None:
        self.content: str = shout["content"]
        self.user: User = User(int(shout["poster"].split("/")[1]), api_key)
        self.created_at: datetime.datetime = (
            parser.parse(shout["updateTime"])
            if shout.get("updateTime")
            else None
        )
        self.first_created_at: datetime.datetime = (
            parser.parse(shout["createTime"])
            if shout.get("createTime")
            else None
        )

    def __repr__(self) -> str:
        return f'<rblxopencloud.GroupShout content="{self.content}">'


class GroupRolePermissions:
    """
    Represents a role's permissions inside of a group.

    Attributes:
        view_wall_posts (bool): View group wall
        create_wall_posts (bool): Post on group wall
        delete_wall_posts (bool): Delete group wall posts
        view_group_shout (bool): View group shout
        create_group_shout (bool): Post group shout
        change_member_ranks (bool): Manage lower-ranked member ranks
        accept_join_requests (bool): Accept join requests
        exile_members (bool): Kick lower-ranked members
        manage_relationships (bool): Manage allies and enemies
        view_audit_log (bool): View audit log
        spend_group_funds (bool): Spend group funds
        advertise_group (bool): Advertise the group
        create_avatar_items (bool): Create avatar items
        manage_avatar_items (bool): Configure avatar items
        manage_experiences (bool): Create and edit group experiences
        view_experience_analytics (bool): View group experience analytics
        create_api_keys (bool): Create group API keys
        manage_api_keys (bool): Administer all group API keys
    """

    def __init__(self, permissions) -> None:
        self.view_wall_posts: bool = permissions["viewWallPosts"]
        self.create_wall_posts: bool = permissions["createWallPosts"]
        self.delete_wall_posts: bool = permissions["deleteWallPosts"]
        self.view_group_shout: bool = permissions["viewGroupShout"]
        self.create_group_shout: bool = permissions["createGroupShout"]
        self.change_member_ranks: bool = permissions["changeRank"]
        self.accept_join_requests: bool = permissions["acceptRequests"]
        self.exile_members: bool = permissions["exileMembers"]
        self.manage_relationships: bool = permissions["manageRelationships"]
        self.view_audit_log: bool = permissions["viewAuditLog"]
        self.spend_group_funds: bool = permissions["spendGroupFunds"]
        self.advertise_group: bool = permissions["advertiseGroup"]
        self.create_avatar_items: bool = permissions["createAvatarItems"]
        self.manage_avatar_items: bool = permissions["manageAvatarItems"]
        self.manage_experiences: bool = permissions["manageGroupUniverses"]
        self.view_experience_analytics: bool = permissions[
            "viewUniverseAnalytics"
        ]
        self.create_api_keys: bool = permissions["createApiKeys"]
        self.manage_api_keys: bool = permissions["manageApiKeys"]

    def __repr__(self) -> str:
        return "<rblxopencloud.GroupRolePermissions>"


class GroupRole:
    """
    Represents a role inside of a group.

    Attributes:
        id (int): The ID of the role.
        name (str): The name of the role.
        rank (int): The rank number of this role (0-255).
        description (Optional[str]): The description of the rank. Will be \
        `None` if the authorizing user is the owner.
        member_count (Optional[int]): The number of members in this rank. \
        Will be `None` if it is the guest rank.
        permissions (Optional[GroupRolePermissions]): The permissions this \
        rank has. Will be `None` unless the authorizing user owns the group, \
        the authorizing user's rank in the group is this rank, or it is the \
        guest rank.
    """

    def __init__(self, role) -> None:
        self.id: int = int(role["id"])
        self.name: str = role["displayName"]
        self.rank: int = role["rank"]
        self.description: Optional[str] = role.get("description")
        self.member_count: Optional[int] = role.get("memberCount", None)
        self.permissions: Optional[GroupRolePermissions] = (
            GroupRolePermissions(role["permissions"])
            if role.get("permissions")
            else None
        )

    def __repr__(self) -> str:
        return f'<rblxopencloud.GroupRole id={self.id} name="{self.name}" \
rank={self.rank})>'


class GroupMember(User):
    """
    Represents a user inside of a group.

    Attributes:
        id (int): The user ID of the group member.
        role_id (int): The role ID assigned to the group member.
        group (Group): The group this group member is associated with.
        joined_at (Optional[datetime.datetime]): The time the user joined the group.
        updated_at (Optional[datetime.datetime]): The time the user was last update in \
        the group (Such as rank change).
    """

    def __init__(self, member, api_key, group=None) -> None:
        self.id: int = int(member["user"].split("/")[1])
        self.role_id: int = int(member["role"].split("/")[-1])
        self.group: Group = (
            group
            if group
            else Group(int(member["role"].split("/")[1]), api_key)
        )
        self.joined_at: datetime.datetime = (
            parser.parse(member["createTime"])
            if member.get("createTime")
            else None
        )
        self.updated_at: datetime.datetime = (
            parser.parse(member["updateTime"])
            if member.get("updateTime")
            else None
        )
        super().__init__(self.id, api_key)

    def __repr__(self) -> str:
        return f"<rblxopencloud.GroupMember id={self.id} group={self.group}>"

    async def fetch_role(self, skip_cache: bool = False) -> GroupRole:
        """
        Fetches and returns the user's role info (rank, role name, etc). The \
        roles are cached therefore it runs faster. Shortcut for \
        [`Group.fetch_role`][rblxopencloud.Group.fetch_role]

        Args:
            skip_cache (bool): Wether to forcably refetch role information.

        Returns:
            The [`GroupRole`][rblxopencloud.GroupRole] for the user's current \
            rank.
        """

        return await self.group.fetch_role(self.role_id, skip_cache=skip_cache)

    async def update(self, role_id: int = None):
        """
        Updates the member with the requested information and updates the \
        member object attributes.

        Args:
            role_id: If provided, updates the member's group role to the \
                provided [`GroupRole.id`][rblxopencloud.GroupRole.id]. This \
                role must not be Owner or Guest and must be lower than the \
                authorizing user's rank.

        Returns:
            The updated [`GroupMember`][rblxopencloud.GroupMember] object.
        """

        member = await self.group.update_member(self.id, role_id)

        self.role_id: int = member.role_id
        self.updated_at: datetime.datetime = member.updated_at

        return self


class GroupJoinRequest(User):
    """
    Represents a user requesting to join a group.

    Attributes:
        id (int): The user's ID.
        group (Group): The group this object is related to.
        requested_at (datetime.datetime): The time when the user requested to \
        join the Group.
    
    !!! tip
        This class bases [`User`][rblxopencloud.User], so all methods of it \
        can be used from this object, such as \
        [`User.list_inventory`][rblxopencloud.User.list_inventory].
    """

    def __init__(self, member, api_key, group=None) -> None:
        self.id: int = int(member["user"].split("/")[1])
        self.group: Group = group
        self.requested_at: datetime.datetime = parser.parse(
            member["createTime"]
        )

        super().__init__(self.id, api_key)

    def __repr__(self) -> str:
        return f"<rblxopencloud.GroupJoinRequest id={self.id} \
group={self.group}>"

    def accept(self):
        """
        Accepts the join request for this user. Shortcut for \
        [`Group.accept_join_request`][rblxopencloud.Group.accept_join_request].
        """
        return self.group.accept_join_request(self.id)

    def decline(self):
        """
        Declines the join request for this user. Shortcut for \
        [`Group.decline_join_request`\
        ][rblxopencloud.Group.decline_join_request].
        """
        return self.group.decline_join_request(self.id)


class GroupAuditLogEntryActionType(Enum):
    """
    Enum denoting the action type of a group audit log entry.

    Attributes:
        Unknown (0): An unknown action type.
        DeletePost (1):
        RemoveMember (2):
        AcceptJoinRequest (3):
        DeclineJoinRequest (4):
        PostStatus (5):
        ChangeRank (6):
        BuyAd (7):
        SendAllyRequest (8):
        CreateEnemy (9):
        AcceptAllyRequest (10):
        DeclineAllyRequest (11):
        DeleteAlly (12):
        DeleteEnemy (13):
        AddGroupPlace (14):
        RemoveGroupPlace (15):
        CreateItems (16):
        ConfigureItems (17):
        SpendGroupFunds (18):
        ChangeOwner (19):
        Delete (20):
        AdjustCurrencyAmounts (21):
        Abandon (22):
        Claim (23):
        Rename (24):
        ChangeDescription (25):
        InviteToClan (26):
        KickFromClan (27):
        CancelClanInvite (28):
        BuyClan (29):
        CreateGroupAsset (30):
        UpdateGroupAsset (31):
        ConfigureGroupAsset (32):
        RevertGroupAsset (33):
        CreateGroupDeveloperProduct (34):
        ConfigureGroupGame (35):
        CreateGroupDeveloperSubscriptionProduct (36):
        Lock (37):
        Unlock (38):
        CreateGamePass (39):
        CreateBadge (40):
        ConfigureBadge (41):
        SavePlace (42):
        PublishPlace (43):
        UpdateRolesetRank (44):
        UpdateRolesetData (45):
        BanMember (46):
        UnbanMember (47):
        CreateForumCategory (48):
        UpdateForumCategory (49):
        ArchiveForumCategory (50):
        DeleteForumCategory (51):
        DeleteForumPost (52):
        DeleteForumComment (53):
        PinForumPost (54):
        UnpinForumPost (55):
        LockForumPost (56):
        UnlockForumPost (57):
        CreateRoleset (58):
        DeleteRoleset (59):
        CreateCommerceProduct (60):
        SetCommerceProductActive (61):
        ArchiveCommerceProduct (62):
        AcceptCommerceProductBundlingFee (63):
        SetCommerceProductInactive (64):
        ConnectMerchant (65):
        DisconnectMerchant (66):
        JoinGroup (67):
        LeaveGroup (68):
        UpdateGroupIcon (69):
        UpdateGroupCoverPhoto (70):

    """

    Unknown = 0
    DeletePost = 1
    RemoveMember = 2
    AcceptJoinRequest = 3
    DeclineJoinRequest = 4
    PostStatus = 5
    ChangeRank = 6
    BuyAd = 7
    SendAllyRequest = 8
    CreateEnemy = 9
    AcceptAllyRequest = 10
    DeclineAllyRequest = 11
    DeleteAlly = 12
    DeleteEnemy = 13
    AddGroupPlace = 14
    RemoveGroupPlace = 15
    CreateItems = 16
    ConfigureItems = 17
    SpendGroupFunds = 18
    ChangeOwner = 19
    Delete = 20
    AdjustCurrencyAmounts = 21
    Abandon = 22
    Claim = 23
    Rename = 24
    ChangeDescription = 25
    InviteToClan = 26
    KickFromClan = 27
    CancelClanInvite = 28
    BuyClan = 29
    CreateGroupAsset = 30
    UpdateGroupAsset = 31
    ConfigureGroupAsset = 32
    RevertGroupAsset = 33
    CreateGroupDeveloperProduct = 34
    ConfigureGroupGame = 35
    CreateGroupDeveloperSubscriptionProduct = 36
    Lock = 37
    Unlock = 38
    CreateGamePass = 39
    CreateBadge = 40
    ConfigureBadge = 41
    SavePlace = 42
    PublishPlace = 43
    UpdateRolesetRank = 44
    UpdateRolesetData = 45
    BanMember = 46
    UnbanMember = 47
    CreateForumCategory = 48
    UpdateForumCategory = 49
    ArchiveForumCategory = 50
    DeleteForumCategory = 51
    DeleteForumPost = 52
    DeleteForumComment = 53
    PinForumPost = 54
    UnpinForumPost = 55
    LockForumPost = 56
    UnlockForumPost = 57
    CreateRoleset = 58
    DeleteRoleset = 59
    CreateCommerceProduct = 60
    SetCommerceProductActive = 61
    ArchiveCommerceProduct = 62
    AcceptCommerceProductBundlingFee = 63
    SetCommerceProductInactive = 64
    ConnectMerchant = 65
    DisconnectMerchant = 66
    JoinGroup = 67
    LeaveGroup = 68
    UpdateGroupIcon = 69
    UpdateGroupCoverPhoto = 70


class GroupAuditLogEntryDescription(TypedDict):
    """
    Represents the description of a group audit log entry returned by \
    Roblox. It contains information regarding the change that was made.
    
    !!! note:
        This is a TypedDict, meaning the returned type is a dictionary. The \
        attributed documented below are keys, not class attributes.Note that \
        not all fields are present for every entry and that some fields \
        may not be documented here. The following is a best effort based on \
        available documentation.

    Attributes:
        AssetType (NotRequired[str]):
        AssetId (NotRequired[int]):
        AssetName (NotRequired[str]):
        VersionNumber (NotRequired[int]):
        RevertVersionNumber (NotRequired[Optional[int]]):
        TargetId (NotRequired[int]):
        TargetName (NotRequired[str]):
        TargetDisplayName (NotRequired[str]):
        NewRoleSetId (NotRequired[int]):
        OldRoleSetId (NotRequired[int]):
        NewRoleSetName (NotRequired[str]):
        OldRoleSetName (NotRequired[str]):
        Actions (NotRequired[Optional[list[int]]]):
        Type (NotRequired[Optional[int]]):
        UniverseId (NotRequired[Optional[int]]):
        UniverseName (NotRequired[str]):
        NewDescription (NotRequired[str]):
        NewName (NotRequired[str]):
        OldDescription (NotRequired[str]):
        OldName (NotRequired[str]):
        RoleSetId (NotRequired[int]):
        RoleSetName (NotRequired[str]):
        PostDesc (NotRequired[str]):
        BadgeId (NotRequired[int]):
        BadgeName (NotRequired[str]):
        Amount (NotRequired[int]):
        CurrencyTypeId (NotRequired[int]):
        ItemDescription (NotRequired[str]):
        CurrencyTypeName (NotRequired[str]):
        NewRank (NotRequired[int]):
        OldRank (NotRequired[int]):
        Text (NotRequired[str]):
        GamePassId (NotRequired[int]):
        PlaceId (NotRequired[int]):
        GamePassName (NotRequired[str]):
        PlaceName (NotRequired[str]):
        TargetGroupId (NotRequired[int]):
        TargetGroupName (NotRequired[str]):
    """

    AssetType: NotRequired[str]
    AssetId: NotRequired[int]
    AssetName: NotRequired[str]
    VersionNumber: NotRequired[int]
    RevertVersionNumber: NotRequired[Optional[int]]
    TargetId: NotRequired[int]
    TargetName: NotRequired[str]
    TargetDisplayName: NotRequired[str]
    NewRoleSetId: NotRequired[int]
    OldRoleSetId: NotRequired[int]
    NewRoleSetName: NotRequired[str]
    OldRoleSetName: NotRequired[str]
    Actions: NotRequired[Optional[list[int]]]
    Type: NotRequired[Optional[int]]
    UniverseId: NotRequired[Optional[int]]
    UniverseName: NotRequired[str]
    NewDescription: NotRequired[str]
    NewName: NotRequired[str]
    OldDescription: NotRequired[str]
    OldName: NotRequired[str]
    RoleSetId: NotRequired[int]
    RoleSetName: NotRequired[str]
    PostDesc: NotRequired[str]
    BadgeId: NotRequired[int]
    BadgeName: NotRequired[str]
    Amount: NotRequired[int]
    CurrencyTypeId: NotRequired[int]
    ItemDescription: NotRequired[str]
    CurrencyTypeName: NotRequired[str]
    NewRank: NotRequired[int]
    OldRank: NotRequired[int]
    Text: NotRequired[str]
    GamePassId: NotRequired[int]
    PlaceId: NotRequired[int]
    GamePassName: NotRequired[str]
    PlaceName: NotRequired[str]
    TargetGroupId: NotRequired[int]
    TargetGroupName: NotRequired[str]


class GroupAuditLogEntry:
    """
    Represents an entry in a group's audit log.

    Attributes:
        member: The member who performed the action logged in this entry. The \
        `username`, `display_name`, `role_id` and `verified` attributes are \
        resolved.
        action_type: The type of action performed in this entry.
        description: A dictionary containing raw information regarding the \
        action, such as the target user, experience, asset, rank, text, etc.
        created_at: The time when the action logged was performed.
    """

    def __init__(self, entry, group: "Group", api_key) -> None:

        self.member: GroupMember = GroupMember(
            {
                "user": f"users/{entry['actor']['user']['userId']}",
                "role": f"groups/{entry['actor']['role']['id']}",
            },
            api_key,
            group,
        )
        self.member.username = entry["actor"]["user"].get("username")
        self.member.display_name = entry["actor"]["user"].get("displayName")
        self.member.verified = entry["actor"]["user"].get("hasVerifiedBadge")

        if not group._Group__role_cache.get(int(entry["actor"]["role"]["id"])):
            group._Group__role_cache[int(entry["actor"]["role"]["id"])] = {
                "id": entry["actor"]["role"]["id"],
                "displayName": entry["actor"]["role"].get("name"),
                "rank": entry["actor"]["role"].get("rank"),
            }

        self.action_type: GroupAuditLogEntryActionType = (
            GroupAuditLogEntryActionType._member_map_.get(
                entry.get("actionType", "Unknown").replace(" ", ""),
                GroupAuditLogEntryActionType.Unknown,
            )
        )

        self.description: GroupAuditLogEntryDescription = entry.get(
            "description", {}
        )

        self.created_at: Optional[datetime.datetime] = (
            parser.parse(entry["created"]) if entry.get("created") else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.GroupAuditLogEntry action_type={self.action_type} created_at={self.created_at}>"


class Group(Creator):
    """
    Represents a group on Roblox. It can be used for both uploading assets, \
    and accessing group information.
    
    Args:
        id: The group's ID.
        api_key: Your API key created from \
        [Creator Dashboard](https://create.roblox.com/credentials) with \
        access to this group.
    
    Attributes:
        id (int): The group's ID.
        name (Optional[str]): The group's name.
        description (Optional[str]): The group's description.
        created_at (Optional[datetime.datetime]): When the group was created.
        updated_at (Optional[datetime.datetime]): When the group was last \
        updated.
        owner (Optional[User]): The group's group's owner.
        member_count (Optional[int]): The number of members in the group.
        public_entry (Optional[bool]): Wether you can join without being \
        approved.
        locked (Optional[bool]): Wether the group has been locked by Roblox \
        moderation.
        verified (Optional[bool]): Wether the group has a verified badge.
    """

    def __init__(self, id: int, api_key: str) -> None:
        self.id: int = id
        self.__api_key = api_key

        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.created_at: Optional[datetime.datetime] = None
        self.updated_at: Optional[datetime.datetime] = None
        self.owner: Optional[User] = None
        self.member_count: Optional[int] = None
        self.public_entry: Optional[bool] = None
        self.locked: Optional[bool] = None
        self.verified: Optional[bool] = None

        self.__role_cache = {}

        super().__init__(id, api_key, "Group")

    def __repr__(self) -> str:
        return f"<rblxopencloud.Group id={self.id}>"

    async def fetch_info(self) -> "Group":
        """
        Updates the empty parameters in this Group object and returns it self \
        with the group info.
        """

        _, data, _ = await send_request(
            "GET",
            f"/groups/{self.id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        self.name = data["displayName"]
        self.description = data["description"]
        self.created_at = (
            parser.parse(data["createTime"])
            if data.get("createTime")
            else None
        )
        self.updated_at = (
            parser.parse(data["updateTime"])
            if data.get("updateTime")
            else None
        )
        self.owner = (
            User(int(data["owner"].split("/")[1]), self.__api_key)
            if data.get("owner")
            else None
        )

        self.member_count = data["memberCount"]
        self.public_entry = data["publicEntryAllowed"]
        self.locked = data["locked"]
        self.verified = data["verified"]

        return self

    async def fetch_member(self, user_id: int) -> Optional[GroupMember]:
        """
        Returns the member info for the provided user or `None` if the user \
        is not a member of the group.

        Args:
            user_id: The user ID to fetch member info for.

        Returns:
            The [`GroupMember`][rblxopencloud.GroupMember] for the provided \
            user or `None` if the user isn't a member of the group.
        """

        _, data, _ = await send_request(
            "GET",
            f"/groups/{self.id}/memberships",
            params={"limit": 1, "filter": f"user == 'users/{user_id}'"},
            expected_status=[200],
            authorization=self.__api_key,
        )

        if not data["groupMemberships"]:
            return None
        return GroupMember(data["groupMemberships"][0], self.__api_key, self)

    async def update_member(
        self, user_id: int, role_id: int = None
    ) -> Optional[GroupMember]:
        """
        Updates the member with the requested information and returns the \
        updated member info.

        Args:
            user_id: The user ID to fetch member info for. Must not be the \
                authorizing user. 
            role_id: If provided, updates the member's group role to the \
                provided [`GroupRole.id`][rblxopencloud.GroupRole.id]. This \
                role must not be Owner or Guest and must be lower than the \
                authorizing user's rank.

        Returns:
            The updated [`GroupMember`][rblxopencloud.GroupMember] for the \
            provided user.
        """

        membership_id = (
            urlsafe_b64encode(str(user_id).encode()).strip(b"=").decode()
        )

        _, data, _ = await send_request(
            "PATCH",
            f"/groups/{self.id}/memberships/{membership_id}",
            json={
                "path": f"groups/{self.id}/memberships/{membership_id}",
                "user": f"users/{user_id}",
                "role": (
                    f"groups/{self.id}/roles/{role_id}" if role_id else None
                ),
            },
            expected_status=[200],
            authorization=self.__api_key,
        )

        return GroupMember(data, self.__api_key, self)

    async def fetch_role(
        self, role_id: int, skip_cache: bool = False
    ) -> Optional[GroupRole]:
        """
        Returns the role info for the provided role ID or `None` if the role \
        ID isn't found.

        Args:
            role_id: The ID of the role to find.
            skip_cache: Wether to forcably refetch role information.

        Returns:
            The [`GroupRole`][rblxopencloud.GroupRole] for the provided role \
            ID or `None` if the role couldn't be found.
        """

        if skip_cache or not list(self.__role_cache.keys()):
            list(await self.list_roles())

        role_entry = self.__role_cache.get(role_id)
        return GroupRole(role_entry) if role_entry else None

    async def list_members(
        self, limit: int = None, role_id: int = None
    ) -> AsyncGenerator[Any, GroupMember]:
        """
        Iterates each member in the group, optionally limited to a specific \
        role.
                
        Args:
            limit: The maximum number of members to iterate. \
            This can be `None` to return all members.
            role_id: If present, the api will only provide \
            members with this role.
        
        Yields:
            [`GroupMember`][rblxopencloud.GroupMember] for every member in \
            the group.
        """
        filter = None

        if role_id:
            filter = f"role == 'groups/{self.id}/roles/{role_id}'"

        async for entry in iterate_request(
            "GET",
            f"/groups/{self.id}/memberships",
            authorization=self.__api_key,
            params={
                "maxPageSize": limit if limit and limit <= 99 else 99,
                "filter": filter,
            },
            data_key="groupMemberships",
            cursor_key="pageToken",
            max_yields=limit,
            expected_status=[200],
        ):
            yield GroupMember(entry, self.__api_key, self)

    async def list_roles(
        self, limit: int = None
    ) -> AsyncGenerator[Any, GroupRole]:
        """
        Iterates every role in the group.
        
        Args:
            limit: The maximum number of roles to iterate. This can be \
            `None` to return all role.
        
        Yields:
            [`GroupRole`][rblxopencloud.GroupRole] for every role in the group.
        """

        async for entry in iterate_request(
            "GET",
            f"/groups/{self.id}/roles",
            authorization=self.__api_key,
            params={"maxPageSize": limit if limit and limit <= 20 else 20},
            data_key="groupRoles",
            cursor_key="pageToken",
            max_yields=limit,
            expected_status=[200],
        ):
            self.__role_cache[int(entry["id"])] = entry

            yield GroupRole(entry)

    async def list_join_requests(
        self, limit: int = None, user_id: int = None
    ) -> AsyncGenerator[Any, "GroupJoinRequest"]:
        """
        Iterates every group join request for private groups.
        
        Args:
            limit: The maximum number of join requests to iterate. This can \
            be `None` to return all join requests.
            user_id: If present, the api will only provide the join request \
            with this user ID.
        
        Yields:
            [`GroupJoinRequest`][rblxopencloud.GroupJoinRequest] for each \
            user who has requested to join.
        """

        async for entry in iterate_request(
            "GET",
            f"/groups/{self.id}/join-requests",
            authorization=self.__api_key,
            expected_status=[200],
            params={
                "maxPageSize": limit if limit and limit <= 100 else 100,
                "filter": f"user == 'users/{user_id}'" if user_id else None,
            },
            data_key="groupJoinRequests",
            cursor_key="nextPageToken",
            max_yields=limit,
        ):
            yield GroupJoinRequest(entry, self.__api_key)

    async def fetch_shout(self) -> GroupShout:
        """
        Returns [`GroupShout`][rblxopencloud.GroupShout] with information \
        about the group's current shout. It requires permission to view the \
        shout from the API key owner or OAuth2 authorizing user.

        Returns:
            [`GroupShout`][rblxopencloud.GroupShout] with information about \
            the group's shout.
        """

        _, data, _ = await send_request(
            "GET",
            f"/groups/{self.id}/shout",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return GroupShout(data, self.__api_key)

    async def accept_join_request(self, user_id: int):
        """
        Accepts the join request for the provided user.
        
        Args:
            user_id: The user ID to accept the join request for. Must have \
            requested to join.
        """

        await send_request(
            "POST",
            f"/groups/{self.id}/join-requests/{user_id}:accept",
            authorization=self.__api_key,
            expected_status=[200],
            json={},
        )

    async def decline_join_request(self, user_id: int):
        """
        Declines the join request for the provided user.

        Args:
            user_id: The user ID to decline the join request for. Must have \
            requested to join.
        """

        await send_request(
            "POST",
            f"/groups/{self.id}/join-requests/{user_id}:decline",
            authorization=self.__api_key,
            expected_status=[200],
            json={},
        )

    async def list_audit_logs(
        self,
        limit: int = None,
        action_type: "GroupAuditLogEntryActionType" = None,
        user_id: int = None,
        descending: bool = True,
    ) -> AsyncGenerator[Any, "GroupAuditLogEntry"]:
        """
        Lists the audit log entries for the group, optionally filtered by \
        action type and user ID.

        Requires `legacy-group:manage` on an API Key or OAuth2 authorization.

        Args:
            limit: The maximum number of audit log entries to iterate. \
            Defaults to `None`, meaning no limit.
            action_type: Filters audit log entries to only return those of \
            the specified action type.
            user_id: Filters audit log entries to only return those performed \
            by the specified user ID.
            descending: Whether to sort the audit log entries in descending \
            order by creation time meaning the most recent entries are \
            returned first.

        Yields:
            The audit log entries for each audit log entry found.

        ???+ warning "Edge case with role caching"
            This endpoint caches some basic rank info (e.g. role ID, name, \
            and rank number) for any role found in the audit log. This means \
            that calls to [`GroupMember.fetch_role`][rblxopencloud.GroupMember.fetch_role] \
            will use the cached role information. While this means that \
            additional requests aren't used for these members, it means that \
            information such as permissions, member counts and descriptions \
            are unavailable for these cached roles.

            Furthermore, it means future requests to [`GroupMember.fetch_role`][rblxopencloud.GroupMember.fetch_role] \
            and [`Group.fetch_role`][rblxopencloud.Group.fetch_role] \
            for roles not found in the audit log will not be cached, so \
            `None` will be returned instead.

            If you want to ensure all role information is available and all \
            roles are available, you should either call [`Group.list_roles`][rblxopencloud.Group.list_roles] \
            before calling this method or set `skip_cache=True` for the next \
            call to [`GroupMember.fetch_role`][rblxopencloud.GroupMember.fetch_role] \
            or [`Group.fetch_role`][rblxopencloud.Group.fetch_role] afterwards.
        
        ??? example
            Prints the 50 most recent audit log entries for saving a place to \
            the console, along with the username of the member who performed \
            the action, their role name in the group and the place name and \
            version ID.
            ```python
            async for entry in group.list_audit_logs(limit=50, action_type=GroupAuditLogEntryActionType.SavePlace):
                # Fetch role will not make an additional request because the role info is cached from the audit log entry request
                role = await entry.member.fetch_role()
                print(
                    f"{entry.member.username} ({role.name}) saved {entry.description.get('AssetName')}, version ID: {entry.description.get('VersionNumber')}"
                )
            ```
        """

        if limit and limit <= 10:
            passed_limit = 10
        elif limit and limit <= 25:
            passed_limit = 25
        elif limit and limit <= 50:
            passed_limit = 50
        else:
            passed_limit = 100

        async for entry in iterate_request(
            "GET",
            f"legacy-groups/v1/groups/{self.id}/audit-log",
            authorization=self.__api_key,
            params={
                "limit": passed_limit,
                "userId": user_id,
                "sortOrder": "Desc" if descending else "Asc",
                "actionType": action_type.name if action_type else None,
            },
            data_key="data",
            cursor_key="cursor",
            max_yields=limit,
            expected_status=[200],
        ):
            yield GroupAuditLogEntry(entry, self, self.__api_key)
