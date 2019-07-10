

class PikaxException(Exception):
    pass



class ReqException(PikaxException):
    pass

class PostKeyError(PikaxException):
    pass

class LoginError(PikaxException):
    pass

class IDError(PikaxException):
    pass

class ArtworkError(PikaxException):
    pass

class OtherUserPageError(PikaxException):
    pass

class UserError(PikaxException):
    pass
