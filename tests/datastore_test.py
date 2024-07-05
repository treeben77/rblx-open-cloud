from datetime import datetime
import os
import secrets
import unittest

if not os.environ.get("OPEN_CLOUD_USER"):
    from dotenv import load_dotenv
    load_dotenv()

import rblxopencloud

experience = rblxopencloud.Experience(
    os.environ["EXPERIENCE_ID"], os.environ["OPEN_CLOUD_USER"]
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
        value = secrets.token_urlsafe(16)

        version = datastore.set_entry("test_entry_set", value)

        self.assertIsInstance(version, rblxopencloud.EntryVersion)
        self.assertEqual(version.content_length, len(value) + 2)

        entry, info = datastore.get_entry("test_entry_set")

        self.assertEqual(entry, value)
        self.assertEqual(info.version, version.version)
        
    def test_remove_entry(self):
        datastore.set_entry("test_entry_remove", 1)

        datastore.remove_entry("test_entry_remove")

        with self.assertRaises(rblxopencloud.NotFound):
            datastore.get_entry("test_entry_remove")
    
    def test_list_keys(self):
        entry_keys = []

        for entry in datastore.list_keys("test_entry"):
            entry_keys.append(entry.key)

            self.assertIsInstance(entry, rblxopencloud.ListedEntry)
            self.assertTrue(entry.key.startswith("test_entry"))
            self.assertEqual(entry.scope, "global")
        
        self.assertIn("test_entry", entry_keys)

ordered_datastore = experience.get_ordered_datastore("rblxopencloud_unittest")

class ordered_data_stores(unittest.TestCase):

    def test_get_entry(self):
        entry = ordered_datastore.get_entry("test_entry")

        self.assertEqual(entry, 133)
    
        with self.assertRaises(rblxopencloud.NotFound):
            ordered_datastore.get_entry("test_entry_not_exists")
    
    def test_set_entry(self):
        value = secrets.randbelow(1000)

        entry = ordered_datastore.set_entry("test_entry_set", value)

        self.assertEqual(value, entry)

        entry = ordered_datastore.get_entry("test_entry_set")

        self.assertEqual(entry, value)
    
    def test_remove_entry(self):
        ordered_datastore.set_entry("test_entry_remove", 1)

        ordered_datastore.remove_entry("test_entry_remove")

        with self.assertRaises(rblxopencloud.NotFound):
            ordered_datastore.get_entry("test_entry_remove")
    
    def test_sort_keys(self):
        prev_value = None
        entry_keys = []

        for entry in ordered_datastore.sort_keys():
            entry_keys.append(entry.key)

            self.assertIsInstance(entry, rblxopencloud.SortedEntry)
            self.assertEqual(entry.scope, "global")
            self.assertTrue(not prev_value or entry.value <= prev_value)

            prev_value = entry.value
        
        self.assertIn("test_entry", entry_keys)
        self.assertIn("test_entry_1", entry_keys)

if __name__ == '__main__':
    unittest.main()
