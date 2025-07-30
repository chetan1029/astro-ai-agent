class AstroProfileError(Exception):
    pass

class AstroProfileNotFoundError(AstroProfileError):
    pass

class AstroProfileAlreadyExistsError(AstroProfileError):
    pass

class DataStoreError(AstroProfileError):
    pass
