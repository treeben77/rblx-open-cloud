import rblxopencloud

# create a experience object, with the first value being the experience ID and the second being your api key
experience = rblxopencloud.Experience(3499447036, "api-key-here")

# this will publish a message to that topic in every server in that experience. it's this simple.
experience.publish_message("topic-name", "Hello World!")

# unfortently, there is currently no way to recieve messages.
# roblox also doesnt support publishing anything other than strings with open cloud.