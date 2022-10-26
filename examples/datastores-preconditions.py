import rblxopencloud

# create a universe object, with the first value being the universe ID and the second being your api key
universe = rblxopencloud.Universe(3499447036, "api-key-here")

# create a datastore with the name 'exampleStore' and the scope of 'open-cloud'
datastore = universe.get_data_store("exampleStore", scope="open-cloud")

# you can use exclusive_create to prevent overriding an existing value
version = datastore.set("287113233", "this is a new value", exclusive_create=True)
# this will raise rblxopencloud.PreconditionFailure if the value already exists.

# you can also get it's current value without sending another request:
try:
    version = datastore.set("287113233", "this is a new value", exclusive_create=True)
except(rblxopencloud.PreconditionFailed) as error:
    print(error.value, error.info)

# you can also set previous_version to a version ID and only update the value if the current version is the provided version.
try:
    version = datastore.set("287113233", "this is a new value", previous_version="08DA8D91A2A32691.0000000007.08DAB014F46E3CF6.01")
except(rblxopencloud.PreconditionFailed) as error:
    print(error.value, error.info)

# DataStore.increment and DataStore.remove don't support preconditions.