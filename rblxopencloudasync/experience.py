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

import io
import urllib.parse
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Optional, Union

from dateutil import parser

from .datastore import DataStore, OrderedDataStore
from .group import Group
from .http import Operation, iterate_request, send_request
from .memorystore import MemoryStoreQueue, SortedMap
from .user import User

__all__ = (
    "Experience",
    "ExperienceAgeRating",
    "ExperienceSocialLink",
    "PaymentProvider",
    "Place",
    "Platform",
    "Subscription",
    "SubscriptionExpirationReason",
    "SubscriptionState",
    "UserRestriction",
)


class Platform(Enum):
    """
    Enum representing a platform, currently used for \
    [`Subscription`][rblxopencloud.Subscription].
    
    Attributes:
        Unknown (0): The platform is unknown or not specified. 
        Desktop (1):
        Mobile (2): 
    """

    Unknown = 0
    Desktop = 1
    Mobile = 2


PLATFORM_STRINGS = {"DESKTOP": Platform.Desktop, "MOBILE": Platform.Mobile}


class PaymentProvider(Enum):
    """
    Enum representing a payment provider, currently used for \
    [`Subscription`][rblxopencloud.Subscription].
    
    Attributes:
        Unknown (0): The provider is unknown or not specified. 
        RobloxCredit (1):
        Stripe (2): 
        Google (3): 
        Apple (4): 
    """

    Unknown = 0
    RobloxCredit = 1
    Stripe = 2
    Google = 3
    Apple = 4


PAYMENT_PROVIDER_STRINGS = {
    "ROBLOX_CREDIT": PaymentProvider.RobloxCredit,
    "STRIPE": PaymentProvider.Stripe,
    "GOOGLE": PaymentProvider.Google,
    "APPLE": PaymentProvider.Apple,
}


class SubscriptionState(Enum):
    """
    Enum representing the current state of a \
    [`Subscription`][rblxopencloud.Subscription].

    Attributes:
        Unknown (0): The current state is unknown or unspecified.
        Active (1): The subscription is active and set to renew.
        PendingCancelation (2): The subscription is active but will not renew.
        PendingRenewal (3): The subscription is currently in the grace period \
        and pending payment confirmation.
        Expired (4): The subscription has expired.
    """

    Unknown = 0
    Active = 1
    PendingCancelation = 2
    PendingRenewal = 3
    Expired = 4


SUBSCRIPTION_STATE_STRINGS = {
    "SUBSCRIBED_WILL_RENEW": SubscriptionState.Active,
    "SUBSCRIBED_WILL_NOT_RENEW": SubscriptionState.PendingCancelation,
    "SUBSCRIBED_RENEWAL_PAYMENT_PENDING": SubscriptionState.PendingRenewal,
    "EXPIRED": SubscriptionState.Expired,
}


class SubscriptionExpirationReason(Enum):
    """
    Enum representing the reason why a \
    [`Subscription`][rblxopencloud.Subscription] expired.
    
    Attributes:
        Unknown (0): The expiration reason is unknown or not specified. 
        Cancelled (1): The subscribing user cancelled the subscription.
        Refunded (2): The subscribing user requested a refund for the \
        subscription.
        Lapsed (3): Payment was not recieved when the subscription was renewed.
        ProductInactive (4): The subscription product was set to inactive.
        ProductDeleted (5): The subscription product was deleted.
    """

    Unknown = 0
    Cancelled = 1
    Refunded = 2
    Lapsed = 3
    ProductInactive = 4
    ProductDeleted = 5


SUBSCRIPTION_EXPIRATION_REASON_STRINGS = {
    "PRODUCT_INACTIVE": SubscriptionExpirationReason.ProductInactive,
    "PRODUCT_DELETED": SubscriptionExpirationReason.ProductDeleted,
    "SUBSCRIBER_CANCELLED": SubscriptionExpirationReason.Cancelled,
    "SUBSCRIBER_REFUNDED": SubscriptionExpirationReason.Refunded,
    "LAPSED": SubscriptionExpirationReason.Lapsed,
}


