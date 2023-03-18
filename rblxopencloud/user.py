import datetime

class User():
    def __init__(self, data: dict):
        self.username: str = data.get("preferred_username")
        self.id: int = data.get("id") or data.get("sub")
        self.display_name: str = data.get("nickname")
        self.profile_uri: str = data.get("profile") or f"https://roblox.com/users/{self.id}/profile"
        self.created_at: datetime.datetime = datetime.datetime.fromtimestamp(data["created_at"]) if data.get("created_at") else None

    def __repr__(self) -> str:
        return f"rblxopencloud.User(username={self.username}, id={self.id})"