# this example uses the flask library for a webserver.
from flask import Flask, request, redirect
import rblxopencloud

app = Flask(__name__)
# the number is the client ID, and the first string is the client secret. Both of these are given to you when you create your app.
# the URI at the end is the redirect uri. It is where the user goes after authorzing. It should be the uri for @app.route("/roblox").
oauth2 = rblxopencloud.OAuth2App(123456789, "api-secret-from-creator-dashboard", "http://localhost:9066/roblox")

# the home page of your app will just redirect you to the authorization page.
@app.route("/")
def index():
    # oauth2.generate_uri will generate a uri with the following list of scope, and the state which you can redirect the end user to.
    # this is more convinent then just using a pasted uri, because it looks nicer, and is easier to add variables into.
    return redirect(oauth2.generate_uri(scope=["openid", "profile", "universe-messaging-service:publish", "asset:read", "asset:write"], state="amogus"))

# this is the endpoint the user will return to after authorizing.
@app.route("/roblox")
def roblox():
    # this will turn the ?code= that roblox provided into an access token that you can use.
    access = oauth2.exchange_code(code=request.args["code"])
    # for example, this will get the user's information
    print(access.user)
    # and this will list the experiences and accounts that were authorized.
    print(resources:=access.fetch_resources())

    # this will send a message to every server in the first experience access was granted to.
    resources.experiences[0].publish_message("topic-name", "Hello World!")

    # this would send that message to every experience authorized:
    for experience in resources.experiences:
        experience.publish_message("topic-name", "Hello World!")

    # this will upload example.png to the first authorized account.
    with open("example.png", "rb") as file:
        resources.accounts[0].upload_asset(file, rblxopencloud.AssetType.Decal, "name", "description")

    # here's how to get the ids of experiences and accounts
    print(resources.experiences[0].id)
    print(resources.accounts[0].id)
    
    # this is true if the account is a user, but if it is a group, then it will be false.
    print(type(resources.accounts[0]) == rblxopencloud.User)

    # if you want to use the authorization in the future, you'll need to store the refresh token somewhere safe. this is how to get it:
    print(access.refresh_token)

    # when you next want to use this authorization, you must refresh the token, like this:
    new_access = oauth2.refresh_token("refresh-token-here")

    # this will create a new access token, and you'll be able to access the resources again!
    # do note however, that you MUST store the new refresh token, otherwise you not be able to refresh it again.

    return f"Hey {access.user.display_name}, here's ur resources: {resources}"

# this runs the flask server.
app.run("localhost", 9066)