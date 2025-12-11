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


creator = rblxopencloud.User(
    os.environ["TEST_USER_ID"],
    os.environ["TEST_USER_CLOUD_KEY"],
)

version = f"{sys.version_info.major}.{sys.version_info.minor}"

SKIP_UPDATE_TESTS = os.environ.get("PRIMARY_VERSION") not in (
    None,
    version,
)


class fetch_asset_information(unittest.TestCase):

    def test_fetch_asset(self):
        asset = creator.fetch_asset(14903722621)

        self.assertIsInstance(asset, rblxopencloud.Asset)
        self.assertEqual(asset.id, 14903722621)
        self.assertEqual(asset.type, rblxopencloud.AssetType.Model)
        self.assertEqual(asset.name, "firehydrant")
        self.assertEqual(
            asset.description, "A simple fire hydrant to keep the flames away!"
        )
        self.assertEqual(asset.icon_asset_id, 14903722784)
        self.assertEqual(asset.is_archived, False)
        self.assertIs(asset.creator, creator)
        self.assertIsInstance(asset.revision_time, datetime)
        self.assertEqual(
            asset.moderation_status, rblxopencloud.ModerationStatus.Approved
        )

    def test_fetch_creator_store_product(self):
        product = creator.fetch_creator_store_product(
            rblxopencloud.AssetType.Model, 14903722621
        )

        self.assertIsInstance(product, rblxopencloud.CreatorStoreProduct)
        self.assertEqual(product.asset_id, 14903722621)
        self.assertIs(product.creator, creator)
        self.assertEqual(product.base_price, rblxopencloud.Money("USD", 0))
        self.assertEqual(product.purchase_price.quantity, 0)
        self.assertEqual(product.purchasable, True)
        self.assertEqual(product.published, True)