class Subscription:
    """
    Represents a subscription to a subscription product.

    Attributes:
        user_id: The user ID, or the subscription ID of this subscription.
        product_id: The ID of the subscription product.
        active: Wether the subscription is currently active (not expired).
        will_renew: Wether the subscription will renew after `period_end_at`.
        state: The subscriptions's current state.
        created_at: The time the subscription was created at (subscribed at).
        updated_at: The time the subscription was last updated at.
        last_billed_at: The time the user last payed for the subscription.
        period_end_at: The time the current billing period ends at. If active \
        this is when the subscription will renew at and if not active is when \
        the subscription will expire at.
        payment_provider: The user's payment provider for this subscription.
        purchase_platform: The platform the subscription was started on.
        expiration_reason: The reason the subscription expired.
    """

    def __init__(self, data) -> None:
        self.user_id: int = int(data["path"].split("/")[5])
        self.product_id: str = data["path"].split("/")[3]

        self.active: bool = data["active"]
        self.will_renew: bool = data["willRenew"]
        self.state: SubscriptionState = SUBSCRIPTION_STATE_STRINGS.get(
            data["state"], SubscriptionState.Unknown
        )

        self.created_at: datetime = parser.parse(data["createTime"])
        self.updated_at: datetime = parser.parse(data["updateTime"])
        self.last_billed_at: datetime = parser.parse(data["lastBillingTime"])
        self.period_end_at: datetime = (
            parser.parse(data["expireTime"])
            if data.get("expireTime")
            else parser.parse(data["nextRenewTime"])
        )

        self.payment_provider: PaymentProvider = PAYMENT_PROVIDER_STRINGS.get(
            data["paymentProvider"], PaymentProvider.Unknown
        )

        self.purchase_platform: Platform = PLATFORM_STRINGS.get(
            data["purchasePlatform"], Platform.Unknown
        )

        # Only provide an expiration reason if expired or a reason is specified
        self.expiration_reason: Optional[SubscriptionExpirationReason] = (
            SUBSCRIPTION_EXPIRATION_REASON_STRINGS.get(
                data["expirationDetails"]["reason"],
                SubscriptionExpirationReason.Unknown,
            )
            if (
                data.get("expirationDetails", {}).get("reason")
                and (
                    self.state == SubscriptionState.Expired
                    or (
                        data["expirationDetails"]["reason"]
                        != "EXPIRATION_REASON_UNSPECIFIED"
                    )
                )
            )
            else None
        )

    def __repr__(self) -> str:
        return f'<rblxopencloud.Subscription user_id={self.user_id} \
product_id="{self.product_id}" state={self.state}>'


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


class ExperienceSocialLink:
    """
    Represents a social link in an experience.

    Args:
        title: The text displayed for the social link.
        uri: The URI of the social link.

    Attributes:
        title: The text displayed for the social link.
        uri: The URI of the social link.
    """

    def __init__(self, title: str, uri: str) -> None:
        self.title = title
        self.uri = uri

    def __repr__(self) -> str:
        return f'<rblxopencloud.ExperienceSocialLink uri="{self.uri}">'


EXPERIENCE_AGE_RATING_STRINGS = {
    "AGE_RATING_UNSPECIFIED": ExperienceAgeRating.Unspecified,
    "AGE_RATING_ALL": ExperienceAgeRating.AllAges,
    "AGE_RATING_9_PLUS": ExperienceAgeRating.NinePlus,
    "AGE_RATING_13_PLUS": ExperienceAgeRating.ThirteenPlus,
    "AGE_RATING_17_PLUS": ExperienceAgeRating.SeventeenPlus,
}


