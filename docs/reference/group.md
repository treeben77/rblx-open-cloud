# Group

This reference documents APIs relating to groups (also known as *communities*).

::: rblxopencloud.Group
    options:
        merge_init_into_class: true

## Non-creatable Dataclasses

::: rblxopencloud.GroupJoinRequest
    options:
        inherited_members: false

::: rblxopencloud.GroupMember
    options:
        inherited_members: false
        filters:
            - "!fetch_role$"

::: rblxopencloud.GroupRole

::: rblxopencloud.GroupRolePermissions

::: rblxopencloud.GroupShout

::: rblxopencloud.GroupAuditLogEntry

## Enums

::: rblxopencloud.GroupAuditLogEntryActionType

## Types

::: rblxopencloud.GroupAuditLogEntryDescription
