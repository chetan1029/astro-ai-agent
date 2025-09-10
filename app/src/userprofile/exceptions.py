class UserProfileError(Exception):
    pass


class UserProfileNotFoundError(UserProfileError):
    pass


class UserProfileAlreadyExistsError(UserProfileError):
    pass


class DataStoreError(UserProfileError):
    pass
