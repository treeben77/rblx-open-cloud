Webhook
=============================

.. currentmodule:: rblx-open-cloud

.. class:: Webhook(secret=None, api_key=None)

    Represents a Roblox outgoing webhook. It is used to validate and process webhook events.

    .. versionadded:: 1.4

    :param Optional[Union[str, bytes]] secret: Random letters only known by Roblox and the server to validate requests.
    :param str api_key: Your API key created from `Creator Dashboard <https://create.roblox.com/credentials>`__ with access to all objects that are generated in events.

    .. attribute:: secret 

        The webhook secret that is used to validate the event origins.

        :type: Optional[bytes]
    
    .. method:: process_notification(body, secret_header=None, validate_signature=True)

        Processes a HTTP webhook event and returns a response text and status code tuple. Example for Flask:
        
        .. code:: python

            @app.route('/webhook-roblox', methods=["POST"])
            def webhook_roblox():
                return webhook.process_notification(body=request.data, secret_header=request.headers["Roblox-Signature"])

        :returns: tuple[str, int]
        :param bytes body: The HTTP raw body.
        :param bytes secret_header: The raw value of the ``Roblox-Signature`` header.
        :param bool validate_signature: Wether to validate the signature or not. This should not be disabled in production.
        :raises rblx-open-cloud.UnknownEventType: Recieved an unsupported event type from Roblox.
        :raises rblx-open-cloud.UndefinedEventType: Recieved an event that doesn't have an event callback register.

    .. decorator:: event

        Register event callbacks with this decorator. The allowed function names, and the notification type they return is as follows:

        .. list-table::
            :widths: 30 30 40
            :header-rows: 1

            * - Event Name
              - Notification Type
              - Event Description
            * - ``on_test``
              - :class:`rblx-open-cloud.TestNotification`
              - Triggers when the user clicks 'Test Response' on the Webhook configuration page
            * - ``on_right_to_erasure_request``
              - :class:`rblx-open-cloud.RightToErasureRequestNotification`
              - Triggers when a right to erause request is recieved.

        :raises ValueError: Attempted to bind an event to an unkown type.

.. class:: Notification()

    Represents a recieved webhook event.

    .. versionadded:: 1.4

    .. warning::

        This class is not designed to be created by users. It is inherited by :class:`rblx-open-cloud.TestNotification`, and :class:`rblx-open-cloud.RightToErasureRequestNotification`

    .. attribute:: notification_id 

        A unique ID differentiating every notification. If a notification with the same ID is recieved, it should be treated as a duplicate and ignored. 

        :type: str

    .. attribute:: timestamp 

        The time the event was created.

        :type: datetime.datetime

    .. attribute:: webhook 

        The webhook this event was created by.

        :type: :class:`rblx-open-cloud.Webhook`

.. class:: TestNotification()

    Represents a recieved webhook event triggered by the user pressing 'Test Response' on the webhook configuration page.

    .. versionadded:: 1.4

    .. warning::

        This class is not designed to be created by users. It is returned ``on_test`` events from :meth:`rblx-open-cloud.Webhook.event`.

    .. attribute:: notification_id 

        A unique ID differentiating every notification. If a notification with the same ID is recieved, it should be treated as a duplicate and ignored. 

        :type: str

    .. attribute:: timestamp 

        The time the event was created.

        :type: datetime.datetime

    .. attribute:: webhook 

        The webhook this event was created by.

        :type: :class:`rblx-open-cloud.Webhook`

    .. attribute:: user 

        The user who triggered the test.

        :type: :class:`rblx-open-cloud.User`

.. class:: RightToErasureRequestNotification()

    Represents a recieved webhook event triggered by a user requesting Roblox to erase all their user data.

    .. versionadded:: 1.4

    .. warning::

        This class is not designed to be created by users. It is returned ``on_right_to_erasure_request`` events from :meth:`rblx-open-cloud.Webhook.event`.

    .. attribute:: notification_id 

        A unique ID differentiating every notification. If a notification with the same ID is recieved, it should be treated as a duplicate and ignored. 

        :type: str

    .. attribute:: timestamp 

        The time the event was created.

        :type: datetime.datetime

    .. attribute:: webhook 

        The webhook this event was created by.

        :type: :class:`rblx-open-cloud.Webhook`

    .. attribute:: user_id 

        The ID of the user which created the request.

        :type: int

    .. attribute:: experiences 

        A list of experiences to remove user data from.

        :type: list[:class:`rblx-open-cloud.Experience`]