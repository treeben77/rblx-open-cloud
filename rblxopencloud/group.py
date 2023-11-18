from .creator import Creator
from .exceptions import rblx_opencloudException, InvalidKey, NotFound, RateLimited, ServiceUnavailable, PermissionDenied
import datetime
from typing import Optional, Iterable
from . import user_agent, request_session
from .user import User

__all__ = (
    "Group",
    "GroupMember",
    "GroupRole",
    "GroupRolePermissions",
    "GroupShout"
)

class GroupShout():
    """
    Represents a group's shout.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`Group.fetch_shout()`][rblxopencloud.Group.fetch_shout].

    Attributes:
        content (str): The shout's content.
        user (User): The user who posted the shout.
        created_at (datetime.datetime): The timestamp the shout was created.
        first_created_at (datetime.datetime): The timestamp the first shout in the group was created.
    """

    def __init__(self, shout, api_key=None) -> None:
        self.content: str = shout["content"]
        self.user: User = User(int(shout["poster"].split("/")[1]), api_key)
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat((shout["updateTime"].split("Z")[0]+"0"*6)[0:26])
        self.first_created_at: datetime.datetime = datetime.datetime.fromisoformat((shout["createTime"].split("Z")[0]+"0"*6)[0:26])

    def __repr__(self) -> str:
        return f"rblxopencloud.GroupShout(content=\"{self.content}\")"

