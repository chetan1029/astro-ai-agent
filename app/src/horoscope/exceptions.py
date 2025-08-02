class HoroscopeError(Exception):
    pass

class HoroscopeNotFoundError(HoroscopeError):
    pass

class HoroscopeAlreadyExistsError(HoroscopeError):
    pass

class DataStoreError(HoroscopeError):
    pass
