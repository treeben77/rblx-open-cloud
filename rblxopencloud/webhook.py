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
    
    Args:
        secret: Random letters only known by Roblox and the server to validate requests.
        api_key: Your API key created from [Creator Dashboard](https://create.roblox.com/credentials) with access to all objects that are generated in events.
    
    Attributes:
        secret (Optional[bytes]): The webhook secret only known by Roblox and the recieving agent. 
    """

    def __init__(self, secret: Optional[Union[str, bytes]] = None, api_key: Optional[str]=None) -> None:
        self.secret: Optional[bytes] = secret if type(secret) == bytes or secret == None else secret.encode()
        self.__api_key: Optional[str] = api_key
        self.__events: list[Callable] = {}
        self.__on_error: Optional[Callable] = None

    def __repr__(self) -> str:
        return f"rblxopencloud.Webhook()"

    def process_notification(self, body: bytes, secret_header: bytes = None, validate_signature: bool=True) -> tuple[str, int]:
        """
        Processes a HTTP webhook event and returns a response text and status code tuple.
        
        Example:
            Since the webhook section of the library was designed specificly for Flask, it is very easy to implement with Flask. Here's an example:
            ```py
                @app.route('/webhook-roblox', methods=["POST"])
                def webhook_roblox():
                    return webhook.process_notification(body=request.data, secret_header=request.headers["Roblox-Signature"])
            ```
            If you're using another framework, it will be slightly more complex to work it out.

        Args:
            body: The HTTP raw body.
            secret_header: The raw value of the `Roblox-Signature` header.
            validate_signature: Wether to validate the signature or not. This should not be disabled in production.
        
        Returns:
            A tuple with the string response in the first index, and the status code in the second index. Designed to be put straight into the return route in Flask.
        
        Raises:
            UnknownEventType: The library recieved a webhook payload for an unknown type.
            UnhandledEventType: The library recieved a webhook payload that doesn't have any handler function attached.
        
        !!! note
            If an exception is raised in the notification handler, then it will be raised from this method. Therefore, any exception could be raised by this method. 
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
        | `on_test` | [`rblxopencloud.TestNotification`][rblxopencloud.TestNotification] | Triggers when the user clicks 'Test Response' on the Webhook configuration page |
        | `on_right_to_erasure_request` | [`rblxopencloud.RightToErasureRequestNotification`][rblxopencloud.RightToErasureRequestNotification] | Triggers when a right to erause request is recieved. |
        
        Example:
            This will print the user ID and effected experiences for every right to erasure request that is recieved.
            ```py
            @webhook.event
            def on_right_to_erasure_request(notification):
                print(notification.user_id, notification.experiences)
            ```
        """

        if func.__name__ == "on_error":
            self.__on_error = func
        else:
            if not func.__name__ in EVENT_TYPES.values(): raise ValueError(f"'{func.__name__}' is not a valid event name.")

            self.__events[func.__name__] = func

        return func

class Notification():
    """
    Represents a recieved base webhook event.

    !!! warning
        This class isn't designed to be created by users. It is returned by some decorated functions from [`Webhook.event()`][rblxopencloud.Webhook.event].
    
    Attributes:
        notification_id: The notifications unique ID. If an ID is repeated, assume it is a duplicate and ignore it.
        timestamp: The time the notification was created.
        webhook: The webhook that the notifcation came from.
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

    !!! warning
        This class isn't designed to be created by users. It is returned by some decorated functions from [`Webhook.event()`][rblxopencloud.Webhook.event].
    
    Attributes:
        notification_id (str): The notifications unique ID. If an ID is repeated, assume it is a duplicate and ignore it.
        timestamp (datetime.datetime): The time the notification was created.
        webhook (Webhook): The webhook that the notifcation came from.
        user: The user that clicked the test button.
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

    !!! warning
        This class isn't designed to be created by users. It is returned by some decorated functions from [`Webhook.event()`][rblxopencloud.Webhook.event].
    
    Attributes:
        notification_id (str): The notifications unique ID. If an ID is repeated, assume it is a duplicate and ignore it.
        timestamp (datetime.datetime): The time the notification was created.
        webhook (Webhook): The webhook that the notifcation came from.
        user_id: The ID of the user who requested their data to be erased.
        experiences: A list of experiences the user potentially has saved data.
    """    
    
    def __init__(self, body, webhook, api_key):
        super().__init__(body, webhook, api_key)
        event = body["EventPayload"]

        self.user_id: int = event["UserId"]
        self.experiences: list[Experience] = [Experience(experience_id, api_key) for experience_id in event["GameIds"]]
    
    def __repr__(self) -> str:
        return f"rblxopencloud.RightToErasureRequestNotification(notification_id=\"{self.notification_id}\", user={self.user})"