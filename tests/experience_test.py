import os
import unittest

if not os.environ.get("OPEN_CLOUD_USER"):
    from dotenv import load_dotenv

    load_dotenv()

import rblxopencloud

experience = rblxopencloud.Experience(
    os.environ["EXPERIENCE_ID"], os.environ["OPEN_CLOUD_USER"]
)


class user_restrictions(unittest.TestCase):

    def test_fetch_user_restriction(self):
        restriction = experience.fetch_user_restriction(287113233)

        self.assertIsInstance(restriction, rblxopencloud.UserRestriction)
        self.assertEqual(restriction.active, False)

        restriction = experience.fetch_user_restriction(287113234)

        self.assertIsInstance(restriction, rblxopencloud.UserRestriction)
        self.assertEqual(restriction.active, True)
        self.assertEqual(restriction.duration_seconds, None)
        self.assertEqual(restriction.display_reason, "some display reason")
        self.assertEqual(restriction.private_reason, "some private reason")

    def test_ban_unban_user(self):
        restriction = experience.ban_user(
            287113235,
            duration_seconds=86400,
            display_reason="some display reason",
            private_reason="some private reason",
        )

        self.assertIsInstance(restriction, rblxopencloud.UserRestriction)
        self.assertEqual(restriction.active, True)
        self.assertEqual(restriction.duration_seconds, 86400)

        restriction = experience.unban_user(287113235)

        self.assertIsInstance(restriction, rblxopencloud.UserRestriction)
        self.assertEqual(restriction.active, False)

    def test_list_ban_logs(self):
        for restriction in experience.list_ban_logs(287113233, limit=10):
            self.assertIsInstance(restriction, rblxopencloud.UserRestriction)
            self.assertEqual(restriction.user.id, 287113233)


class experience_subscriptions(unittest.TestCase):

    def test_fetch_subscription(self):
        subscription = experience.fetch_subscription(
            "EXP-2491104735766773879", 287113233
        )

        self.assertIsInstance(subscription, rblxopencloud.Subscription)
        self.assertEqual(subscription.active, False)
        self.assertEqual(subscription.product_id, "EXP-2491104735766773879")
        self.assertEqual(subscription.user_id, 287113233)
        self.assertEqual(
            subscription.state, rblxopencloud.SubscriptionState.Expired
        )
        self.assertEqual(
            subscription.expiration_reason,
            rblxopencloud.SubscriptionExpirationReason.Cancelled,
        )


class experience_info(unittest.TestCase):

    def test_fetch_info(self):
        result = experience.fetch_info()

        self.assertEqual(experience, result)
        self.assertEqual(
            experience.name, "treeben77's very awesome test experience!"
        )
        self.assertEqual(
            experience.discord_social_link.uri, "https://discord.gg/6Y3bzJ59KU"
        )
        self.assertEqual(
            experience.age_rating, rblxopencloud.ExperienceAgeRating.AllAges
        )
        self.assertTrue(experience.desktop_enabled)
