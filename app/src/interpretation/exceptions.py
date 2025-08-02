class InterpretationError(Exception):
    pass

class InterpretationNotFoundError(InterpretationError):
    pass

class InterpretationAlreadyExistsError(InterpretationError):
    pass

class DataStoreError(InterpretationError):
    pass
