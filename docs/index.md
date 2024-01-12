# Introduction

[![Discord Server](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdiscord.com%2Fapi%2Fv10%2Finvites%2F4CSc9E5uQy%3Fwith_counts%3Dtrue&query=%24.approximate_member_count&suffix=%20members&style=for-the-badge&logo=discord&logoColor=white&label=Discord%20Server&labelColor=%235865F2&color=%23353535)](https://discord.gg/4CSc9E5uQy)
[![DevForum Post](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdevforum.roproxy.com%2Ft%2F1991959.json&query=%24.like_count&suffix=%20Likes&style=for-the-badge&logo=robloxstudio&logoColor=white&label=DevForum%20Post&labelColor=%23009fff&color=%23353535)](https://devforum.roblox.com/t/1991959)
[![Downloads](https://img.shields.io/pypi/dm/rblx-open-cloud?style=for-the-badge&logo=pypi&logoColor=white&label=PyPi%20Downloads&labelColor=%23006dad&color=%23353535)](https://pypi.org/project/rblx-open-cloud)

rblx-open-cloud is a Python API wrapper for [Roblox's Open Cloud](https://create.roblox.com/docs/cloud/open-cloud). It supports all experience and creator APIs, OAuth2, and incoming webhooks, and OAuth2.

## Getting Started

### Instalation

=== "Windows"
    ```console
    py -3 -m pip install rblx-open-cloud --upgrade
    ```

=== "Linux"
    ```console
    python3 -m pip install rblx-open-cloud --upgrade
    ```

### Basic Usage

Here are examples of creating classes for experiences, and groups.

=== "Experience"

    This example will create an experience object, with `0000000` as the experience/universe ID, and `apikey` is the API key (see below).

    ```py
    from rblxopencloud import Experience

    experience = Experience(0000000, "apikey")
    ```

    Check out the experience [guide](guides/experience.md) and [reference](reference/experience.md) to learn more.

=== "Group"

    This example will create an experience object, with `0000000` as the group ID, and `apikey` is the API key (see below).

    ```py
    from rblxopencloud import Group

    group = Group(0000000, "apikey")
    ```

    Check out the group [guide](guides/group.md) and [reference](reference/group.md) to learn more.

### API Keys

To use Open Cloud APIs you need to create an API key. An API key is a string which is provided to Roblox is prove who you are, and that you have permission to use these APIs. Here's how to create an API key:

1. Go to the [Creator Dashboard](https://create.roblox.com/dashboard/credentials), and navigate to the Open Cloud API Keys section.
2. Press 'CREATE API KEY'.
3. Give your API key a name to identify it.
4. Under 'Access Permissions', select the API system from the drop down you'd like to use
5. Configure the permissions to allow the required experiences and/or scopes.

Each guide gives more detailed information about how to create API keys for that guide. Most APIs are also able to be authentiated with [OAuth2](guides/oauth2.md).

## Getting Help

You can ask for help in the [Discord server](https://discord.gg/4CSc9E5uQy) or the [DevForum Post](https://devforum.roblox.com/t/1991959), and you can report bugs on the [GitHub repository](https://github.com/treeben77/rblx-open-cloud/issues).

**Thank you for using rblx-open-cloud!**
