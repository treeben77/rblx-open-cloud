import rblxopencloud

# create a universe object, with the first value being the universe ID and the second being your api key
universe = rblxopencloud.Universe(3499447036, "api-key-here")

# create a datastore with the name 'exampleStore' and the scope of 'open-cloud'
datastore = universe.get_data_store("exampleStore", scope="open-cloud")

# this will list every key as an ListedEntry object in the datastore scope.
for entry in datastore.list_keys():
    print(entry.key, entry.scope) # ListedEntry only has these 2 attributes.

# you can get a list of versions like this, but be careful for large datastores, this could take a long time and result in rate limiting.
entries = list(datastore.list_keys())

# you can provide a scope to only return keys that start with a specific string
# using 287 will only return keys such as 287113233, 287 or 28743791
for entry in datastore.list_keys(prefix="287"):
    print(entry.key, entry.scope)

# you can limit the amount of values you can get with the limit param, use None for no limit.
# this doesn't guarentee you won't get less, it means you won't get more.
for entry in datastore.list_keys(limit=25):
    print(entry.key, entry.scope)

# you can get entries from all data stores if scope is None
datastore = universe.get_data_store("exampleStore", scope=None)

for entry in datastore.list_keys():
    print(entry.key, entry.scope)

# note: if you don't use a scope you have to use other functions differently, for example:
value, info = datastore.get("open-cloud/287113233") # the scope and key are split with a '/' in the same string

# you can also like datastores in a universe
for datastore in universe.list_data_stores():
    print(datastore.name)

# you can set a default scope for the datastores with the scope param
for datastore in universe.list_data_stores(scope="open-cloud"):
    print(datastore.name)

# just like with keys, you can provide a limit and/or a prefix
for datastore in universe.list_data_stores(prefix="example"):
    print(datastore.name)

for datastore in universe.list_data_stores(limit=25):
    print(datastore.name)

# if you want to list versions, look at examples/datastores-versions.py