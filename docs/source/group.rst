Group
=============================

.. currentmodule:: rblx-open-cloud

.. class:: Group()

    Represents a group on Roblox. It can be used for both uploading assets, and accessing group information.

    .. versionadded:: 1.1

    :param int id: The group's ID.
    :param str api_key: Your API key created from `Creator Dashboard <https://create.roblox.com/credentials>`__ with access to this group.

    .. attribute:: id 

        The group's ID

        :type: int
      
    .. attribute:: name 

        The group's name. It is only present after calling :meth:`fetch_info`.

        :type: Optional[str]
      
    .. attribute:: description 

        The group's description. It is only present after calling :meth:`fetch_info`.

        :type: Optional[str]
      
    .. attribute:: created_at 

        The time the group was created. It is only present after calling :meth:`fetch_info`.

        :type: Optional[datetime.datetime]
      
    .. attribute:: updated_at 

        The time the group was last updated. It is only present after calling :meth:`fetch_info`.

        :type: Optional[datetime.datetime]
      
    .. attribute:: owner 

        The group's owner. It is only present after calling :meth:`fetch_info`.

        :type: Optional[:class:`rblx-open-cloud.User`]
      
    .. attribute:: member_count 

        The number of memebers in the group. It is only present after calling :meth:`fetch_info`.

        :type: Optional[int]
      
    .. attribute:: public_entry 

        Wether anyone can join the group without requesting to join or not. It is only present after calling :meth:`fetch_info`.

        :type: Optional[bool]
      
    .. attribute:: locked 

        Wether the group has been locked, moderated, or banned by Roblox. It is only present after calling :meth:`fetch_info`.

        :type: Optional[bool]
      
    .. attribute:: verified 

        Wether the group has a verified checkmark. It is only present after calling :meth:`fetch_info`.

        :type: Optional[bool]

    .. method:: upload_asset(file, asset_type, name, description, expected_robux_price=0)

        Uploads the file onto roblox as an asset with the provided name and description. It will return :class:`rblx-open-cloud.Asset` if the asset is processed instantly, otherwise it will return :class:`rblx-open-cloud.PendingAsset`. The following asset types and file formats are accepted:

        .. list-table::
            :widths: 50 50
            :header-rows: 1

            * - Asset Type
              - File Formats
            * - :attr:`rblx-open-cloud.AssetType.Decal`
              - ``.png``, ``.jpeg``, ``.bmp``, ``.tga``
            * - :attr:`rblx-open-cloud.AssetType.Audio`
              - ``.mp3``, ``.ogg``
            * - :attr:`rblx-open-cloud.AssetType.Model`
              - ``.fbx``

        The ``asset:read`` and ``asset:write`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        .. versionchanged:: 1.3
            It can now raise :class:`rblx-open-cloud.ModeratedText` if the name or description is invalid. It used to raise :class:`rblx-open-cloud.InvalidAsset`.
      
        :param io.BytesIO file: The file opened in bytes to be uploaded.
        :param rblx-open-cloud.AssetType asset_type: The type of asset you're uploading.
        :param str name: The name of your asset.
        :param str description: The description of your asset.
        :param str expected_robux_price: The amount of robux expected to upload. Fails if lower than actual price.

        :returns: Union[:class:`rblx-open-cloud.Asset`, :class:`rblx-open-cloud.PendingAsset`]
        :raises rblx-open-cloud.InvalidAsset: The file is not a supported, or is corrupted
        :raises rblx-open-cloud.ModeratedText: The name or description was moderated by Roblox's chat filter.
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. danger::

            Assets uploaded with Open Cloud can still get your account moderated if they break the Terms of Service.

            For OAuth2 applications, please read `this post by Hooksmith <https://devforum.roblox.com/t/public-beta-building-your-applications-with-oauth-20/2401354/36>`__.

    .. method:: update_asset(asset_id, file)

        Updates the file for an existing assest on Roblox. It will return :class:`rblx-open-cloud.Asset` if the asset is processed instantly, otherwise it will return :class:`rblx-open-cloud.PendingAsset`. The following asset types and file formats can be updated:

        .. list-table::
            :widths: 50 50
            :header-rows: 1

            * - Asset Type
              - File Formats
            * - :attr:`rblx-open-cloud.AssetType.Model`
              - ``.fbx``

        The ``asset:read`` and ``asset:write`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        .. versionchanged:: 1.3
            It can now raise :class:`rblx-open-cloud.ModeratedText` if the name or description is invalid. It used to raise :class:`rblx-open-cloud.InvalidAsset`.
        
        :param int asset_id: The ID of the asset to update.
        :param io.BytesIO file: The file opened in bytes to be uploaded.

        :returns: Union[:class:`rblx-open-cloud.Asset`, :class:`rblx-open-cloud.PendingAsset`]
        :raises rblx-open-cloud.ModeratedText: The name or description was moderated by Roblox's chat filter.
        :raises rblx-open-cloud.InvalidAsset: The file is not a supported, or is corrupted
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to read and write assets.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's servers are currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. danger::

            Assets uploaded with Open Cloud can still get your account moderated if they break the Terms of Service.

            For OAuth2 applications, please read `this post by Hooksmith <https://devforum.roblox.com/t/public-beta-building-your-applications-with-oauth-20/2401354/36>`__.

    .. method:: fetch_info()

      Updates the empty parameters in this Group object and returns it self with the group info.
      
      The ``group:read`` scope is required if authorized via `OAuth2 </oauth2>`__.

      .. versionadded:: 1.5

      :returns: :class:`rblx-open-cloud.Group`
      :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to access group data.
      :raises rblx-open-cloud.NotFound: The group could not be found.
      :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
      :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
      :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

    .. method:: fetch_shout()

      Returns :class:`rblx-open-cloud.GroupShout` with information about the group's current shout. It requires permission to view the shout from the API key owner or OAuth2 authorizing user.

      The ``group:read`` scope is required if authorized via `OAuth2 </oauth2>`__.

      .. versionadded:: 1.5

      :returns: :class:`rblx-open-cloud.GroupShout`
      :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to access group data.
      :raises rblx-open-cloud.NotFound: The group could not be found.
      :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
      :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
      :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
    
    .. method:: list_members(limit=None, role_id=None, user_id=None)

        Interates :class:`rblx-open-cloud.GroupMember` for each user in the group.
        
        The example below would iterate through every user in the group.
        
        .. code:: python

            for member in group.list_members():
                print(member)
        
        The ``group:read`` scope is required if authorized via `OAuth2 </oauth2>`__.

        .. versionadded:: 1.5

        :param Optional[int] limit: The maximum number of members to iterate. This can be ``None`` to return all members.
        :param Optional[int] role_id: If present, the api will only provide members with this role.
        :param Optional[int] user_id: If present, the api will only provide the member with this user ID.
        
        :returns: Iterable[:class:`rblx-open-cloud.GroupMember`]
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to access group data.
        :raises rblx-open-cloud.NotFound: The user could not be found.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
    
    .. method:: list_roles(limit=None)

        Interates :class:`rblx-open-cloud.GroupRole` for each role in the group.
        
        The ``group:read`` scope is required if authorized via `OAuth2 </oauth2>`__.

        .. versionadded:: 1.5

        :param Optional[int] limit: The maximum number of roles to iterate. This can be ``None`` to return all roles.
        
        :returns: Iterable[:class:`rblx-open-cloud.GroupRole`]
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to access group data.
        :raises rblx-open-cloud.NotFound: The user could not be found.
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: GroupMember()

  Represents a user inside of a group.

  .. versionadded:: 1.5

  .. warning::

      This class is not designed to be created by users. It a returned by by :class:`rblx-open-cloud.User.list_groups` and :class:`rblx-open-cloud.Group.list_members`.

  .. attribute:: id 

        The user's ID

        :type: int
  
  .. attribute:: role_id 

        The user's role ID in the group

        :type: int
  
  .. attribute:: group 

        The group this membership data relates to.

        :type: :class:`rblx-open-cloud.Group`
  
  .. attribute:: joined_at 

        The time this member joined the group.

        :type: :class:`datetime.datetime`
  
  .. attribute:: updated_at 

        The last time this user was updated (e.g. the role was changed)

        :type: :class:`datetime.datetime`

