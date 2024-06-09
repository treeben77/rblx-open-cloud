# Introduction

[![Discord Server](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdiscord.com%2Fapi%2Fv10%2Finvites%2F4CSc9E5uQy%3Fwith_counts%3Dtrue&query=%24.approximate_member_count&suffix=%20members&style=for-the-badge&logo=discord&logoColor=white&label=Discord%20Server&labelColor=%235865F2&color=%23353535)](https://discord.gg/4CSc9E5uQy)
[![DevForum Post](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdevforum.roproxy.com%2Ft%2F1991959.json&query=%24.like_count&suffix=%20Likes&style=for-the-badge&logo=robloxstudio&logoColor=white&label=DevForum%20Post&labelColor=%23009fff&color=%23353535)](https://devforum.roblox.com/t/1991959)
[![Downloads](https://img.shields.io/pypi/dm/rblx-open-cloud?style=for-the-badge&logo=pypi&logoColor=white&label=PyPi%20Downloads&labelColor=%23006dad&color=%23353535)](https://pypi.org/project/rblx-open-cloud)

rblx-open-cloud is a Python API wrapper for [Roblox's Open Cloud](https://create.roblox.com/docs/cloud/open-cloud). It supports all experience and creator APIs, OAuth2, and incoming webhooks.

## Installation Process
To install rblx-open-cloud from PyPI package, you can install it from pip:

=== "Windows"
    ```console
    py -3 -m pip install rblx-open-cloud --upgrade
    ```

=== "Linux"
    ```console
    python3 -m pip install rblx-open-cloud --upgrade
    ```

### Basic Usage
In order to use this library, you will need an OpenCloud API key or OAuth application to proceed further. You can see [Roblox's documentation of this here.](https://create.roblox.com/docs/cloud/open-cloud/api-keys)

In rblxopencloud, we provide OAuth & API key of OpenCloud, so you can use one library for all of them:

=== "API Keys"

    This example will be if you used mulitple different API Keys and do not want one API Key to manage your requests.

    ```py
    from rblxopencloud import Experience

    experience = Experience(experience_id, "api_key")
    ```

    This example will be if you use only one API Key for everything, and you do not want to do the above example.

    ```py
    from rblxopencloud import ApiKey

    api_key = ApiKey("api key")

    group = api_key.get_group(123422)
    ```

    More in-depth example is at [guide](guides/api.md) 
    
=== "OAuth Application"
    This example, we are setting up and configuring our client secret, client ID, and our redirect. 

    ```py
    from rblxopencloud import OAuth2App

    rblxapp = OAuth2App(0000000000000000000, "your-client-secret", "https://example.com/redirect")
    ```
    More in-depth example is at [guide](guides/oauth.md) 
    

We have more in-depth examples for API Keys at [this link](guides/api.md) and [reference](reference/experience.md) to learn more.

## Getting Help

You can ask for help in the [Discord server](https://discord.gg/4CSc9E5uQy) or the [DevForum Post](https://devforum.roblox.com/t/1991959), and you can report bugs on the [GitHub repository](https://github.com/treeben77/rblx-open-cloud/issues).

**Thank you for using rblx-open-cloud!**
