from .exceptions import UnknownEventType, UnhandledEventType
from .user import User
from .experience import Experience

from typing import Optional, Union, Callable
import hashlib
import hmac
import base64
import time
from datetime import datetime
import json

__all__ = (
    "Webhook",
    "Notification",
    "TestNotification",
    "RightToErasureRequestNotification"
)

EVENT_TYPES = {
    "SampleNotification": "on_test",
    "RightToErasureRequest": "on_right_to_erasure_request"
}

class Webhook():
    """
    Represents a Roblox outgoing webhook. It is used to validate and process webhook events.
    ### Parameters
    secret: Optional[Union[str, bytes]] - Random letters only known by Roblox and the server to validate requests.
    api_key: str - Your API key created from [Creator Dashboard](https://create.roblox.com/credentials) with access to all objects that are generated in events.
    """

    def __init__(self, secret: Optional[Union[str, bytes]] = None, api_key: Optional[str]=None) -> None:
        self.secret: Optional[bytes] = secret if type(secret) == bytes or secret == None else secret.encode()
        self.__api_key: Optional[str] = api_key
        self.__events: list[Callable] = {}
        self.__on_error: Optional[Callable] = None

    def __repr__(self) -> str:
        return f"rblxopencloud.Webhook()"

    def process_notification(self, body: bytes, secret_header: bytes = None, validate_signature=True) -> tuple[str, int]:
        """
        Processes a HTTP webhook event and returns a response text and status code tuple. Example for Flask:
        
        ```py
            @app.route('/webhook-roblox', methods=["POST"])
            def webhook_roblox():
                return webhook.process_notification(body=request.data, secret_header=request.headers["Roblox-Signature"])
        ```
        ### Parameters
        body: bytes - The HTTP raw body.
        secret_header: bytes - The raw value of the `Roblox-Signature` header.
        validate_signature: bool - Wether to validate the signature or not. This should not be disabled in production.
        """

        if validate_signature:
            if self.secret:
                if not secret_header: return "Invalid signature", 401

                split_header = secret_header.split(",")
                if not len(split_header) >= 2: return "Invalid signature", 401
                
                hash_object = hmac.new(self.secret, msg=split_header[0].split('=')[1].encode()+b'.'+body, digestmod=hashlib.sha256)

                if not base64.b64encode(hash_object.digest()).decode() == split_header[1].split('=', maxsplit=1)[1]: return "Invalid signature", 401

            if secret_header:
                split_header = secret_header.split(",")

                if 0 < time.time() - int(split_header[0].split('=')[1]) > 600:
                    return "Invalid signature", 401

        body = json.loads(body)

        notification = Notification(body, self, self.__api_key)

        try:
            event_type = EVENT_TYPES.get(body["EventType"])
            if not event_type: raise UnknownEventType(f"Unkown webhook event type '{event_type}'")

            if event_type == "on_test":
                notification = TestNotification(body, self, self.__api_key)
            elif event_type == "on_right_to_erasure_request":
                notification = RightToErasureRequestNotification(body, self, self.__api_key)

            function = self.__events.get(event_type)
            if not function: raise UnhandledEventType(f"'{event_type}' doesn't have am event callback.")

            function(notification=notification)
        except(Exception) as error:
            if self.__on_error:
                self.__on_error(notification, error)
            else:
                raise error
            
        return "", 204
    
    def event(self, func: Callable):
        """
        Register event callbacks with this decorator. The allowed function names, and the notification type they return is as follows:

        | Event Name | Notification Type | Event Description |
        | --- | --- | --- |
        | `on_test` | `rblx-open-cloud.TestNotification` | Triggers when the user clicks 'Test Response' on the Webhook configuration page |
        | `on_right_to_erasure_request` | `rblx-open-cloud.RightToErasureRequestNotification` | Triggers when a right to erause request is recieved. |
        """

        if func.__name__ == "on_error":
            self.__on_error = func
        else:
            if not func.__name__ in EVENT_TYPES.values(): raise ValueError(f"'{func.__name__}' is not a valid event name.")

            self.__events[func.__name__] = func

        return func

class Notification():
    """
    Represents a recieved webhook event.
    """

    def __init__(self, body, webhook, api_key):
        self.notification_id: str = body["NotificationId"]
        self.timestamp: datetime = datetime.fromisoformat((body["EventTime"].split("Z")[0]+"0"*6)[0:26])
        self.webhook: Webhook = webhook
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Notification(notification_id=\"{self.notification_id}\")"

class TestNotification(Notification):
    """
    Represents a recieved webhook event triggered by the user pressing 'Test Response' on the webhook configuration page.
    """

    def __init__(self, body, webhook, api_key):
        super().__init__(body, webhook, api_key)
        event = body["EventPayload"]

        self.user: User = User(event["UserId"], api_key)
    
    def __repr__(self) -> str:
        return f"rblxopencloud.TestNotification(notification_id=\"{self.notification_id}\", user={self.user})"

class RightToErasureRequestNotification(Notification):
    """
    Represents a recieved webhook event triggered by a user requesting Roblox to erase all their user data.
    """
    
    def __init__(self, body, webhook, api_key):
        super().__init__(body, webhook, api_key)
        event = body["EventPayload"]

        self.user_id: int = event["UserId"]
        self.experiences: list[Experience] = [Experience(experience_id, api_key) for experience_id in event["GameIds"]]
    
    def __repr__(self) -> str:
        return f"rblxopencloud.RightToErasureRequestNotification(notification_id=\"{self.notification_id}\", user={self.user})"