"""Domain exceptions surfaced as concise user-facing errors."""


class ShamaranError(Exception):
    """Base class for expected Shamaran failures."""


class ConfigurationError(ShamaranError):
    pass


class ProviderError(ShamaranError):
    pass


class WorkspaceSecurityError(ShamaranError):
    pass


class ToolValidationError(ShamaranError):
    pass


class CommandBlockedError(ShamaranError):
    pass


class GitToolError(ShamaranError):
    pass


class MemoryStoreError(ShamaranError):
    pass
