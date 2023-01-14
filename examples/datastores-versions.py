import rblxopencloud

# this built in module is required for this tutorial
from datetime import datetime 

# create a universe object, with the first value being the universe ID and the second being your api key
universe = rblxopencloud.Experience(3499447036, "api-key-here")

# create a datastore with the name 'exampleStore' and the scope of 'open-cloud'
datastore = universe.get_data_store("exampleStore", scope="open-cloud")

# this will list every version as an EntryVersion object in the last 30 days.
for version in datastore.list_versions("287113233"):
    print(version.version) # this is the version's id
    print(version.deleted) # wether this version is deleted
    print(version.content_length) # how long, in characters this version is.
    print(version.created) # datetime.datetime of when this version was created
    print(version.key_created) # datetime.datetime of when the key was created

    # this is a shortcut for datastore.get_version and returns this version's value and info
    value, info = version.get_value()
    print(value, info)

# you can get a list of versions like this, but be careful for often modifed keys, this could take a long time and result in rate limiting.
versions = list(datastore.list_versions("287113233"))

# you can get versions after a specific time, this will list all versions after the 10th Oct 2022 at midday local time.
# note: Roblox only stores datastores for 30 days!
for version in datastore.list_versions("287113233", after=datetime(2022, 10, 22, 12, 00, 00)):
    print(version)

# the same can be done with before, this will list all versions before the 10th Oct 2022 at midday local time.
for version in datastore.list_versions("287113233", before=datetime(2022, 10, 22, 12, 00, 00)):
    print(version)

# you can limit the amount of values you can get with the limit param, use None for no limit.
# this doesn't guarentee you won't get less, it means you won't get more.
for version in datastore.list_versions("287113233", limit=25):
    print(version)

# you can set descending to False if you want to get the oldest first, otherwise it'll be the newest first
for version in datastore.list_versions("287113233", descending=False):
    print(version)

# if you already have a version ID and want to get it's value you can use the DataStore.get_version method
datastore.get_version("287113233", "08DA8D91A2A32691.0000000007.08DAB014F46E3CF6.01")