.. class:: GroupRole()

  Represents a role inside of a group.

  .. versionadded:: 1.5

  .. warning::

      This class is not designed to be created by users. It a returned by :class:`rblx-open-cloud.Group.list_roles`.

  .. attribute:: id 

        The role's unique ID

        :type: int
  
  .. attribute:: name 

        The role's name.

        :type: str
  
  .. attribute:: rank 

        The role's rank between 0 and 255.

        :type: int
  
  .. attribute:: description 

        The description set for this role, only visible if the authorizd user is the group owner.

        :type: Optional[str]
  
  .. attribute:: member_count 

        The number of members with this role. It is ``None`` for the guest role (rank 0)

        :type: Optional[int]
  
  .. attribute:: permissions 

        The :class:`rblx-open-cloud.GroupRolePermissions` for this role. This will be None unless the authorized user is the group owner, the authorized user's role is this role, or the role is the guest role.

        :type: Optional[:class:`rblx-open-cloud.GroupRolePermissions`]

.. class:: GroupRolePermissions()

  Represents a role's permissions inside of a group.

  .. versionadded:: 1.5

  .. warning::

      This class is not designed to be created by users. It a attribute of :class:`rblx-open-cloud.GroupRole`.

  .. attribute:: view_wall_posts 

      Allows the member to view the group's wall.

      :type: bool

  .. attribute:: create_wall_posts 

      Allows the member to send posts on the group's wall.

      :type: bool

  .. attribute:: delete_wall_posts 

      Allows the member to delete other member's posts on the wall.

      :type: bool

  .. attribute:: view_group_shout 

      Allows the member to view the group's current shout.

      :type: bool

  .. attribute:: create_group_shout 

      Allows the member to update the group's current shout.

      :type: bool

  .. attribute:: change_member_ranks 

      Allows the member to change lower ranked member's role.

      :type: bool

  .. attribute:: accept_join_requests 

      Allows the member to accept user join requests.

      :type: bool

  .. attribute:: exile_members 

      Allows the member to exile members from the group.

      :type: bool

  .. attribute:: manage_relationships 

      Allows the member to add and remove allies and enemies.

      :type: bool

  .. attribute:: view_audit_log 

      Allows the member to view the group's audit logs.

      :type: bool

  .. attribute:: exile_members 

      Allows the member to exile members from the group.

      :type: bool

  .. attribute:: spend_group_funds 

      Allows the member to spend group funds.

      :type: bool

  .. attribute:: advertise_group 

      Allows the member to create advertisements for the group.

      :type: bool

  .. attribute:: create_avatar_items 

      Allows the member to create avatar items for the group.

      :type: bool

  .. attribute:: manage_avatar_items 

      Allows the member to manage avatar items for the group.

      :type: bool

  .. attribute:: manage_experiences

      Allows the member to create, edit, and manage the group's experiences.

      :type: bool

  .. attribute:: view_experience_analytics

      Allows the member to view the analytics of the group's experiences.

      :type: bool

  .. attribute:: create_api_keys

      Allows the member to create Open Cloud API keys.

      :type: bool

  .. attribute:: manage_api_keys

      Allows the member to manage all Open Cloud API keys.

      :type: bool

.. class:: GroupShout()

  Represents a group shout.

  .. versionadded:: 1.5

  .. warning::

      This class is not designed to be created by users. It a returned by :class:`rblx-open-cloud.Group.fetch_shout`.

  .. attribute:: content 

      The shout message.

      :type: str

  .. attribute:: user 

      The user who created the shout.

      :type: :class:`rblx-open-cloud.User`

  .. attribute:: created_at 

      The time that the group shout was sent at.

      :type: datetime.datetime

  .. attribute:: first_created_at 

      The time that the first group shout of the group was sent at.

      :type: datetime.datetime