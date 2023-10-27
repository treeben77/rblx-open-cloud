# Group

The [`rblxopencloud.User`][rblxopencloud.User] object allows access to user info, and uploading assets.

## Getting Started

### Creating an API Key

To use any APIs, first you will need to create an API key, the key allows the library to preform requests. To create an API key, you must go to the [Creator Dashboard](https://create.roblox.com/dashboard/credentials), and then press 'CREATE API KEY'. This will open the new API key menu.

First, you will need to give your API key a name, it should be something that will help you identify it from any other API keys you might have. Next, you will need to define what APIs and permissions you give to your API key. For user API keys you can use the Group API to get a list of groups, the Inventory API to get group items, or the assets API to get assets.

Once you've finished selecting permissions, the last section is security. This allows you to define what IP addresses/CIDR notations can use your API key, and how long until it expires. If you do not know your IP address, you can add `0.0.0.0/0` to the IP address list to allow all IP addresses. The experiation allows you to configure a set time for your API key to be disabled, which is useful if you plan to not use the API key in the future.

After pressing 'SAVE & GENERATE KEY', Roblox will provide you with a string of random letters, numbers and symbols. You will need this key, but do not share the key with anyone else. This key allows people to use your API key!

!!! warning
    When selecting permissions, you should provide only what APIs and scopes your API key will need to use. This helps minize the impact if the API key is comprimised. Using `0.0.0.0/0` significantly increases the risk in your API key being used by bad actors.

### User Permissions

Uploading assets require the API key to be owned by the user itself. Other APIs such as listing user groups or inventory API do not require the key to be owned by user. For example, you can fetch the list of groups for any user on the platform, as long as the API key has the Group API permission.

## Accessing User Information

### Listing Inventory Items

You can list all items in a user's inventory with [`User.list_inventory`][rblxopencloud.User.list_inventory]. If the user's inventory is not public, and the authorizing user doesn't have permission to access the users inventory (i.e. they're not friends with the user, but only friends can access their inventrory), the request will throw an error.

```py
user = rblxopencloud.User(000000, "api-key")

for item in user.list_inventory():
    print(item)
```

You can use [OAuth2](oauth2.md) to authorize permission to access the users inventory, and you can access their inventory even if it is private.

You can set limits to what types of items to list. The different allowed filters are `assets`, `badges`, `game_passes`, and `private_servers`. All of these can be a boolean, wether to include these asset types, or a list of IDs, which will only include IDs of that type. `assets` also allows a list of [`rblxopencloud.InventoryAssetType`][rblxopencloud.InventoryAssetType] to limit what types of assets to return. For example if you only wanted their to know the user's classic shirts, t-shirts, and pants, you could use this:

```py
for item in user.list_inventory(assets=[
    rblxopencloud.InventoryAssetType.ClassicShirt,
    rblxopencloud.InventoryAssetType.ClassicShirt,
    rblxopencloud.InventoryAssetType.ClassicPants
]):
    print(item)
```

If filter parameters are filled, then it will return the entire inventory. But if *any* filter parameters have a value, then it all empty parameters will default to `False`.

### Listing Groups

You can list groups the user is a member of using [`User.list_groups`][rblxopencloud.User.list_groups]. You can give the groups for any user as long as the API key has the Groups API. This example will list all the groups for the current member.

```py
for member in user.list_groups():
    print(member.group, member.role_id)
```

## Uploading Assets

You can upload images, audio, and models to your user account using the [`User.upload_asset`][rblxopencloud.User.upload_asset] method. It requires an API key owned by the User with read and write Asset API permissions. The following example will upload the image at the path `path-to/image.png`:

```py
with open("path-to/image.png", "rb") as file:
    status = user.upload_asset(file, rblxopencloud.AssetType.Decal, "asset name", "asset description")

if isinstance(asset, rblxopencloud.Asset):
    print(asset)
else:
    while True:
        status = asset.fetch_status()
        if status:
            print(status)
            break
```

!!! danger
    Avoid uploading assets to Roblox that you don't have full control over, such as AI generated assets or content created by unknown people. Assets uploaded that break Roblox's Terms of Services can get your account moderated.

    For OAuth2 developers, it has been confirmed by Roblox staff [in this DevForum post](https://devforum.roblox.com/t/2401354/36), that your app will not be punished if a malicious user uses it to upload Terms of Service violating content, and instead the authorizing user's account will be punished.

You can update model assets using [`User.update_asset`][rblxopencloud.User.update_asset].