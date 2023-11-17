# Asynchronous

!!! bug "Alpha Library"
    The asynchronous version of the library is currently in Alpha. If you find any issues with it please report it in the annoucement's thread in the [Discord server](https://discord.gg/zW36pJGFnh), or on the [GitHub issue tracker](https://github.com/treeben77/rblx-open-cloud/issues).

    Additionally, avoid using the `rblxopencloud.preform_request` method, as it's likely it's name will be changed.

If you're using rblx-open-cloud in an asynchronous context, such as with [discord.py](https://github.com/Rapptz/discord.py), or [ro.py](https://github.com/ro-py/ro.py), then it could be beneficial to use the aynchronous version of the library.

## Installing the Alpha Version

You can install the alpha version with the following command:

```console
pip install git+https://github.com/treeben77/rblx-open-cloud.git@async --force
```

## Importing the Library

When installing the library, it will install both the `rblxopencloud`, and `rblxopencloudasync` modules. The regular `rblxopencloud` library will still work as normal. `rblxopencloudasync` is the asyncronous version. For example, here is a comparison between importing the two versions:

=== "Normal"
    ```py
    import rblxopencloud
    ```

=== "Asyncronous"
    ```py
    import rblxopencloudasync
    ```

## Syntax Differences

All classes, methods, and attributes still persist the same values/returns, so you can still use the library reference. The difference is all methods that call to the Roblox API need to be awaited. For example, [`Experience.get_data_store`][rblxopencloud.Experience.get_data_store] does not need to be awaited, but [`Experience.publish_message`][rblxopencloud.Experience.publish_message] does. Here is an example of the differences between the two libraries for fetching a key, and listing it's versions:

=== "Normal"
    ```py
    from rblxopencloud import Experience

    experience = Experience(0000000000, "api-key")

    datastore = experience.get_data_store("playerData")

    value, info = datastore.get("287113233")
    print(value, info)

    for version in datastore.list_versions("287113233"):
        print(version)
    ```

=== "Asyncronous"
    ```py
    from rblxopencloudasync import Experience

    experience = Experience(0000000000, "api-key")

    datastore = experience.get_data_store("playerData")

    value, info = await datastore.get("287113233")
    print(value, info)

    async for version in datastore.list_versions("287113233"):
        print(version)
    ```