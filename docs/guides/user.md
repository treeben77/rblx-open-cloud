# User
The [`rblxopencloud.User`][rblxopencloud.User] object allows access to user info, and uploading assets.

## Accessing User Information

### Fetching User Info

You can fetch a users basic info by using the [`User.fetch_info`][rblxopencloud.User.fetch_info] method:

```py
user = rblxopencloud.User(000000, "api-key")

user.fetch_info()

print(user.display_name, user.username)
```

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
    operation = user.upload_asset(file, rblxopencloud.AssetType.Decal, "asset name", "asset description")

asset = operation.wait()
print(asset)
```

!!! danger
    Avoid uploading assets to Roblox that you don't have full control over, such as AI generated assets or content created by unknown people. Assets uploaded that break Roblox's Terms of Services can get your account moderated.

    For OAuth2 developers, it has been confirmed by Roblox staff [in this DevForum post](https://devforum.roblox.com/t/2401354/36), that your app will not be punished if a malicious user uses it to upload Terms of Service violating content, and instead the authorizing user's account will be punished.

You can update model assets using [`User.update_asset`][rblxopencloud.User.update_asset].