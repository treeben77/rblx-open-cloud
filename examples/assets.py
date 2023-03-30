import rblxopencloud

# to upload assets to your account, choose User
creator = rblxopencloud.User(13058, api_key="api-key-from-step-2")
# if you want to upload assets to a group, choose Group
creator = rblxopencloud.Group(13058, api_key="api-key-from-step-2")

# let's start with decals. open the file as read bytes.
with open("example.png", "rb") as file:
    # call the upload_asset function, name is the item name and description is the item description, you should use an item type of Decal.
    asset = creator.upload_asset(file, rblxopencloud.AssetType.Decal, "name", "description")
    # asset will be either Asset or PendingAsset. Asset contains information about the asset.
    # PendingAsset means Roblox hasn't finnished processing it. This will have a fetch_operation method
    # the fetch operation method will check if it's ready yet, it will return either None or Asset.

    # here's some code that will wait until the decal is ready
    if isinstance(asset, rblxopencloud.Asset):
        # if it's already been processed, then print the asset.
        print(asset)
    else:
        # otherwise, we'll go into a loop that continuosly loops through that.
        while True:
            # this will try to check if the asset has been processed yet
            status = asset.fetch_status()
            if status:
                # if it has been print it then stop the loop.
                print(status)
                break

# now for audio. it's the same as above but with audio
with open("example.mp3", "rb") as file:
    # call the upload_asset object, name is the item name and description is the item description, you should use an item type of Audio.
    asset = creator.upload_asset(file, rblxopencloud.AssetType.Audio, "name", "description")
    # for simplicity, I won't include the asset fetch_operation part above here but it also works.

    # please note that you can only upload 10 audios a month and if you're ID verified that's 100.

# and finally for .fbx files. it's the same as above but with a model
with open("example.fbx", "rb") as file:
    # call the upload_asset object, name is the item name and description is the item description, you should use an item type of Audio.
    asset = creator.upload_asset(file, rblxopencloud.AssetType.Model, "name", "description")
    # for simplicity, I won't include the asset fetch_operation part above here but it also works.
    # you're most likely going to recieve a PendingAsset with models because roblox has to render them which takes time

# you can also update uploaded fbx files:
with open("example.fbx", "rb") as file:
    # call the update_asset object, 1234 is the asset's ID
    asset = creator.update_asset(1234, file)
    # for simplicity, I won't include the asset fetch_operation part above here but it also works.
    # you're most likely going to recieve a PendingAsset with models because roblox has to render them which takes time