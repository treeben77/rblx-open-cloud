---
title: Getting Started 
---

## Quickstart 

### Installing rblx-open-cloud
```
py -3 -m pip install rblx-open-cloud --upgrade
```

### Let's get a basic usage for rblx-open-cloud
Keep in mind, if you want in-depth tutorials, then please check out the guides section of this documentation.This will cover the basics of how to use this library.

```py
from rblxopencloud import Experience

# @param universeID number -- is the identifier of the experience that you want to access. 
# @param API_KEY string --  will be your API key.
experience = Experience(11334231, "test_api_key")
```

API keys can be created in the [Creator Dashboard](https://create.roblox.com/dashboard/credentials). You can find that tutorial [here](https://create.roblox.com/docs/cloud/open-cloud/api-keys#creating-an-api-key) by Roblox.