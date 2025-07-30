class BirthProfileError(Exception):
    pass

class BirthProfileNotFoundError(BirthProfileError):
    pass

class BirthProfileAlreadyExistsError(BirthProfileError):
    pass

class DataStoreError(BirthProfileError):
    pass