class UserRestriction:
    """
    Represents a user restriction (or ban) within an experience or place on \
    Roblox.
        
    Attributes:
        place: The place object this restriction belongs to. `None` if it is \
        universe-wide.
        user: The user object that this restriction relates to.
        active: Whether the restriction is currently active.
        display_reason: The reason for this restriction shown to the client.
        private_reason: The reason for this restriction never shwon to the \
        client. Can be used to store sensitive information about the ban.
        inherited: For bans specific to a place, whether the ban was \
        inherited from a universe-wide ban.
        exclude_alt_accounts: Whether the ban should not attempt to prevent \
        alternate accounts.
        duration_seconds: The number of seconds this restriction is for. \
        `None` means it is indefinite or not active.
        start_timestamp: The timestamp this restriction started at.
        issuer_user_id: Only for \
        [`Experience.list_ban_logs`][rblxopencloud.Experience.list_ban_logs], \
        the user ID identified to have issued the ban. `None` if issued by a \
        game script.
    """

    def __init__(self, data, api_key, place=None) -> None:
        if data.get("path"):
            if "places" not in data["path"].split("/"):
                self.place: Optional[Place] = None
            elif place:
                self.place: Optional[Place] = place
            else:
                self.place: Optional[Place] = Place(
                    int(data["path"].split("/")[3]), None, api_key, None
                )
        elif data.get("place"):
            self.place: Optional[Place] = Place(
                int(data["place"].split("/")[-1]), None, api_key, None
            )

        self.user: User = User(int(data["user"].split("/")[1]), api_key)

        if data.get("path"):
            restriction_info = data["gameJoinRestriction"]
            self.issuer_user_id: Optional[int] = None
        else:
            restriction_info = data

            self.issuer_user_id: Optional[int] = (
                int(restriction_info["moderator"]["robloxUser"].split("/")[-1])
                if restriction_info["moderator"].get("robloxUser")
                else None
            )

        self.active: bool = restriction_info["active"]

        self.display_reason: str = restriction_info["displayReason"]
        self.private_reason: str = restriction_info["privateReason"]
        self.inherited: Optional[bool] = restriction_info.get("inherited")
        self.exclude_alt_accounts: bool = restriction_info[
            "excludeAltAccounts"
        ]

        duration = restriction_info.get("duration")
        self.duration_seconds: Optional[int] = (
            duration
            if not (type(duration) == str and duration.endswith("s"))
            else int(duration[0:-1])
        )
        self.start_timestamp: Optional[datetime] = (
            parser.parse(restriction_info["startTime"])
            if restriction_info.get("startTime")
            else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.UserRestriction active={self.active} \
user={repr(self.user)}>"


class Place:
    """
    Represents a place within an experience on Roblox.

    Attributes:
        id: The place's ID.
        experience: The experience this place is a part of.
        name: The place's name.
        description: The place's description.
        created_at: The time the place was created.
        updated_at: The time the place was last updated.
        server_size: The number of players the can be in a single server.
    """

    def __init__(self, id, data, api_key, experience) -> None:
        self.id: int = id
        self.experience: Experience = experience
        self.name: Optional[str] = data["displayName"] if data else None
        self.description: Optional[str] = data["description"] if data else None
        self.created_at: Optional[datetime] = (
            parser.parse(data["createTime"]) if data else None
        )
        self.updated_at: Optional[datetime] = (
            parser.parse(data["updateTime"]) if data else None
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

        return self

    async def fetch_info(self) -> "Place":
        """
        Fetches the places's information and fills the Place object parameters.

        Returns:
            The place object with parameters filled.
        """

        _, data, _ = await send_request(
            "GET",
            f"/universes/{self.experience.id}/places/{self.id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return self.__update_params(data)

    async def update(
        self,
        name: str = None,
        description: str = None,
        server_size: int = None,
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

        payload, field_mask = {
            "displayName": name,
            "description": description,
            "serverSize": server_size,
        }, []

        if name:
            field_mask.append("displayName")
        if description:
            field_mask.append("description")
        if server_size:
            field_mask.append("serverSize")

        _, data, _ = await send_request(
            "PATCH",
            f"/universes/{self.experience.id}/places/{self.id}",
            authorization=self.__api_key,
            expected_status=[200],
            json=payload,
            params={"updateMask": ",".join(field_mask)},
        )

        return self.__update_params(data)

    async def upload_place_file(
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

        _, data, _ = await send_request(
            "POST",
            f"universes/v1/{self.experience.id}/places/{self.id}\
/versions",
            authorization=self.__api_key,
            expected_status=[200],
            headers={"content-type": "application/octet-stream"},
            params={"versionType": "Published" if publish else "Saved"},
            data=file.read(),
        )

        return data["versionNumber"]

    async def fetch_user_restriction(self, user_id: int) -> UserRestriction:
        """
        Fetches the current restriction information for the specific place.

        Args:
            user_id: The user ID to fetch restriction information for.

        Returns:
            The current restriction information for the requested user.
        """

        _, data, _ = await send_request(
            "GET",
            f"/universes/{self.experience.id}/places/{self.id}\
/user-restrictions/{user_id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return UserRestriction(data, self.__api_key)

    async def ban_user(
        self,
        user_id: int,
        duration_seconds: Optional[int],
        display_reason: str = "",
        private_reason: str = "",
        exclude_alt_accounts: bool = False,
    ) -> UserRestriction:
        """
        Updates the current user restriction for a user within the place.

        Args:
            user_id: The ID of the user to update restrictions for.
            duration_seconds: The number of seconds the ban should last. \
            Provide `None` for an indefinite restriction.
            display_reason: The reason for the ban shown to the client.
            private_reason: The reason for the ban never shown to the client.
            exclude_alt_accounts: Whether the user's detected alt accounts \
            shouldn't be banned as well.
        
        Returns:
            The updated restriction information for the requested user.
        """

        _, data, _ = await send_request(
            "PATCH",
            f"/universes/{self.experience.id}/places/{self.id}\
/user-restrictions/{user_id}",
            authorization=self.__api_key,
            expected_status=[200],
            json={
                "gameJoinRestriction": {
                    "active": True,
                    "duration": (
                        f"{duration_seconds}s" if duration_seconds else None
                    ),
                    "excludeAltAccounts": exclude_alt_accounts,
                    "displayReason": display_reason,
                    "privateReason": private_reason,
                }
            },
        )

        return UserRestriction(data, self.__api_key)

    async def unban_user(self, user_id: int) -> UserRestriction:
        """
        Removes the current user restriction for a user within the place.

        Args:
            user_id: The ID of the user to remove restrictions for.

        Returns:
            The updated restriction information for the requested user.
        """

        _, data, _ = await send_request(
            "PATCH",
            f"/universes/{self.experience.id}/places/{self.id}\
/user-restrictions/{user_id}",
            authorization=self.__api_key,
            expected_status=[200],
            json={"gameJoinRestriction": {"active": False}},
        )

        return UserRestriction(data, self.__api_key)


class Experience:
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
            if data.get("createTime")
            else None
        )
        self.updated_at = (
            parser.parse(data["updateTime"])
            if data.get("updateTime")
            else None
        )

        if data.get("user"):
            self.owner = User(int(data["user"].split("/")[1]), self.__api_key)
        elif data.get("group"):
            self.owner = Group(
                int(data["group"].split("/")[1]), self.__api_key
            )
        else:
            self.owner = None

        self.public = data["visibility"] == "PUBLIC"
        self.voice_chat_enabled = data["voiceChatEnabled"]
        self.private_server_price = data.get("privateServerPriceRobux")
        self.age_rating = EXPERIENCE_AGE_RATING_STRINGS.get(
            data["ageRating"], ExperienceAgeRating.Unknown
        )

        self.facebook_social_link = (
            ExperienceSocialLink(
                data["facebookSocialLink"]["title"],
                data["facebookSocialLink"]["uri"],
            )
            if data.get("facebookSocialLink")
            else None
        )

        self.twitter_social_link = (
            ExperienceSocialLink(
                data["twitterSocialLink"]["title"],
                data["twitterSocialLink"]["uri"],
            )
            if data.get("twitterSocialLink")
            else None
        )

        self.youtube_social_link = (
            ExperienceSocialLink(
                data["youtubeSocialLink"]["title"],
                data["youtubeSocialLink"]["uri"],
            )
            if data.get("youtubeSocialLink")
            else None
        )

        self.twitch_social_link = (
            ExperienceSocialLink(
                data["twitchSocialLink"]["title"],
                data["twitchSocialLink"]["uri"],
            )
            if data.get("twitchSocialLink")
            else None
        )

        self.discord_social_link = (
            ExperienceSocialLink(
                data["discordSocialLink"]["title"],
                data["discordSocialLink"]["uri"],
            )
            if data.get("discordSocialLink")
            else None
        )

        self.group_social_link = (
            ExperienceSocialLink(
                data["robloxGroupSocialLink"]["title"],
                data["robloxGroupSocialLink"]["uri"],
            )
            if data.get("robloxGroupSocialLink")
            else None
        )

        self.guilded_social_link = (
            ExperienceSocialLink(
                data["guildedSocialLink"]["title"],
                data["guildedSocialLink"]["uri"],
            )
            if data.get("guildedSocialLink")
            else None
        )

        self.desktop_enabled = data["desktopEnabled"]
        self.mobile_enabled = data["mobileEnabled"]
        self.tablet_enabled = data["tabletEnabled"]
        self.console_enabled = data["consoleEnabled"]
        self.vr_enabled = data["vrEnabled"]

        return self

    async def fetch_info(self) -> "Experience":
        """
        Fetches the experience's information and fills the experience object \
        parameters.

        Returns:
            The experience object with parameters filled.
        """

        _, data, _ = await send_request(
            "GET",
            f"/universes/{self.id}",
            expected_status=[200],
            authorization=self.__api_key,
        )

        return self.__update_params(data)

    async def update(
        self,
        voice_chat_enabled: bool = None,
        private_server_price: Union[int, bool] = None,
        desktop_enabled: bool = None,
        mobile_enabled: bool = None,
        tablet_enabled: bool = None,
        console_enabled: bool = None,
        vr_enabled: bool = None,
        facebook_social_link: Union[ExperienceSocialLink, bool] = None,
        twitter_social_link: Union[ExperienceSocialLink, bool] = None,
        youtube_social_link: Union[ExperienceSocialLink, bool] = None,
        twitch_social_link: Union[ExperienceSocialLink, bool] = None,
        discord_social_link: Union[ExperienceSocialLink, bool] = None,
        group_social_link: Union[ExperienceSocialLink, bool] = None,
        guilded_social_link: Union[ExperienceSocialLink, bool] = None,
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

        payload, field_mask = {
            "voiceChatEnabled": voice_chat_enabled,
            "desktopEnabled": desktop_enabled,
            "mobileEnabled": mobile_enabled,
            "tabletEnabled": tablet_enabled,
            "consoleEnabled": console_enabled,
            "vrEnabled": vr_enabled,
        }, []

        # if the key values are not None then add them to the field mask
        if voice_chat_enabled is not None:
            field_mask.append("voiceChatEnabled")
        if desktop_enabled is not None:
            field_mask.append("desktopEnabled")
        if mobile_enabled is not None:
            field_mask.append("mobileEnabled")
        if tablet_enabled is not None:
            field_mask.append("tabletEnabled")
        if console_enabled is not None:
            field_mask.append("consoleEnabled")
        if vr_enabled is not None:
            field_mask.append("vrEnabled")

        if private_server_price is not None:
            if private_server_price is True:
                raise ValueError(
                    "private_server_robux_price should be either int or False."
                )

            # omit the private server price field if False to disable them.
            if type(private_server_price) == int:
                payload["privateServerPriceRobux"] = private_server_price

            field_mask.append("privateServerPriceRobux")

        # iterate through all the social links and add them into the payload
        for platform, value in {
            "facebook": facebook_social_link,
            "twitter": twitter_social_link,
            "youtube": youtube_social_link,
            "twitch": twitch_social_link,
            "discord": discord_social_link,
            "robloxGroup": group_social_link,
            "guilded": guilded_social_link,
        }.items():
            # ignore parameters with a value of None
            if value is not None:
                if value is True:
                    raise ValueError(
                        f"{platform}_social_link should be either \
                    ExperienceSocialLink or False."
                    )

                if type(value) == ExperienceSocialLink:
                    payload[f"{platform}SocialLink"] = {
                        "title": value.title,
                        "uri": value.uri,
                    }
                    field_mask.append(f"{platform}SocialLink.title")
                    field_mask.append(f"{platform}SocialLink.uri")
                else:
                    # any social link is being removed
                    field_mask.append(f"{platform}SocialLink")

        _, data, _ = await send_request(
            "PATCH",
            f"/universes/{self.id}",
            authorization=self.__api_key,
            expected_status=[200],
            params={"updateMask": ",".join(field_mask)},
            json=payload,
        )

        return self.__update_params(data)

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

    def get_datastore(
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

    def get_ordered_datastore(
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

    async def list_datastores(
        self,
        prefix: str = "",
        limit: int = None,
        scope: Optional[str] = "global",
    ) -> AsyncGenerator[Any, DataStore]:
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

        async for entry in iterate_request(
            "GET",
            f"datastores/v1/universes/{self.id}/standard-datastores",
            authorization=self.__api_key,
            expected_status=[200],
            params={"prefix": prefix},
            max_yields=limit,
            data_key="datastores",
            cursor_key="cursor",
        ):
            yield DataStore(
                entry["name"],
                self,
                self.__api_key,
                entry["createdTime"],
                scope,
            )

    def get_sorted_map(self, name: str) -> SortedMap:
        """
        Creates a [`SortedMap`][rblxopencloud.SortedMap] with \
        the provided name. This function doesn't make an API call so there is \
        no validation.

        Args:
            name: The memory store sorted map name.
        
        Returns:
            The sorted map with the provided name.
        """

        return SortedMap(name, self, self.__api_key)

    def get_memory_store_queue(self, name: str) -> MemoryStoreQueue:
        """
        Creates a [`MemoryStoreQueue`][rblxopencloud.MemoryStoreQueue] with \
        the provided name. This function doesn't make an API call so there is \
        no validation.

        Args:
            name: The memory store queue name.
        
        Returns:
            The memory store queue with the provided name.
        """

        return MemoryStoreQueue(name, self, self.__api_key)

    async def publish_message(self, topic: str, data: str) -> None:
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

        await send_request(
            "POST",
            f"messaging-service/v1/universes/{self.id}/topics/{topic}",
            authorization=self.__api_key,
            expected_status=[200],
            json={"message": data},
        )

    async def send_notification(
        self,
        user_id: int,
        message_id: str,
        launch_data: str = None,
        analytics_category: str = None,
        **message_variables: dict[str, Union[str, int]],
    ) -> None:
        """
        Sends an Experience notification to the requested user.

        Args:
            user_id: The user to recieve the notification.
            message_id: The notification string ID.
            analytics_category: The category string used for analytics.
            launch_data: The launch data used if the player joins.
            **message_variables: values to fill variables in the notification \
            string. Message variables for user mentions should be formatted \
            as `userid_<key>`, where `<key>` is the variable key.
        """

        # format params the way roblox expects {key: {"int64_value": value}}
        parameters_dict = {}
        for key, value in message_variables.items():
            if key.startswith("userid_"):
                key = f"userId-{key[7:]}"
            parameters_dict[key] = {
                "int64_value" if type(value) == int else "string_value": value
            }

        await send_request(
            "POST",
            f"/users/{user_id}/notifications",
            authorization=self.__api_key,
            expected_status=[200],
            json={
                "source": {"universe": f"universes/{self.id}"},
                "payload": {
                    "type": "MOMENT",
                    "messageId": message_id,
                    "parameters": parameters_dict,
                    "joinExperience": (
                        {"launchData": launch_data} if launch_data else None
                    ),
                    "analyticsData": (
                        {"category": analytics_category}
                        if analytics_category
                        else None
                    ),
                },
            },
        )

    async def restart_servers(self) -> None:
        """
        Shutdowns all game servers in the experience which are not on the \
        latest published version. Similar to the 'Migrate To Latest Update' \
        button on the game page.
        """

        await send_request(
            "POST",
            f"/universes/{self.id}:restartServers",
            authorization=self.__api_key,
            expected_status=[200],
        )

    async def flush_memory_store(self) -> Operation[bool]:
        """
        Flushes all memory store sorted map and queue data.

        Returns:
            An [`Operation`][rblxopencloud.Operation] to determine when the \
            operation is complete.
        """

        _, data, _ = await send_request(
            "POST",
            f"/universes/{self.id}/memory-store:flush",
            authorization=self.__api_key,
            expected_status=[200],
        )

        op_id = data["path"].split("/")[-1]

        return Operation(
            f"/universes/{self.id}/memory-store/operations/{op_id}",
            self.__api_key,
            True,
        )

    async def fetch_subscription(
        self, product_id: str, user_id: int
    ) -> Subscription:
        """
        Fetches information about a user's subscription to a product within \
        the experience.

        Args:
            product_id: The subscription product ID, starting with `EXP-`, to \
            consider.
            user_id: The subscription ID, which is always the user's ID to \
            fetch subscription information for.
        
        Returns:
            The subscription for the product ID and user ID.
        """

        _, data, _ = await send_request(
            "GET",
            f"/universes/{self.id}/subscription-products/\
{product_id}/subscriptions/{user_id}",
            params={"view": "FULL"},
            authorization=self.__api_key,
            expected_status=[200],
        )

        return Subscription(data)

    async def list_ban_logs(
        self, user_id: int = None, place_id: int = None, limit: int = None
    ) -> AsyncGenerator[Any, UserRestriction]:
        """
        Lists all ban and unban logs within the universe, optionally filtered \
        to a specific user and/ or place.

        Args:
            user_id: The user ID to fetch history for.
            place_id: Only include ban logs for this specific place ID.
        
        Yields:
            Restriction information for each restriction log found.
        """

        filter = []

        if user_id:
            filter.append(f"user == 'users/{user_id}'")
        if place_id:
            filter.append(f"place == 'places/{place_id}'")

        print(
            {
                "maxPageSize": limit if limit and limit <= 100 else 100,
                "filter": "&&".join(filter),
            }
        )
        async for entry in iterate_request(
            "GET",
            f"/universes/{self.id}/user-restrictions:listLogs",
            authorization=self.__api_key,
            expected_status=[200],
            params={
                "maxPageSize": str(limit if limit and limit <= 100 else 100),
                "filter": "&&".join(filter),
            },
            max_yields=limit,
            data_key="logs",
            cursor_key="pageToken",
        ):
            yield UserRestriction(entry, self.__api_key)

    async def fetch_user_restriction(self, user_id: int) -> UserRestriction:
        """
        Fetches the current restriction information for a user universe-wide. \
        (e.g. whether they are banned.)

        Args:
            user_id: The user ID to fetch restriction information for.
        
        Returns:
            The current restriction information for the requested user.
        """

        _, data, _ = await send_request(
            "GET",
            f"/universes/{self.id}/user-restrictions/{user_id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return UserRestriction(data, self.__api_key)

    async def ban_user(
        self,
        user_id: int,
        duration_seconds: Optional[int],
        display_reason: str = "",
        private_reason: str = "",
        exclude_alt_accounts: bool = False,
    ) -> UserRestriction:
        """
        Updates the current user restriction for a user on the universe-wide \
        level.

        Args:
            user_id: The ID of the user to update restrictions for.
            duration_seconds: The number of seconds the ban should last. \
            Provide `None` for an indefinite restriction.
            display_reason: The reason for the ban shown to the client.
            private_reason: The reason for the ban never shown to the client.
            exclude_alt_accounts: Whether the user's detected alt accounts \
            shouldn't be banned as well.
        
        Returns:
            The updated restriction information for the requested user.
        """

        _, data, _ = await send_request(
            "PATCH",
            f"/universes/{self.id}/user-restrictions/{user_id}",
            authorization=self.__api_key,
            expected_status=[200],
            json={
                "gameJoinRestriction": {
                    "active": True,
                    "duration": (
                        f"{duration_seconds}s" if duration_seconds else None
                    ),
                    "excludeAltAccounts": exclude_alt_accounts,
                    "displayReason": display_reason,
                    "privateReason": private_reason,
                }
            },
        )

        return UserRestriction(data, self.__api_key)

    async def unban_user(self, user_id: int) -> UserRestriction:
        """
        Removes the current user restriction for a user on the universe-wide \
        level.

        Args:
            user_id: The ID of the user to remove restrictions for.
        
        Returns:
            The updated restriction information for the requested user.
        """

        _, data, _ = await send_request(
            "PATCH",
            f"/universes/{self.id}/user-restrictions/{user_id}",
            authorization=self.__api_key,
            expected_status=[200],
            json={"gameJoinRestriction": {"active": False}},
        )

        return UserRestriction(data, self.__api_key)
