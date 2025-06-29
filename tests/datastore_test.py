from datetime import datetime
import os
import secrets
import unittest

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


class experience_data_stores(unittest.TestCase):

    def test_get_datastore(self):
        datastore = experience.get_datastore("rblxopencloud_unittest")

        self.assertIsInstance(datastore, rblxopencloud.DataStore)
        self.assertEqual(datastore.experience, experience)
        self.assertEqual(datastore.name, "rblxopencloud_unittest")
        self.assertEqual(datastore.scope, "global")

    def test_get_ordered_datastore(self):
        datastore = experience.get_ordered_datastore("rblxopencloud_unittest")

        self.assertIsInstance(datastore, rblxopencloud.OrderedDataStore)
        self.assertEqual(datastore.experience, experience)
        self.assertEqual(datastore.name, "rblxopencloud_unittest")
        self.assertEqual(datastore.scope, "global")

    def test_list_datastores(self):

        datastore_names = []

        for datastore in experience.list_datastores():
            datastore_names.append(datastore.name)

            self.assertIsInstance(datastore, rblxopencloud.DataStore)
            self.assertEqual(datastore.experience, experience)
            self.assertIsInstance(datastore.created, datetime)

        self.assertIn("rblxopencloud_unittest", datastore_names)

    def test_snapshot_datastores(self):
        was_created, last_created = experience.snapshot_datastores()

        self.assertIsInstance(was_created, bool)
        self.assertIsInstance(last_created, datetime)


datastore = experience.get_datastore("rblxopencloud_unittest")


class standard_data_stores(unittest.TestCase):

    def test_get_entry(self):
        entry, info = datastore.get_entry("test_entry")

        self.assertIsInstance(info, rblxopencloud.EntryInfo)
        self.assertEqual(entry, {"key1": "value", "key2": 3.14})
        self.assertEqual(info.users, [287113233])

        with self.assertRaises(rblxopencloud.NotFound):
            datastore.get_entry("test_entry_not_exists")

    def test_set_entry(self):
        nonce = secrets.token_hex(8)
        value = secrets.token_urlsafe(16)

        version = datastore.set_entry(f"test_entry_set_{nonce}", value)

        self.assertIsInstance(version, rblxopencloud.EntryVersion)
        self.assertEqual(version.content_length, len(value) + 2)

        entry, info = datastore.get_entry(f"test_entry_set_{nonce}")

        self.assertEqual(entry, value)
        self.assertEqual(info.version, version.version)

    def test_remove_entry(self):
        nonce = secrets.token_hex(8)

        datastore.set_entry(f"test_entry_remove_{nonce}", 1)

        datastore.remove_entry(f"test_entry_remove_{nonce}")

        with self.assertRaises(rblxopencloud.NotFound):
            datastore.get_entry(f"test_entry_remove_{nonce}")

    def test_list_keys(self):
        entry_keys = []

        for entry in datastore.list_keys("test_entry"):
            entry_keys.append(entry.key)

            self.assertIsInstance(entry, rblxopencloud.ListedEntry)
            self.assertTrue(entry.key.startswith("test_entry"))
            self.assertEqual(entry.scope, "global")

        self.assertIn("test_entry", entry_keys)

    def test_list_versions(self):
        did_iterate = False

        for entry in datastore.list_versions("test_entry"):

            self.assertIsInstance(entry.version, str)
            self.assertIsInstance(entry.created, datetime)
            self.assertIsInstance(entry.key_created, datetime)
            self.assertIsInstance(entry, rblxopencloud.EntryVersion)

            value, info = entry.get_value()

            self.assertIsInstance(info, rblxopencloud.EntryInfo)
            self.assertEqual(value, {"key1": "value", "key2": 3.14})
            self.assertEqual(info.users, [287113233])
            self.assertEqual(entry.version, info.version)

            did_iterate = True

        self.assertTrue(did_iterate)


ordered_datastore = experience.get_ordered_datastore("rblxopencloud_unittest")


class ordered_data_stores(unittest.TestCase):

    def test_get_entry(self):
        entry = ordered_datastore.get_entry("test_entry")

        self.assertEqual(entry, 133)

        with self.assertRaises(rblxopencloud.NotFound):
            ordered_datastore.get_entry("test_entry_not_exists")

    def test_set_entry(self):
        nonce = secrets.token_hex(8)
        value = secrets.randbelow(1000)

        entry = ordered_datastore.set_entry(f"test_entry_set_{nonce}", value)

        self.assertEqual(value, entry)

        entry = ordered_datastore.get_entry(f"test_entry_set_{nonce}")

        self.assertEqual(entry, value)

    def test_remove_entry(self):
        nonce = secrets.token_hex(8)
        ordered_datastore.set_entry(f"test_entry_remove_{nonce}", 1)

        ordered_datastore.remove_entry(f"test_entry_remove_{nonce}")

        with self.assertRaises(rblxopencloud.NotFound):
            ordered_datastore.get_entry(f"test_entry_remove_{nonce}")

    def test_sort_keys(self):
        prev_value = None
        entry_keys = []

        for entry in ordered_datastore.sort_keys():
            entry_keys.append(entry.key)

            self.assertIsInstance(entry, rblxopencloud.SortedEntry)
            self.assertEqual(entry.scope, "global")
            self.assertIsInstance(entry.value, int)

            if prev_value:
                self.assertLessEqual(entry.value, prev_value)

            prev_value = entry.value

        self.assertIn("test_entry", entry_keys)
        self.assertIn("test_entry_1", entry_keys)


if __name__ == "__main__":
    unittest.main()
