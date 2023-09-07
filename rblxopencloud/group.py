from .creator import Creator
from .exceptions import rblx_opencloudException, InvalidKey, NotFound, RateLimited, ServiceUnavailable, PermissionDenied
import datetime
from typing import Optional, Iterable, TYPE_CHECKING
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
    def __init__(self, shout, api_key=None) -> None:
        self.content: str = shout["content"]
        self.user: User = User(int(shout["poster"].split("/")[1]), api_key)
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat((shout["updateTime"].split("Z")[0]+"0"*6)[0:26])
        self.first_created_at: datetime.datetime = datetime.datetime.fromisoformat((shout["createTime"].split("Z")[0]+"0"*6)[0:26])

    def __repr__(self) -> str:
        return f"rblxopencloud.GroupShout(content=\"{self.content}\")"

class GroupRolePermissions():
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
        self.manage_group_experiences: bool = permissions["manageGroupUniverses"]
        self.view_group_analytics: bool = permissions["viewUniverseAnalytics"]
        self.create_api_keys: bool = permissions["createApiKeys"]
        self.manage_api_keys: bool = permissions["manageApiKeys"]

    def __repr__(self) -> str:
        return f"rblxopencloud.GroupRolePermissions()"

class GroupRole():
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
    Represents a group on Roblox. For now this is only used for uploading assets, but in the future you'll be able to manage other aspects of a group.
    ### Paramaters
    id: int - The group's ID.
    api_key: str - Your API key created from [Creator Dashboard](https://create.roblox.com/credentials) with access to this user.
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

        response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/{self.id}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 404: raise NotFound(response.json()['message'])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
        
        data = response.json()

        self.name = data["displayName"]
        self.description = data["description"]
        self.created_at = datetime.datetime.fromisoformat((data["createTime"].split("Z")[0]+"0"*6)[0:26])
        self.updated_at = datetime.datetime.fromisoformat((data["updateTime"].split("Z")[0]+"0"*6)[0:26])
        self.owner = User(int(data["owner"].split("/")[1]), self.__api_key) if data.get("owner") else None
        self.member_count = data["memberCount"]
        self.public_entry = data["publicEntryAllowed"]
        self.locked = data["locked"]
        self.verified = data["verified"]
        
        return self
        
    def list_members(self, limit: Optional[int]=None, role_id:Optional[int] = None, user_id: Optional[int] = None) -> Iterable["GroupMember"]:

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
    
    def list_roles(self, limit: Optional[int]=None):

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

        response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/{self.id}/shout",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise PermissionDenied(response.json()['message'])
        elif response.status_code == 404: raise NotFound(response.json()['message'])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
        
        return GroupShout(response.json(), self.__api_key)