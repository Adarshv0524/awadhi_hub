# app/core/permissions.py

from typing import Any, Dict, Optional


class Role:
    ADMIN = "admin"
    SENIOR_MODERATOR = "senior_moderator"
    MODERATOR = "moderator"
    REGISTERED = "registered"
    GUEST = "guest"


# simple hierarchy (higher number = more power)
ROLE_RANK = {
    Role.GUEST: 0,
    Role.REGISTERED: 1,
    Role.MODERATOR: 2,
    Role.SENIOR_MODERATOR: 3,
    Role.ADMIN: 4,
}


class Permission:
    """
    Permission bits. We start with a small, clear set that we can
    extend later as other modules come online.
    """
    MANAGE_USERS = 1 << 0          # admin create/update users
    MODERATE_SUBMISSIONS = 1 << 1  # moderation actions
    VIEW_AUDIT_LOGS = 1 << 2
    MANAGE_SETTINGS = 1 << 3
    # 1 << 4, 1 << 5 ... reserved for future features


def has_permission(user_permissions: int, perm_bit: int) -> bool:
    return bool(user_permissions & perm_bit)


def role_at_least(user_role: str, required_role: str) -> bool:
    """
    Compare roles using ROLE_RANK mapping.
    Unknown roles default to rank 0 (least).
    """
    return ROLE_RANK.get(user_role, 0) >= ROLE_RANK.get(required_role, 0)


def check_abac(
    permission_scopes: Optional[Dict[str, Any]],
    action: str,
    resource: Dict[str, Any],
) -> bool:
    """
    Very small, generic ABAC checker.

    Expected format of permission_scopes (example):
        {
          "moderation:approve": {
              "authors": ["tulsidas", "kabir"],
              "max_priority": 5
          }
        }

    Then, for action="moderation:approve" and resource like:
        {"author_slug": "tulsidas", "priority": 3}

    - If no scope for this action -> allow (we treat absence as 'no extra ABAC constraints')
      (We can tighten this later if needed.)
    - Else:
        * if "authors" in scope -> resource["author_slug"] must be in that list.
        * if "max_priority" in scope -> resource["priority"] <= max_priority
    """
    if not permission_scopes:
        return True

    action_scope = permission_scopes.get(action)
    if not action_scope:
        # No constraints defined for this action => allow.
        return True

    # Authors constraint
    allowed_authors = action_scope.get("authors")
    author_slug = resource.get("author_slug")
    if allowed_authors is not None and author_slug is not None:
        if author_slug not in allowed_authors:
            return False

    # Priority constraint
    max_priority = action_scope.get("max_priority")
    priority = resource.get("priority")
    if max_priority is not None and priority is not None:
        try:
            if int(priority) > int(max_priority):
                return False
        except (TypeError, ValueError):
            # If we can't compare, be conservative and deny
            return False

    return True
