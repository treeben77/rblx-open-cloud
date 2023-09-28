---
title: Getting Started 
---

## Quickstart 

### Installing rblx-open-cloud
```
pip install rblx-open-cloud
```

### Let's get a basic usage for rblx-open-cloud
Keep in mind, if you want in-depth tutorials, then please check out the guides section of this documentation.This will cover the basics of how to use this library.

```py
# This is how we import Experience, you'll see why we need this later; 
from rblxopencloud import Experience

experience = Experience(11334231, "test_api_key")
# The first argument "11334231" is the identifier of the experience with data stores that you want to access. You can copy your experience's Universe ID on Creator Dashboard.

# The second argument "test_api_key" will be your API key.
```
APIs can be regened by going through Creator Dashboard. You can find that tutorial [here](https://create.roblox.com/docs/cloud/open-cloud/api-keys#creating-an-api-key) by Roblox.