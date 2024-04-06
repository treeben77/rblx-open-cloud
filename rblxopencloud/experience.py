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

from datetime import datetime
from enum import Enum
import io
from typing import Iterable, Optional, Union
import urllib.parse

from dateutil import parser

from .datastore import DataStore, OrderedDataStore
from .http import iterate_request, send_request
from .group import Group
from .user import User

__all__ = (
    "Experience",
    "ExperienceAgeRating",
    "ExperienceSocialLink",
    "Place"
)

class ExperienceAgeRating(Enum):
    """
    Enum representing the an experience's age rating.
    
    Attributes:
        Unknown (0): The experience age rating is unknown or not implemented.
        Unspecified (1): The experience has not provided an age rating.
        AllAges (2): The experience is marked as All Ages.
        NinePlus (3): The experience is marked as 9+.
        ThirteenPlus (4): The experience is marked as 13+.
        SeventeenPlus (5): The experience is marked as 17+.
    """

    Unknown = 0
    Unspecified = 1
    AllAges = 2
    NinePlus = 3
    ThirteenPlus = 4
    SeventeenPlus = 5

class ExperienceSocialLink():
    """
    Represents a social link in an experience.
    
    Args:
        title (str): The text displayed for the social link.
        uri (str): The URI of the social link.

    Attributes:
        title (str): The text displayed for the social link.
        uri (str): The URI of the social link.
    """

    def __init__(self, title: str, uri: str) -> None:
        self.title = title
        self.uri = uri
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.ExperienceSocialLink uri=\"{self.uri}\">"

exeperience_age_rating_strings = {
    "AGE_RATING_UNSPECIFIED": ExperienceAgeRating.Unspecified,
    "AGE_RATING_ALL": ExperienceAgeRating.AllAges,
    "AGE_RATING_9_PLUS": ExperienceAgeRating.NinePlus,
    "AGE_RATING_13_PLUS": ExperienceAgeRating.ThirteenPlus,
    "AGE_RATING_17_PLUS": ExperienceAgeRating.SeventeenPlus,
}

