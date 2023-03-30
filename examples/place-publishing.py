import rblxopencloud

# create a universe object, with the first value being the experience ID and the second being your api key
experience = rblxopencloud.Experience(3499447036, "api-key-here")

# open the .rbxl file as read bytes
with open("path-to/place-file.rbxl", "rb") as file:
    # the first number is the place ID to update, and publish denotes wether to publish or save the place.
    # TODO: replace '1818' with your place ID
    experience.upload_place(1818, file, publish=False)