class GroupRolePermissions():
    """
    Data class that contains information about a role's permissions.

    !!! warning
        This class isn't designed to be created by users. It is an attribute of [`rblxopencloud.GroupRole()`][rblxopencloud.GroupRole].

    Attributes:
        view_wall_posts (bool): Allows the member to view the group's wall.
        create_wall_posts (bool): Allows the member to send posts the group's wall.
        delete_wall_posts (bool): Allows the member to delete other member's posts the group's wall.
        view_group_shout (bool): Allows the member to view the group's current shout.
        create_group_shout (bool): Allows the member to update the group's current shout.
        change_member_ranks (bool): Allows the member to change lower ranked member's role.
        accept_join_requests (bool): Allows the member to accept user join requests.
        exile_members (bool): Allows the member to exile members from the group.
        manage_relationships (bool): Allows the member to add and remove allies and enemies.
        view_audit_log (bool): Allows the member to view the group's audit logs.
        spend_group_funds (bool): Allows the member to spend group funds.
        advertise_group (bool): Allows the member to create advertisements for the group.
        create_avatar_items (bool): Allows the member to create avatar items for the group.
        manage_avatar_items (bool): Allows the member to manage avatar items for the group.
        manage_experiences (bool): Allows the member to create, edit, and manage the group's experiences.
        view_experience_analytics (bool): Allows the member to view the analytics of the group's experiences.
        create_api_keys (bool): Allows the member to create Open Cloud API keys.
        manage_api_keys (bool): Allows the member to manage all Open Cloud API keys.
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
        self.view_experience_analytics: bool = permissions["viewUniverseAnalytics"]
        self.create_api_keys: bool = permissions["createApiKeys"]
        self.manage_api_keys: bool = permissions["manageApiKeys"]

    def __repr__(self) -> str:
        return f"rblxopencloud.GroupRolePermissions()"

class GroupRole():
    """
    Represents a role inside of a group.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`Group.list_roles()`][rblxopencloud.Group.list_roles].

    Attributes:
        id (int): The role's ID.
        name (str): The role's name.
        rank (int): The numerical rank between 0 and 255. `0` is always the guest role, and `255` is always the owner role.
        description (Optional[str]): The role's description. Only present if the authorized user is the group owner.
        member_count (Optional[int]): The number of group members with this role. Will always be `None` for the guest tole.
        permissions (Optional[GroupRolePermissions]): The role's permissions. It is only present for the guest role, unless the authorizing user is the owner, or are assigned to the role.
    """

    def __init__(self, role) -> None:
        self.id: int = int(role["id"])
        self.name: str = role["displayName"]
        self.rank: int = role["rank"]
        self.description: Optional[str] = role.get("description")
        self.member_count: Optional[int] = role.get("memberCount", None)
        self.permissions: Optional[GroupRolePermissions] = GroupRolePermissions(role["permissions"]) if role.get("permissions") else None
    
    def __repr__(self) -> str:
        return f"rblxopencloud.GroupRole(id={self.id}, name=\"{self.name}\", rank={self.rank})"

class GroupMember(User):
    """
    Represents a user inside of a group.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`Group.list_members()`][rblxopencloud.Group.list_members] and [`User.list_groups()`][rblxopencloud.User.list_groups].

    Attributes:
        id (int): The user's ID.
        role_id (int): The user's role ID.
        group (Group): The group this object is related to.
        joined_at (datetime.datetime): The time when the user joined the group.
        updated_at (datetime.datetime): The time when the user's membership was last updated (i.e. their role was changed).
    
    !!! note
        This class bases [`rblxopencloud.User`][rblxopencloud.User], so all methods of it can be used from this object, such as [`User.list_inventory()`][rblxopencloud.User.list_inventory]. They aren't documented here to save space.
    """

    def __init__(self, member, api_key, group=None) -> None:
        self.id: int = int(member["user"].split("/")[1])
        self.role_id: int = int(member["role"].split("/")[-1])
        self.group: Group = group if group else Group(int(member["role"].split("/")[1]), api_key)
        self.joined_at: datetime.datetime = datetime.datetime.fromisoformat((member["createTime"].split("Z")[0]+("" if "." in member["createTime"] else ".")+"0"*6)[0:26])
        self.updated_at: datetime.datetime = datetime.datetime.fromisoformat((member["updateTime"].split("Z")[0]+("" if "." in member["updateTime"] else ".")+"0"*6)[0:26])

        super().__init__(self.id, api_key)

    def __repr__(self) -> str:
        return f"rblxopencloud.GroupMember(id={self.id}, group={self.group})"

class Group(Creator):
    """
    Represents a group on Roblox. It can be used for both uploading assets, and accessing group information.
    
    Args:
        id: The group's ID.
        api_key: The API key created on the [Creator Dashboard](https://create.roblox.com/credentials) with access to the user.
    
    Attributes:
        id (int): The group's ID.
        name (Optional[str]): The group's name.
        description (Optional[str]): The group's description.
        created_at (Optional[datetime.datetime]): The time the group was created at.
        updated_at (Optional[datetime.datetime]): The time the group was last updated.
        owner (Optional[User]): The group's group's owner.
        member_count (Optional[int]): The number of members in the group.
        public_entry (Optional[bool]): Wether you can join without being approved.
        locked (Optional[bool]): Wether the group has been locked by Roblox moderation.
        verified (Optional[bool]): Wether the group has a verified badge.
    
    !!! note
        All attributes above except for `id` and `None` by default, until [`Group.fetch_info`][rblxopencloud.Group.fetch_info] is called.
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

        super().__init__(id, api_key, "Group")
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Group({self.id})"
    
    def fetch_info(self) -> "Group":
        """
        Updates the empty attributes in the class with the group info.

        **The `group:read` scope is required for OAuth2 authorization.**

        Returns:
            The class itself.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to read public group info, or is from an invalid IP address.
            NotFound: The group does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """

        response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/{self.id}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 404: raise NotFound(response.json()['message'])
        elif response.status_code == 429: raise RateLimited("You're being rate limited!")
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
        
        data = response.json()

        self.name = data["displayName"]
        self.description = data["description"]
        self.created_at = datetime.datetime.fromisoformat((data["createTime"].split("Z")[0]+("." if not "." in data["createTime"] else "")+"0"*6)[0:26])
        self.updated_at = datetime.datetime.fromisoformat((data["updateTime"].split("Z")[0]+("." if not "." in data["updateTime"] else "")+"0"*6)[0:26])
        self.owner = User(int(data["owner"].split("/")[1]), self.__api_key) if data.get("owner") else None
        self.member_count = data["memberCount"]
        self.public_entry = data["publicEntryAllowed"]
        self.locked = data["locked"]
        self.verified = data["verified"]
        
        return self
        
    def list_members(self, limit: Optional[int]=None, role_id:Optional[int] = None, user_id: Optional[int] = None) -> Iterable["GroupMember"]:
        """
        Interates [`rblxopencloud.GroupMember`][rblxopencloud.GroupMember] for each user in the group.
        
        **The `group:read` scope is required for OAuth2 authorization.**

        Example:
            The example below would iterate through every user in the group.
            ```py
                for member in group.list_members():
                    print(member)
            ```
        
        Args:
            limit: The maximum number of members to iterate. This can be `None` to return all members.
            role_id: If present, the api will only provide members with this role.
            user_id: If present, the api will only provide the member with this user ID.
        
        Returns:
            An iterable of [`rblxopencloud.GroupMember`][rblxopencloud.GroupMember] for each member in the group.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to read public group info, or is from an invalid IP address.
            NotFound: The group does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """

        filter = None

        if user_id:
            filter = f"user == 'users/{user_id}'"
        
        if role_id:
            filter = f"role == 'groups/{self.id}/roles/{role_id}'"

        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/{self.id}/memberships",
                headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent}, params={
                "maxPageSize": limit if limit and limit <= 99 else 99,
                "filter": filter,
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
    
    def list_roles(self, limit: Optional[int]=None) -> Iterable[GroupRole]:
        """
        Interates [`rblxopencloud.GroupRole`][rblxopencloud.GroupRole] for each role in the group.
        
        **The `group:read` scope is required for OAuth2 authorization.**
        
        Args:
            limit: The maximum number of roles to iterate. This can be `None` to return all roles.
        
        Returns:
            An iterable of [`rblxopencloud.GroupRole`][rblxopencloud.GroupRole] for each role in the group. If the authorizing user is not the owner, then the `description` of reach role is `None`, and can only see permissions for their own role and the guest role.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to read public group info, or is from an invalid IP address.
            NotFound: The group does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """

        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/{self.id}/roles",
                headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent}, params={
                "maxPageSize": limit if limit and limit <= 20 else 20,
                "pageToken": nextcursor if nextcursor else None
            })

            if response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
            elif response.status_code == 401: raise InvalidKey(response.text)
            elif response.status_code == 404: raise NotFound(response.json()["message"])
            elif response.status_code == 429: raise RateLimited("You're being rate limited!")
            elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
            
            data = response.json()
            for role in data["groupRoles"]:
                yields += 1
                
                yield GroupRole(role)
            nextcursor = data.get("nextPageToken")
            if not nextcursor: break
    
    def fetch_shout(self) -> "GroupShout":
        """
        Fetches the [`rblxopencloud.GroupShout`][rblxopencloud.GroupShout] for the group.
        
        **The `group:read` scope is required for OAuth2 authorization.**
        
        Returns:
            The group's [`rblxopencloud.GroupShout`][rblxopencloud.GroupShout].

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to read public group info, or is from an invalid IP address.
            PermissionDenied: The user does not have the proper guest permissions to view the group's shout.
            NotFound: The group does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """

        response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/{self.id}/shout",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise PermissionDenied(response.json()['message'])
        elif response.status_code == 404: raise NotFound(response.json()['message'])
        elif response.status_code == 429: raise RateLimited("You're being rate limited!")
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
        
        return GroupShout(response.json(), self.__api_key)