class Place():
    """
    Represents a place within an experience on Roblox.
    
    !!! warning
        This class isn't designed to be created by users. It is returned by \
        [`Experience.get_place()`][rblxopencloud.Experience.get_place].
    
    Attributes:
        id (int): The place's ID.
        experience (Experience): The experience this place is a part of.
        name (str): The place's name.
        description (str): The place's description.
        created_at (datetime): The time the place was created.
        updated_at (datetime): The time the place was last updated.
        server_size (str): The number of players the can be in a single server.
    """

    def __init__(self, id, data, api_key, experience) -> None:
        self.id: int = id
        self.experience: Experience = experience
        self.name: Optional[str] = data["displayName"] if data else None
        self.description: Optional[str] = data["description"] if data else None
        self.created_at: Optional[datetime] = (
            parser.parse(data["createTime"])
            if data else None
        )
        self.updated_at: Optional[datetime] = (
            parser.parse(data["updateTime"])
            if data else None
        )

        self.server_size: Optional[str] = data["serverSize"] if data else None
        self.__api_key = api_key
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.Place id={self.id} \
experience={repr(self.experience)}>"
    
    def __update_params(self, data):
        self.name = data["displayName"]
        self.description = data["description"]
        self.created_at = parser.parse(data["createTime"])
        self.updated_at = parser.parse(data["updateTime"])
        self.server_size = data["serverSize"]
    
    def fetch_info(self) -> "Place":
        """
        Fetches the places's information and fills the Place object parameters.

        Returns:
            The place object with parameters filled.
        """
        
        _, data, _ = send_request("GET",
            f"cloud/v2/universes/{self.experience.id}/places/{self.id}",
            authorization=self.__api_key, expected_status=[200]
        )

        self.__update_params(data)
        return self
    
    def update(
            self, name: str = None, description: str = None,
            server_size: int = None
        ) -> "Place":
        """
        Updates information for the place and fills the empty parameters.

        Args:
            name: The new name for the place.
            description: The new description for the place.
            server_size: The new server size for the place.
        
        Returns:
            The place object with the empty parameters filled.
        """

        payload, field_mask = {}, []

        if name:
            payload["displayName"] = name
            field_mask.append("displayName")

        if description:
            payload["description"] = description
            field_mask.append("description")

        if server_size:
            payload["serverSize"] = server_size
            field_mask.append("serverSize")
        
        _, data, _ = send_request("PATCH",
            f"cloud/v2/universes/{self.experience.id}/places/{self.id}",
            authorization=self.__api_key, expected_status=[200],
            json=payload, params={"updateMask": ",".join(field_mask)}
        )
        
        self.__update_params(data)

        return self
    
    def upload_place_file(
            self, file: io.BytesIO, publish: bool = False
        ) -> int:
        """
        Uploads the place file to Roblox, optionally choosing to publish it.

        Args:
            file: The place file to upload, opened in bytes.
            publish: Wether to publish the new place file.

        Returns:
            The place's new version ID.
        """

        _, data, _ = send_request("POST",
            f"universes/v1/{self.experience.id}/places/{self.id}/versions",
            authorization=self.__api_key, expected_status=[200],
            headers={"content-type": "application/octet-stream"}, params={
                "versionType": "Published" if publish else "Saved"
            }, data=file.read()
        )
        
        return data["versionNumber"]

    # def list_root_children(self) -> Operation[list[InstanceType]]:
    #     _, data, _ = send_request("GET", "cloud/v2/universes/"+
    #         f"{self.experience.id}/places/{self.id}/instances/"+
    #         "root:listChildren", authorization=self.__api_key,
    #         expected_status=[200])
        
    #     def operation_callable(response):
    #         instance_objects = []
            
    #         for instance in response["instances"]:
    #             instance_objects.append(
    #                 Instance._determine_instance_subclass(data)
    #                 (instance["engineInstance"]["Id"], instance,
    #                     place=self, api_key=self.__api_key)
    #             )

    #         return instance_objects

    #     return Operation(f"cloud/v2/{data['path']}", self.__api_key,
    #                      operation_callable)

    # def fetch_instance(self, instance_id: str) -> Operation[InstanceType]:

    #     _, data, _ = send_request("GET", "cloud/v2/universes/"+
    #         f"{self.experience.id}/places/{self.id}/instances/{instance_id}",
    #         authorization=self.__api_key, expected_status=[200])
        
    #     return Operation(f"cloud/v2/{data['path']}", self.__api_key,
    #         lambda r: Instance._determine_instance_subclass(r)
    #         (r["engineInstance"]["Id"], r, place=self, api_key=self.__api_key))

