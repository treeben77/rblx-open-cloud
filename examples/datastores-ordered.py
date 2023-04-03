import rblxopencloud

# create a experience object, with the first value being the experience ID and the second being your api key
experience = rblxopencloud.Experience(3499447036, "api-key-here")

# create a ordereddatastore with the name 'exampleStore' and the scope of 'open-cloud'
datastore = experience.get_ordered_data_store("exampleStore", scope="open-cloud")

# this will get the key for '287113233'
value = datastore.get("287113233")
print(value)
# there is no EntryInfo object, this is a Roblox limitation.

# you can increment a number value and it will return the new value
value = datastore.increment("287113233", 4)
print(value)

# you can change the value the set method
version = datastore.set("287113233", 123)

# you can delete a key using:
datastore.remove("287113233")

# you can get the value in order using sort_keys()
for key in datastore.sort_keys():
    print(key.key, key.scope, key.value)

# you can convert it to a list
keys = list(datastore.sort_keys())

# by default it will get the largest values first, but you can also sort by smallest first
for key in datastore.sort_keys(descending=False):
    print(key.key, key.scope, key.value)

# you can also set the max and min key values to retrieve
for key in datastore.sort_keys(min=10, max=40):
    print(key.key, key.scope, key.value)

# and finally, you can set a limit to the number of keys you get.
for key in datastore.sort_keys(limit=20):
    print(key.key, key.scope, key.value)

# ordered data stores also support preconditions, and you can find an example in examples/datastores-preconditions.py