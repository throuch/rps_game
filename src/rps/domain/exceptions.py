class DomainError(Exception):
    pass


class PlayerNotFoundError(DomainError):
    pass


class PlayerNameConflictError(DomainError):
    pass


class GameNotFoundError(DomainError):
    pass
