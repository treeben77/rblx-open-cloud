Exceptions
=============================

.. currentmodule:: rblx-open-cloud

.. exception:: rblx_opencloudException()

   Base exception for the library, raised when the library recieves an unexpected HTTP code.

.. exception:: InvalidKey()

   The api key is invalid or doesn't have sufficent permissions to do the requested task.

.. exception:: NotFound()

   An item in the request, such as a ``datastore``, ``key``, ``version`` or ``place`` was not found.

.. exception:: RateLimited()

   You're being rate limited. Try again in a minute.
   
.. exception:: ServiceUnavailable()

   Roblox is currently experiencing downtime.

.. exception:: PreconditionFailed()

   ``exclusive_create`` is ``True`` and the key already has a value or the current version doesnt match ``previous_version``. This is currently only raised by :meth:`rblx-open-cloud.DataStore.set`

   .. attribute:: value 

         The key's current value

         :type: str
   
   .. attribute:: info 

         The key metadata.

         :type: :class:`rblx-open-cloud.EntryInfo`

.. exception:: InvalidAsset()

   The asset you upload is the wrong type, or is corrupted.

   .. versionadded:: 1.1

.. exception:: ModeratedText()

   Text in the request was filtered by Roblox.

   .. versionadded:: 1.3

.. exception:: InvalidCode()

   The oauth2 code/access token/refresh token is invalid.

   .. versionadded:: 1.3

.. exception:: InsufficientScope()

   The oauth2 authorization doesn't have the required scope.

   .. versionadded:: 1.3

   .. attribute:: scope 

         space-seperated string of scopes Roblox expected.

         :type: str