class Experience():
    """
    Represents an experience/universe on Roblox.

    Args:
        id: The experience/universe ID
        api_key: The API key created on the \
        [Creator Dashboard](https://create.roblox.com/credentials) with \
        access to the experience.
    
    Attributes:
        id (int): The experience/universe ID
        owner (Optional[Union[User, Group]]): The experience's owner.
        name (Optional[str]): The experience's name. 
        description (Optional[str]): The experience's description. 
        created_at (Optional[datetime]): When the experience was created. 
        updated_at (Optional[datetime]): When the experience was last updated. 
        public (Optional[bool]): Whether the game is public. 
        voice_chat_enabled (Optional[bool]): Whether voice chat is enabled. 
        age_rating (Optional[ExperienceAgeRating]: The experience's age rating.
        private_server_price (Optional[int]): The price in robux of private \
        servers, will be `None` if private servers are disabled. 
        desktop_enabled (Optional[bool]): Whether the game can be played on \
        desktop. 
        mobile_enabled (Optional[bool]): Whether the game can be played on \
        phones. 
        tablet_enabled (Optional[bool]): Whether the game can be played on \
        tablets. 
        console_enabled (Optional[bool]): Whether the game can be played on \
        consoles. 
        vr_enabled (Optional[bool]): Wether the game can be played on VR \
        headsets. 
        facebook_social_link (Optional[ExperienceSocialLink]): The Facebook \
        social link, if there is one. 
        twitter_social_link (Optional[ExperienceSocialLink]): The Twitter \
        social link, if there is one. 
        youtube_social_link (Optional[ExperienceSocialLink]): The YouTube \
        social link, if there is one. 
        twitch_social_link (Optional[ExperienceSocialLink]): The Twitch \
        social link, if there is one. 
        discord_social_link (Optional[ExperienceSocialLink]): The Discord \
        social link, if there is one. 
        group_social_link (Optional[ExperienceSocialLink]): The Group social \
        link, if there is one. 
        guilded_social_link (Optional[ExperienceSocialLink]): The Guilded \
        social link, if there is one. 
    """

    def __init__(self, id: int, api_key: str):
        self.id: int = id
        self.__api_key: str = api_key

        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        self.owner: Optional[Union[User, Group]] = None
        self.public: Optional[bool] = None
        self.voice_chat_enabled: Optional[bool] = None
        self.age_rating: Optional[ExperienceAgeRating] = None
        self.private_server_price: Optional[int] = None
        self.desktop_enabled: Optional[bool] = None
        self.mobile_enabled: Optional[bool] = None
        self.tablet_enabled: Optional[bool] = None
        self.console_enabled: Optional[bool] = None
        self.vr_enabled: Optional[bool] = None

        self.facebook_social_link: Optional[ExperienceSocialLink] = None
        self.twitter_social_link: Optional[ExperienceSocialLink] = None
        self.youtube_social_link: Optional[ExperienceSocialLink] = None
        self.twitch_social_link: Optional[ExperienceSocialLink] = None
        self.discord_social_link: Optional[ExperienceSocialLink] = None
        self.group_social_link: Optional[ExperienceSocialLink] = None
        self.guilded_social_link: Optional[ExperienceSocialLink] = None
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.Experience id={self.id}>"
    
    def __update_params(self, data):
        self.name = data["displayName"]
        self.description = data["description"]

        self.created_at = (
            parser.parse(data["createTime"])
            if data.get("createTime") else None
        )
        self.updated_at = (
            parser.parse(data["updateTime"])
            if data.get("updateTime") else None
        )

        if data.get("user"):
            self.owner = User(
                int(data["user"].split("/")[1]), self.__api_key
            )
        elif data.get("group"):
            self.owner = Group(
                int(data["group"].split("/")[1]), self.__api_key
            )
        else:
            self.owner = None
        
        self.public = data["visibility"] == "PUBLIC"
        self.voice_chat_enabled = data["voiceChatEnabled"]
        self.private_server_price = data.get("privateServerPriceRobux",)
        self.age_rating = exeperience_age_rating_strings.get(
            data["ageRating"], ExperienceAgeRating.Unknown)

        self.facebook_social_link = ExperienceSocialLink(
            data["facebookSocialLink"]["title"],
            data["facebookSocialLink"]["uri"]
        ) if data.get("facebookSocialLink") else None

        self.twitter_social_link = ExperienceSocialLink(
            data["twitterSocialLink"]["title"],
            data["twitterSocialLink"]["uri"]
        ) if data.get("twitterSocialLink") else None
                
        self.youtube_social_link = ExperienceSocialLink(
            data["youtubeSocialLink"]["title"],
            data["youtubeSocialLink"]["uri"]
        ) if data.get("youtubeSocialLink") else None
            
        self.twitch_social_link = ExperienceSocialLink(
            data["twitchSocialLink"]["title"],
            data["twitchSocialLink"]["uri"]
        ) if data.get("twitchSocialLink") else None
            
        self.discord_social_link = ExperienceSocialLink(
            data["discordSocialLink"]["title"],
            data["discordSocialLink"]["uri"]
        ) if data.get("discordSocialLink") else None
            
        self.group_social_link = ExperienceSocialLink(
            data["robloxGroupSocialLink"]["title"],
            data["robloxGroupSocialLink"]["uri"]
        ) if data.get("robloxGroupSocialLink") else None
            
        self.guilded_social_link = ExperienceSocialLink(
            data["guildedSocialLink"]["title"],
            data["guildedSocialLink"]["uri"]
        ) if data.get("guildedSocialLink") else None
            
        self.desktop_enabled = data["desktopEnabled"]
        self.mobile_enabled = data["mobileEnabled"]
        self.tablet_enabled = data["tabletEnabled"]
        self.console_enabled = data["consoleEnabled"]
        self.vr_enabled = data["vrEnabled"]
    
    def fetch_info(self) -> "Experience":
        """
        Fetches the experience's information and fills the experience object \
        parameters.

        Returns:
            The experience object with parameters filled.
        """

        _, data, _ = send_request("GET", f"cloud/v2/universes/{self.id}",
            expected_status=[200], authorization=self.__api_key
        )

        self.__update_params(data)
        return self
    
    def update(
            self, voice_chat_enabled: bool = None,
            private_server_price: Union[int, bool] = None,
            desktop_enabled: bool = None, mobile_enabled: bool = None,
            tablet_enabled: bool = None, console_enabled: bool = None,
            vr_enabled: bool = None,
            facebook_social_link: Union[ExperienceSocialLink, bool] = None,
            twitter_social_link: Union[ExperienceSocialLink, bool] = None,
            youtube_social_link: Union[ExperienceSocialLink, bool] = None,
            twitch_social_link: Union[ExperienceSocialLink, bool] = None,
            discord_social_link: Union[ExperienceSocialLink, bool] = None,
            group_social_link: Union[ExperienceSocialLink, bool] = None,
            guilded_social_link: Union[ExperienceSocialLink, bool] = None
        ) -> "Experience":
        """
        Updates the experience information and fills the experience object \
        parameters.

        Args:
            voice_chat_enabled: Whether voice chat is enabled.
            private_server_price: The price in robux for the private server. \
            Set this to `False` to disable private servers.
            desktop_enabled: Whether the experience can be played on desktop.
            mobile_enabled: Whether the experience can be played on phones.
            console_enabled: Wehther the experience can be played on consoles.
            vr_enabled: Whether the experience can be played on VR headsets.
            facebook_social_link: The experience's Facebook social link.
            twitter_social_link: The experience's Twitter social link.
            youtube_social_link: The experience's YouTube social link.
            twitch_social_link: The experience's Twitch social link.
            discord_social_link: The experience's Discord social link.
            group_social_link: The experience's Roblox group social link.
            guilded_social_link: The experience's Guilded social link.

        Returns:
            The experience object with parameters filled.

        !!! tip
            To update the experience's name or description use \
            [`Place.update`][rblxopencloud.Place.update] on the experience's \
            start place.
        """

        payload, field_mask = {}, []

        if voice_chat_enabled != None:
            payload["voiceChatEnabled"] = voice_chat_enabled
            field_mask.append("voiceChatEnabled")

        if private_server_price != None:
            if private_server_price == True: raise ValueError(
                "private_server_robux_price should be either int or False."
            )

            if type(private_server_price) == int:
                payload["privateServerPriceRobux"] = (
                    private_server_price
                )
            
            field_mask.append("privateServerPriceRobux")

        # iterate through all the social links and add them into the payload
        for platform, value in {
            "facebook": facebook_social_link,  "twitter": twitter_social_link,
            "youtube": youtube_social_link, "twitch": twitch_social_link,
            "discord": discord_social_link, "robloxGroup": group_social_link,
            "guilded": guilded_social_link
        }.items():
            # ignore parameters with a value of None
            if value != None:
                if value == True: raise ValueError(
                    f"{platform}_social_link should be either \
                    ExperienceSocialLink or False."
                )

                if type(value) == ExperienceSocialLink:
                    payload[f"{platform}SocialLink"] = {
                        "title": value.title,
                        "uri": value.uri
                    }
                    field_mask.append(f"{platform}SocialLink.title")
                    field_mask.append(f"{platform}SocialLink.uri")
                else:
                    # any social link is being removed
                    field_mask.append(f"{platform}SocialLink")

        for platform, value in {
            "desktop": desktop_enabled, "mobile": mobile_enabled,
            "tablet": tablet_enabled, "console": console_enabled,
            "vr": vr_enabled
        }.items():
            if value != None:
                payload[f"{platform}Enabled"] = value
                field_mask.append(f"{platform}Enabled")
        
        _, data, _ = send_request("PATCH",
            f"cloud/v2/universes/{self.id}",
            authorization=self.__api_key, expected_status=[200],
            params={"updateMask": ",".join(field_mask)}, json=payload
        )

        self.__update_params(data)
        return self
    
    def get_place(self, place_id: int) -> Place:
        """
        Creates a [`Place`][rblxopencloud.Place] class for a place within the \
        experience. Does not make any API calls.

        Args:
            place_id: The ID of the place.

        Returns:
            The created place object with all parameters as `None` except \
            `id` and `experience`.
        """
        
        return Place(place_id, None, self.__api_key, self)
    
    def get_data_store(
            self, name: str, scope: Optional[str] = "global"
        ) -> DataStore:
        """
        Creates a [`DataStore`][rblxopencloud.DataStore] with the provided \
        name and scope.

        Args:
            name: The data store name.
            scope: The data store scope. Use `None` for `scope/key` syntax.

        Returns:
            The created data store object with `DataStore.created` as `None`.
        """
        
        return DataStore(name, self, self.__api_key, None, scope)
    
    def get_ordered_data_store(
            self, name: str, scope: Optional[str] = "global"
        ) -> OrderedDataStore:
        """
        Creates an [`OrderedDataStore`][rblxopencloud.OrderedDataStore] with \
        the provided name and scope.

        Args:
            name: The data store name.
            scope: The data store scope. Use `None` for `scope/key` syntax.

        Returns:
            The created data store object.
        """
        
        return OrderedDataStore(name, self, self.__api_key, scope)

    def list_data_stores(
            self, prefix: str = "", limit: int = None,
            scope: Optional[str] = "global"
        ) -> Iterable[DataStore]:
        """
        Iterates all data stores in the experience.

        Args:
            prefix: Filters data stores to those which start with prefix.
            limit: The maximum number of Data Stores to iterate.
            scope: The scope data stores should have. Can be `None` for key \
            syntax like `scope/key`.
        
        Yields:
            [`DataStore`][rblxopencloud.DataStore] for every datastore in the \
            experience.
        """
        
        for entry in iterate_request("GET",
            f"datastores/v1/universes/{self.id}/standard-datastores",
            authorization=self.__api_key, expected_status=[200],
            params={"prefix": prefix},
            max_yields=limit, data_key="datastores", cursor_key="cursor"
        ):
            yield DataStore(entry["name"], self, self.__api_key,
                entry["createdTime"], scope)
    
    def publish_message(self, topic: str, data: str) -> None:
        """
        Publishes a message to live game servers that can be recieved with \
        [MessagingService](https://create.roblox.com/docs/reference/engine/\
classes/MessagingService).

        Args:
            topic: The topic to publish the message into.
            data: The message to send. Open Cloud only supports string data, \
            not tables. 
        
        !!! note
            Messages sent by Open Cloud with only be recieved by live \
            servers. Studio won't recieve thesse messages.
        """

        topic = urllib.parse.quote(topic)

        send_request("POST",
            f"messaging-service/v1/universes/{self.id}/topics/{topic}",
            authorization=self.__api_key, expected_status=[200], json={
                "message": data
            }
        )
        
    def send_notification(self, user_id: int, message_id: str, 
            launch_data: str = None, analytics_category: str = None,
            **message_variables: dict[str, Union[str, int]]
        ) -> None:
        """
        Sends an Experience notification to the requested user.

        Args:
            user_id: The user to recieve the notification.
            message_id: The notification string ID.
            analytics_category: The category string used for analytics.
            launch_data: The launch data used if the player joins.
            **message_variables: values to fill variables in the notification \
            string.
        """

        # format params the way roblox expects {key: {"int64_value": value}}
        parameters_dict = {}
        for key, value in message_variables.items():
            parameters_dict[key] = {
                "int64_value" if type(value) == int else "string_value": value
            }
        
        send_request("POST",
            f"cloud/v2/users/{user_id}/notifications",
            authorization=self.__api_key, expected_status=[200], json={
                "source": {
                    "universe": f"universes/{self.id}"
                },
                "payload": {
                    "type": "MOMENT",
                    "messageId": message_id,
                    "parameters": parameters_dict,
                    "joinExperience": {
                        "launchData": launch_data
                    } if launch_data else None,
                    "analyticsData": {
                        "category": analytics_category
                    } if analytics_category else None
                }
            }
        )
    
    def restart_servers(self) -> None:
        """
        Shutdowns all game servers in the experience which are not on the \
        latest published version. Similar to the 'Migrate To Latest Update' \
        button on the game page.
        """

        send_request("POST",
            f"cloud/v2/universes/{self.id}:restartServers",
            authorization=self.__api_key, expected_status=[200]
        )
