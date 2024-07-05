# Basic Example

## API Key Authentication
This example will be if you used mulitple different API Keys and do not want one API Key to manage your requests.

```py
from rblxopencloud import Experience, Group

experience = Experience(experience_id, "api-key-1")
experience = Group(group_id, "api-key-2")
```

This example will be if you use only one API Key for everything, and you do not want to do the above example.

```py
from rblxopencloud import ApiKey

api_key = ApiKey("api-key")

experience = api_key.get_experience(experience_id)
group = api_key.get_group(group_id)
```

## OAuth Application Authentication
This example, we are setting up and configuring our client secret, client ID, and our redirect. 

```py
from rblxopencloud import OAuth2App

rblxapp = OAuth2App(0000000000000000000, "your-client-secret", "https://example.com/redirect")
```