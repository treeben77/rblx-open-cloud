from base64 import b64encode
from datetime import datetime
import os
import pathlib
import secrets
import sys
import time
import unittest
from nacl import public, encoding

import rblxopencloud

# enables HTTP request debug logging
rblxopencloud.http.VERSION_INFO = "alpha"

if not os.environ.get("TEST_USER_CLOUD_KEY"):
    from dotenv import load_dotenv

    load_dotenv()


experience = rblxopencloud.Experience(
    os.environ["TEST_UNIVERSE_ID"],
    os.environ["TEST_USER_CLOUD_KEY"],
)

version = f"{sys.version_info.major}.{sys.version_info.minor}"

SKIP_UPDATE_TESTS = os.environ.get("PRIMARY_VERSION") not in (
    None,
    version,
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

    def test_ban_user(self):
        # avoids per user rate limits
        offset = sys.version_info.minor
        restriction = experience.ban_user(
            287113235 + offset,
            duration_seconds=86400,
            display_reason="some display reason",
            private_reason="some private reason",
        )

        self.assertIsInstance(restriction, rblxopencloud.UserRestriction)
        self.assertEqual(restriction.active, True)
        self.assertEqual(restriction.duration_seconds, 86400)

    def test_list_ban_logs(self):
        for restriction in experience.list_ban_logs(287113233, limit=10):
            self.assertIsInstance(restriction, rblxopencloud.UserRestriction)
            self.assertEqual(restriction.user.id, 287113233)


class subscriptions(unittest.TestCase):

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

        self.assertIs(experience, result)
        self.assertEqual(
            experience.name, "treeben77's very awesome test experience!"
        )
        self.assertEqual(
            experience.discord_social_link.uri, "https://discord.gg/6Y3bzJ59KU"
        )
        self.assertEqual(
            experience.age_rating,
            rblxopencloud.ExperienceAgeRating.ThirteenPlus,
        )
        self.assertTrue(experience.desktop_enabled)

    def test_update_info(self):
        expected_price = secrets.randbelow(490) + 10

        result = experience.update(private_server_price=expected_price)

        self.assertEqual(result, experience)
        self.assertEqual(result.private_server_price, expected_price)


class place_info(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        self.place = experience.get_place(9362552649)
        super().__init__(methodName)

    def test_fetch_info(self):
        # fetch_info should return itself.
        self.assertIs(self.place.fetch_info(), self.place)

        self.assertIn("UPDATED FROM OPEN CLOUD", self.place.description)
        self.assertIs(self.place.experience, experience)

    def test_update_info(self):
        values = ("place", "python", "value", "open", "cloud", "code", "tree")
        expected_value = f"{secrets.choice(values)} {secrets.choice(values)}"

        description = "HELLO WORLD OMG OMG THIS WAS UPDATED FROM OPEN CLOUD! "

        print(description + expected_value)
        result = self.place.update(description=description + expected_value)

        self.assertIs(result, self.place)
        self.assertEqual(self.place.description, description + expected_value)

    def test_place_publishing(self):
        place = experience.get_place(81636022792923)

        test_assets = pathlib.Path(__file__).parent.resolve() / "test_assets"

        with open(test_assets / "place.rbxl", "rb") as file:
            version = place.upload_place_file(file)

        self.assertIsInstance(version, int)


class secrets_store(unittest.TestCase):

    def test_list_secrets(self):
        found_target_secret = False

        for secret in experience.list_secrets(limit=10):
            self.assertIsInstance(secret, rblxopencloud.Secret)
            self.assertIsInstance(secret.created_at, datetime)
            self.assertIsInstance(secret.updated_at, datetime)
            self.assertIs(secret.experience, experience)

            if secret.id == "test_key":
                found_target_secret = True
                self.assertEqual(secret.domain, "secret1.treeben77.xyz")

        self.assertTrue(found_target_secret, "No such secret 'test_key'")

    def test_secret_write(self):
        secret_id = f"unittest_{secrets.token_hex(8)}"

        secret = experience.create_secret(
            secret_id, secrets.token_urlsafe(), domain="example.com"
        )

        self.assertIsInstance(secret, rblxopencloud.Secret)
        self.assertIsInstance(secret.created_at, datetime)
        self.assertIsInstance(secret.updated_at, datetime)

        new_secret = secret.update(
            secret=secrets.token_urlsafe(), domain="new.example.com"
        )

        self.assertIs(new_secret, secret)

        new_secret.delete()

    def test_manual_key_update(self):
        secret_content = "secret content"
        key_id, public_key = experience.fetch_secrets_public_key()

        self.assertRegex(key_id, r"[0-9]+")
        self.assertRegex(public_key.decode(), r"[a-zA-Z0-9+/]+=*")

        public_key = public.PublicKey(public_key, encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)

        encrypted = sealed_box.encrypt(secret_content.encode("utf-8"))

        secret = experience.update_secret(
            "test_key", b64encode(encrypted), key_id=key_id
        )

        self.assertIsInstance(secret, rblxopencloud.Secret)
        self.assertIsInstance(secret.updated_at, datetime)


class messaging_service(unittest.TestCase):

    def test_publish_message(self):
        experience.publish_message("topic", "payload")


class restart_servers(unittest.TestCase):

    def test_restart_servers(self):
        experience.restart_servers()


class developer_products(unittest.TestCase):

    def test_list_developer_products(self):
        found_products = False

        for product in experience.list_developer_products():
            self.assertIsInstance(product, rblxopencloud.DeveloperProduct)
            self.assertIs(product.experience, experience)

            self.assertIsInstance(product.id, int)
            self.assertIsInstance(product.name, str)
            self.assertIsInstance(product.description, str)
            self.assertIsInstance(
                product.icon_asset_id,
                int if product.icon_asset_id else type(None),
            )
            self.assertIsInstance(product.is_for_sale, bool)
            self.assertIsInstance(product.store_page_enabled, bool)
            self.assertIsInstance(product.regional_pricing_enabled, bool)
            self.assertTrue(
                product.price_in_robux is None
                or isinstance(product.price_in_robux, int)
            )
            self.assertIsInstance(product.created_at, datetime)
            self.assertIsInstance(product.updated_at, datetime)

            found_products = True

        self.assertTrue(found_products, "No developer products found")

    def test_fetch_developer_product(self):
        product = experience.fetch_developer_product(3472883382)

        self.assertIsInstance(product, rblxopencloud.DeveloperProduct)
        self.assertIs(product.experience, experience)

        self.assertEqual(product.id, 3472883382)
        self.assertEqual(product.name, "Test Open Cloud Product 5")
        self.assertEqual(product.description, "Hello World!")
        self.assertEqual(product.icon_asset_id, 82396052319080)
        self.assertEqual(product.is_for_sale, True)
        self.assertEqual(product.store_page_enabled, True)
        self.assertEqual(product.regional_pricing_enabled, True)
        self.assertEqual(product.price_in_robux, 67)
        self.assertIsInstance(product.created_at, datetime)
        self.assertIsInstance(product.updated_at, datetime)

    def test_update_developer_product(self):
        if SKIP_UPDATE_TESTS:
            self.skipTest("Skipped updating resource test for version.")

        new_name = f"rblx-open-cloud unittest {secrets.token_hex(2)}"
        new_description = secrets.token_hex(16)
        new_price = secrets.randbelow(10000)
        new_regional_pricing_enabled = secrets.choice([True, False])
        new_is_store_page_enabled = secrets.choice([True, False])

        experience.update_developer_product(
            3472891726,
            name=new_name,
            description=new_description,
            price_in_robux=new_price,
            regional_pricing_enabled=new_regional_pricing_enabled,
            store_page_enabled=new_is_store_page_enabled,
        )

        time.sleep(5)  # wait for eventual consistency

        developer_product = experience.fetch_developer_product(3472891726)

        self.assertEqual(developer_product.id, 3472891726)
        self.assertEqual(developer_product.name, new_name)
        self.assertEqual(developer_product.description, new_description)
        self.assertEqual(developer_product.price_in_robux, new_price)
        self.assertEqual(
            developer_product.regional_pricing_enabled,
            new_regional_pricing_enabled,
        )
        self.assertEqual(
            developer_product.store_page_enabled,
            new_is_store_page_enabled,
        )

        self.assertIsInstance(developer_product.created_at, datetime)
        self.assertIsInstance(developer_product.updated_at, datetime)
        self.assertGreater(
            developer_product.updated_at, developer_product.created_at
        )
        self.assertAlmostEqual(
            developer_product.updated_at.timestamp(),
            time.time(),
            delta=10,
        )


class game_passes(unittest.TestCase):
    def test_list_game_passes(self):
        found_passes = False

        for game_pass in experience.list_game_passes():
            self.assertIsInstance(game_pass, rblxopencloud.GamePass)
            self.assertIs(game_pass.experience, experience)

            self.assertIsInstance(game_pass.id, int)
            self.assertIsInstance(game_pass.name, str)
            self.assertIsInstance(game_pass.description, str)
            self.assertIsInstance(
                game_pass.icon_asset_id,
                int if game_pass.icon_asset_id else type(None),
            )
            self.assertIsInstance(game_pass.price_in_robux, int)
            self.assertIsInstance(game_pass.regional_pricing_enabled, bool)
            self.assertIsInstance(game_pass.created_at, datetime)
            self.assertIsInstance(game_pass.updated_at, datetime)

            found_passes = True

        self.assertTrue(found_passes, "No game passes found")

    def test_fetch_game_pass(self):
        game_pass = experience.fetch_game_pass(1617590110)

        self.assertIsInstance(game_pass, rblxopencloud.GamePass)
        self.assertIs(game_pass.experience, experience)

        self.assertEqual(game_pass.id, 1617590110)
        self.assertEqual(game_pass.name, "rblx-open-cloud unittest gamepass")
        self.assertEqual(game_pass.description, "This is a test game pass.")
        self.assertEqual(game_pass.icon_asset_id, 139446863449203)
        self.assertEqual(game_pass.price_in_robux, 670)
        self.assertEqual(game_pass.regional_pricing_enabled, False)
        self.assertIsInstance(game_pass.created_at, datetime)
        self.assertIsInstance(game_pass.updated_at, datetime)

    def test_update_game_pass(self):
        if SKIP_UPDATE_TESTS:
            self.skipTest("Skipped updating resource test for version.")

        new_name = f"rblx-open-cloud unittest {secrets.token_hex(2)}"
        new_description = secrets.token_hex(16)
        new_price = secrets.randbelow(10000)
        new_regional_pricing_enabled = secrets.choice([True, False])

        experience.update_game_pass(
            1618032326,
            name=new_name,
            description=new_description,
            price_in_robux=new_price,
            regional_pricing_enabled=new_regional_pricing_enabled,
        )

        time.sleep(5)  # wait for eventual consistency

        game_pass = experience.fetch_game_pass(1618032326)

        self.assertEqual(game_pass.id, 1618032326)
        self.assertEqual(game_pass.name, new_name)
        self.assertEqual(game_pass.description, new_description)
        self.assertEqual(game_pass.price_in_robux, new_price)
        self.assertEqual(
            game_pass.regional_pricing_enabled,
            new_regional_pricing_enabled,
        )
        self.assertIsInstance(game_pass.created_at, datetime)
        self.assertIsInstance(game_pass.updated_at, datetime)
        self.assertGreater(game_pass.updated_at, game_pass.created_at)
        self.assertAlmostEqual(
            game_pass.updated_at.timestamp(),
            time.time(),
            delta=10,
        )
