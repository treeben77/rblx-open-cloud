Exceptions
=============================

.. currentmodule:: rblx-open-cloud

.. exception:: rblx_opencloudException()

   Base exception for the library, raised when the library recieves an unexpected HTTP code.

.. exception:: InvalidToken()

   The api key is invalid or doesn't have sufficent permissions to do the requested task.

.. exception:: NotFound()

   An item in the request, such as a ``datastore``, ``key``, ``version`` or ``place`` was not found.

.. exception:: RateLimited()

   You're being rate limited. Try again in a minute.
   
.. exception:: ServiceUnavailable()

   Roblox is currently experiencing downtime (this happens almost weekly).