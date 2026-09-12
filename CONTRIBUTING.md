We appreciate any and all contributions that improve rblx-open-cloud for all! Thank you for your contributions.

This guide is a work in progress. Currently it documents some standard naming conventions used by the library

### Method naming conventions

Methods (functions) are named in `camel_case`. When naming a method, the standard approach is to use `verb_nouns`. The verb is the action word, the nouns are the subject of the action. Some common verbs used in the library are:

| Verb | Description |
| --- | --- |
| `get_` | Used for functions that create an object, but do not fetch data from Roblox. For instance, `get_user` wound create an empty user object with an ID that can use other APIs. |
| `list_` | Fetches pages of objects from Roblox and iterates it as an object. If an endpoint is not a pages with cursors, use fetch instead and return a list. Use `search` if you are querying many different search queries |
| `fetch_` | Fetches the relevant object information from Roblox and returns it in the appropraite object. |
| `create_` | Requests an object to be created on Roblox, and then returns it if the API allows. |
| `update_` | Requests an existing object to be updated on Roblox, and then returns it if the API allows. Do not complete a second request to fetch the updated object. |
| `delete_` | Requests an object to be deleted on Roblox. |
| `search_` | Similar to `list` since these functions should be iterables, but is more aimed at discovery rather than listing all elements. |
| `generate_` | Usually utility functions generating secrets or URIs. However, this is not strict, for instance `User.generate_headshot` |

In some circumstances it may be beneficial to use a specific verb such a `refresh`, `revoke`, `accept`, `grant`, `archive` or `ban`.