"""Safe profile-configuration failures."""


class ProfileError(Exception):
    """Base class for profile bundle errors."""


class ProfileConfigurationError(ProfileError, ValueError):
    """Raised when profile inputs cannot be validated safely."""

    def __init__(self) -> None:
        super().__init__("profile configuration validation failed")
