# Asynchronous

!!! bug "Alpha Feature"
    The asynchronous version of the library is currently in Alpha. If you find any issues with it please report it in the annoucement's thread in the [Discord server](https://discord.gg/zW36pJGFnh), or on the [GitHub issue tracker](https://github.com/treeben77/rblx-open-cloud/issues).

If you're using rblx-open-cloud in an asynchronous context, such as with [discord.py](https://github.com/Rapptz/discord.py) or [ro.py](https://github.com/ro-py/ro.py), then it could be beneficial to use the aynchronous version of the library.

## Importing the Library

When installing rblxopencloud, both `rblxopencloud` and `rblxopencloudasync` modules are installed. The regular `rblxopencloud` library will still work as normal. `rblxopencloudasync` is the asyncronous version. For example, here is a comparison between importing the two versions:

=== "Normal"
    ```py
    import rblxopencloud
    ```

=== "Asyncronous"
    ```py
    import rblxopencloudasync
    ```

## Syntax Differences

All classes, methods, and attributes still persist the same values/returns, so you can still use the library reference. The difference is all methods that call to the Roblox API need to be awaited. For example, [`Experience.get_datastore`][rblxopencloud.Experience.get_datastore] does not need to be awaited, but [`Experience.publish_message`][rblxopencloud.Experience.publish_message] does. Here is an example of the differences between the two libraries for fetching a key, and listing it's versions:

=== "Normal"
    ```py
    from rblxopencloud import Experience

    experience = Experience(0000000000, "api-key")

    datastore = experience.get_datastore("playerData")

    value, info = datastore.get_entry("287113233")
    print(value, info)

    for version in datastore.list_versions("287113233"):
        print(version)
    ```

=== "Asyncronous"
    ```py
    from rblxopencloudasync import Experience

    experience = Experience(0000000000, "api-key")

    datastore = experience.get_datastore("playerData")

    value, info = await datastore.get_entry("287113233")
    print(value, info)

    async for version in datastore.list_versions("287113233"):
        print(version)
    ```