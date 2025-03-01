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
from typing import Iterable, Optional

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
        joined_at (datetime.datetime): The time the user joined the group.
        updated_at (datetime.datetime): The time the user was last update in \
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
        self.joined_at: datetime.datetime = parser.parse(member["createTime"])
        self.updated_at: datetime.datetime = parser.parse(member["updateTime"])
        super().__init__(self.id, api_key)

    def __repr__(self) -> str:
        return f"<rblxopencloud.GroupMember id={self.id} group={self.group}>"

    def fetch_role(self, skip_cache: bool = False) -> GroupRole:
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

        return self.group.fetch_role(self.role_id, skip_cache=skip_cache)

    def update(self, role_id: int = None):
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

        member = self.group.update_member(self.id, role_id)

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

    def fetch_info(self) -> "Group":
        """
        Updates the empty parameters in this Group object and returns it self \
        with the group info.
        """

        _, data, _ = send_request(
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

    def fetch_member(self, user_id: int) -> Optional[GroupMember]:
        """
        Returns the member info for the provided user or `None` if the user \
        is not a member of the group.

        Args:
            user_id: The user ID to fetch member info for.

        Returns:
            The [`GroupMember`][rblxopencloud.GroupMember] for the provided \
            user or `None` if the user isn't a member of the group.
        """

        _, data, _ = send_request(
            "GET",
            f"/groups/{self.id}/memberships",
            params={"limit": 1, "filter": f"user == 'users/{user_id}'"},
            expected_status=[200],
            authorization=self.__api_key,
        )

        if not data["groupMemberships"]:
            return None
        return GroupMember(data["groupMemberships"][0], self.__api_key, self)

    def update_member(
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

        _, data, _ = send_request(
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

    def fetch_role(
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
            list(self.list_roles())

        role_entry = self.__role_cache.get(role_id)
        return GroupRole(role_entry) if role_entry else None

    def list_members(
        self, limit: int = None, role_id: int = None
    ) -> Iterable[GroupMember]:
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

        for entry in iterate_request(
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

    def list_roles(self, limit: int = None) -> Iterable[GroupRole]:
        """
        Iterates every role in the group.
        
        Args:
            limit: The maximum number of roles to iterate. This can be \
            `None` to return all role.
        
        Yields:
            [`GroupRole`][rblxopencloud.GroupRole] for every role in the group.
        """

        for entry in iterate_request(
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

    def list_join_requests(
        self, limit: int = None, user_id: int = None
    ) -> Iterable["GroupJoinRequest"]:
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

        for entry in iterate_request(
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

    def fetch_shout(self) -> GroupShout:
        """
        Returns [`GroupShout`][rblxopencloud.GroupShout] with information \
        about the group's current shout. It requires permission to view the \
        shout from the API key owner or OAuth2 authorizing user.

        Returns:
            [`GroupShout`][rblxopencloud.GroupShout] with information about \
            the group's shout.
        """

        _, data, _ = send_request(
            "GET",
            f"/groups/{self.id}/shout",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return GroupShout(data, self.__api_key)

    def accept_join_request(self, user_id: int):
        """
        Accepts the join request for the provided user.
        
        Args:
            user_id: The user ID to accept the join request for. Must have \
            requested to join.
        """

        send_request(
            "POST",
            f"/groups/{self.id}/join-requests/{user_id}:accept",
            authorization=self.__api_key,
            expected_status=[200],
            json={},
        )

    def decline_join_request(self, user_id: int):
        """
        Declines the join request for the provided user.

        Args:
            user_id: The user ID to decline the join request for. Must have \
            requested to join.
        """

        send_request(
            "POST",
            f"/groups/{self.id}/join-requests/{user_id}:decline",
            authorization=self.__api_key,
            expected_status=[200],
            json={},
        )
