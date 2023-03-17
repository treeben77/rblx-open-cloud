import datetime

class User():
    def __init__(self, openid: dict):
        self.username = openid["preferred_username"]
        self.id = openid["sub"]
        self.display_name = openid["nickname"]
        self.profile_uri = openid["profile"]
        self.created_at = datetime.datetime.fromtimestamp(openid["created_at"])

    def __repr__(self) -> str:
        return f"rblxopencloud.User(username={self.username}, id={self.id})"