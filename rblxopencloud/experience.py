import io
from typing import Optional, Iterable, Union
from .datastore import DataStore, OrderedDataStore
from . import send_request, iterate_request
from .user import User
from .group import Group
from enum import Enum
from dateutil import parser
from datetime import datetime
import urllib.parse
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
    Represents a place within an experience on Roblox. Currently only holds place information, and can only be updated with [`Experience.update_place()`][rblxopencloud.Experience.update_place].
    
    !!! warning
        This class isn't designed to be created by users. It is returned by [`Experience.fetch_place()`][rblxopencloud.Experience.fetch_place], and [`Experience.update_place()`][rblxopencloud.Experience.update_place].
    
    Attributes:
        id (int): The place's ID.
        experience (Experience): The experience this place is a part of.
        name (str): The place's name.
        description (str): The place's description.
        created_at (datetime): The time the place was created.
        updated_at (datetime): The time the place was last updated.
        server_size (str): The maximum number of players that can be in a single server.
    """

    def __init__(self, data, api_key, experience) -> None:
        self.id: int = int(data['path'].split("/")[-1])
        self.experience: Experience = experience
        self.name: str = data["displayName"]
        self.description: str = data["description"]
        self.created_at: datetime = parser.parse(data["createTime"])
        self.updated_at: datetime = parser.parse(data["updateTime"])
        self.server_size: str = data["serverSize"]
        self.__api_key = api_key
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.Place id={self.id}, \
experience={repr(self.experience)}>"

class Experience():
    """
    Represents an experience/game on Roblox. Allows interaction with data stores, messaging service, etc.

    Args:
        id: The experience/universe ID
        api_key: The API key created on the [Creator Dashboard](https://create.roblox.com/credentials) with access to the experience.
    
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
    
    def update(self, voice_chat_enabled: bool = None,
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
            [`Experience.update_place`][rblxopencloud.Experience.\
            update_place] on the experience's start place.
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

        for platform, value in {
            "facebook": facebook_social_link,  "twitter": twitter_social_link,
            "youtube": youtube_social_link, "twitch": twitch_social_link,
            "discord": discord_social_link, "robloxGroup": group_social_link,
            "guilded": guilded_social_link
        }.items():
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
                    field_mask.append(f"{platform}SocialLink")

        for platform, value in {
            "desktop": desktop_enabled, "mobile": mobile_enabled,
            "tablet": tablet_enabled, "console": console_enabled,
            "vr": vr_enabled
        }.items():
            if value != None:
                payload[f"{platform}Enabled"] = value
                field_mask.append(f"{platform}Enabled")
        
        _, data, _ = send_request("PATCH", f"cloud/v2/universes/{self.id}",
            authorization=self.__api_key, expected_status=[200],
            json=payload, params={"updateMask": ",".join(field_mask)}
        )

        self.__update_params(data)
        return self
    
    def get_data_store(self, name: str, scope: Optional[str] = "global"
        ) -> DataStore:
        """
        Creates a [`rblxopencloud.DataStore`][rblxopencloud.DataStore] with \
        the provided name and scope.

        Args:
            name: The data store name.
            scope: The data store scope. Use `None` for `scope/key` syntax.

        Returns:
            The created data store object with `DataStore.created` as `None`.
        """
        
        return DataStore(name, self, self.__api_key, None, scope)
    
    def get_ordered_data_store(self, name: str, scope: Optional[str] = "global"
        ) -> OrderedDataStore:
        """
        Creates a [`rblxopencloud.OrderedDataStore`]\
        [rblxopencloud.OrderedDataStore] with the provided name and scope.

        Args:
            name: The data store name.
            scope: The data store scope. Use `None` for `scope/key` syntax.

        Returns:
            The created data store object.
        """
        
        return OrderedDataStore(name, self, self.__api_key, scope)

    def list_data_stores(self, prefix: str="", limit: int=None,
        scope: Optional[str] = "global") -> Iterable[DataStore]:
        """
        Iterates all data stores in the experience.

        Args:
            prefix: Filters data stores to those which start with prefix.
            limit: The maximum number of Data Stores to iterate.
            scope: The scope data stores should have. Can be `None` for key \
            syntax like `scope/key`.
        
        Yields:
            [`rblxopencloud.DataStore`][rblxopencloud.DataStore]s in the \
            experience.
        """
        
        for entry in iterate_request("GET",
            f"datastores/v1/universes/{self.id}/standard-datastores",
            authorization=self.__api_key, params={"prefix": prefix},
            expected_status=[200], max_yields=limit,
            data_key="datastores", cursor_key="cursor",
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
            data: The message to send. Open Cloud only support string data, \
            not tables. 
        
        !!! note
            Messages sent by Open Cloud with only be recieved by live \
            servers. Studio won't recieve thesse messages.
        """

        send_request("POST", f"messaging-service/v1/universes/{self.id}/"+
            f"topics/{urllib.parse.quote(topic)}", expected_status=[200],
            authorization=self.__api_key, json={"message": data}
        )
    
    def fetch_place(self, place_id: int) -> Place:
        """
        Fetches the information of a place within the expereince.

        Args:
            place_id: The place ID to fetch information for.

        Returns:
            The place information.
        """
        
        _, data, _ = send_request("GET",
            f"cloud/v2/universes/{self.id}/places/{place_id}",
            authorization=self.__api_key, expected_status=[200]
        )

        return Place(data, self.__api_key, self)
    
    def update_place(self, place_id: int, name: str = None,
        description: str = None, server_size: int = None) -> Place:
        """
        Updates information for a place within the experience.

        Args:
            place_id: The place ID to update.
            name: The new name for the place.
            description: The new description for the place.
            server_size: The new server size for the place.
        
        Returns:
            The updated place.
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
            f"cloud/v2/universes/{self.id}/places/{place_id}",
            authorization=self.__api_key, expected_status=[200],
            json=payload, params={"updateMask": ",".join(field_mask)}
        )

        return Place(data, self.__api_key, self)
    
    def upload_place(self, place_id: int, file: io.BytesIO,
            publish: bool = False) -> int:
        """
        Uploads the place file to Roblox, optionally choosing to publish it.

        Args:
            place_id: The place ID to upload the file to.
            file: The place file to upload, opened in bytes.
            publish: Wether to publish the new place file.

        Returns:
            The place's new version ID.
        """

        _, data, _ = send_request("POST",
            f"universes/v1/{self.id}/places/{place_id}/versions",
            authorization=self.__api_key, expected_status=[200],
            headers={"content-type": "application/octet-stream"},
            data=file.read(), params={
                "versionType": "Published" if publish else "Saved"
            }
        )
        
        return data["versionNumber"]
    
    def send_notification(self, user_id: int, message_id: str, 
            analytics_category: str = None, launch_data: str = None,
            **message_variables: dict[str, Union[str, int]]) -> None:
        """
        Sends an experience notification to the requested user.

        Args:
            user_id: The user to recieve the notification.
            message_id: The notification string ID.
            analytics_category: The category string used for analytics.
            launch_data: The launch data used if the player joins.
            **message_variables: values to fill variables in the notification \
            string.
        """

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
    