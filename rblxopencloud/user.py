import datetime

class User():
    def __init__(self, openid: dict):
        self.username = openid.get("preferred_username")
        self.id = openid.get("id") or openid.get("sub")
        self.display_name = openid.get("nickname")
        self.profile_uri = openid.get("profile") or f"https://roblox.com/users/{self.id}/profile"
        if openid.get("created_at"): self.created_at = datetime.datetime.fromtimestamp(openid["created_at"])
        else: self.created_at = None

    def __repr__(self) -> str:
        return f"rblxopencloud.User(username={self.username}, id={self.id})"

    def __str__(self) -> str:
        if self.display_name: return self.display_name
        else: return str(self.id)