import rblxopencloud

# create a experience object, with the first value being the experience ID and the second being your api key
experience = rblxopencloud.Experience(3499447036, "api-key-here")

# create a datastore with the name 'exampleStore' and the scope of 'open-cloud'
datastore = experience.get_data_store("exampleStore", scope="open-cloud")

# this will get the key for '287113233'
value, info = datastore.get("287113233")
print(value)

# the second variable from DataStore.get is an EntryInfo object. it contains metadata about the value.
print(info.created) # datetime.datetime of when this value was created
print(info.updated) # datatime.datetim of when this value was last updated
print(info.version) # this is current version code.
print(info.users) # this is a list of user ids user for GDRP tracking and removal
print(info.metadata) # this is an optional dictionary provided by the developer.

# you can increment a number value and it will return the same as DataStore.get
# important: you must provide users and metadata or they'll be removed!!
value, info = datastore.increment("287113233", 4, users=info.users, metadata=info.metadata)
print(value, info)

# you can change the value completly with the set method
# important: you must provide users and metadata or they'll be removed!!
version = datastore.set("287113233", "this is a new value", users=info.users, metadata=info.metadata)

# this returns a EntryVersion object (NOT the same as DataStore.get and DataStore.increment)
print(version.version) # this is the version's id
print(version.deleted) # wether this version is deleted
print(version.content_length) # how long, in characters this version is.
print(version.created) # datetime.datetime of when this version was created
print(version.key_created) # datetime.datetime of when the key was created

# this is a shortcut for datastore.get_version and returns this version's value and info
value, info = version.get_value()
print(value, info)

# and finally for removing keys
datastore.remove("287113233")
# it's that simple. it'll no longer be able to be fetched with DataStore.get but can still be recovered with DataStore.get_version

# this is example including basic features of datastores. there is also examples for list geting versions, listing keys and datastores, and using preconditions