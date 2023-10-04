# Experience

The experience object allows access to an experience's resources such as data stores, messaging service, or uploading places.

## Getting Started

### Creating an API Key

To use any APIs, first you will need to create an API key, the key allows the library to preform requests. To create an API key, you must go to the [Creator Dashboard](https://create.roblox.com/dashboard/credentials), switch to the creator (e.g. user/group) who owns the experience if necessary, and then press 'CREATE API KEY'. This will open the new API key menu.

First, you will need to give your API key a name, it should be something that will help you identify it from any other API keys you might have. Next, you will need to define what APIS and permissions you give to your API key. APIs such as DataStore, or Messaging Service API are experience APIs. Once you've selected the API you'd like to use, press 'ADD API SYSTEM', and it will appear below.

For experience APIs, you will need to specifiy what experience(s) to use allow by clicking 'Select an Experience' and 'ADD EXPERIENCE'. The experience's name will appear below, and now you can specify what API operations. The API permissions you provide here will define what functions you can use in the library.

Once you've finished selecting permissions, the last section is security. This allows you to define what IP addresses/CIDR notations can use your API key, and how long until it expires. If you do not know your IP address, you can add `0.0.0.0/0` to the IP address list to allow all IP addresses. The experiation allows you to configure a set time for your API key to be disabled, which is useful if you plan to not use the API key in the future.

After pressing 'SAVE & GENERATE KEY', Roblox will provide you with a string of random letters, numbers and symbols. You will need this key, but do not share the key with anyone else. This key allows people to use your API key!

!!! warning
    When selecting permissions, you should provide only what APIs and scopes your API key will need to use. This helps minize the impact if the API key is comprimised. Using `0.0.0.0/0` significantly increases the risk in your API key being used by bad actors.

### The `Experience` Object

Now that you've created an API key, you may now use it in your code. The following code library imports and creates an [`rblxopencloud.Experience`][rblxopencloud.Experience] object:

```py
from rblxopencloud import Experience

experience = Experience(00000000, "your-api-key")
```

Replace `00000000` with your experience/universe ID (NOT place ID), and `your-api-key` with the API key string you just generated. Now that you've created an [`rblxopencloud.Experience`][rblxopencloud.Experience] object, you can start using the experience APIs!

<!-- ## Using Experience APIs -->