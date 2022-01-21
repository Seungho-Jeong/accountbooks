class AbstractException(Exception):
    def __init__(self, message, status=400):
        self.message = message
        self.status = status


class InvalidValueException(AbstractException):
    pass


class DataTypeException(AbstractException):
    pass


class DuplicationException(AbstractException):
    pass


class UnauthorizedException(AbstractException):
    def __init__(self, message="login required.", status=401):
        self.message = message
        self.status = status


class PermissionException(AbstractException):
    def __init__(self, message="permission denied.", status=403):
        self.message = message
        self.status = status


class DataTooLongException(AbstractException):
    def __init__(self, message="data too long.", status=413):
        self.message = message
        self.status = status
