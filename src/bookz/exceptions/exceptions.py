class AuthorNotFound(Exception):
    pass

class AuthorUpdateConflict(Exception):
    pass

class BookNotFound(Exception):
    pass

class BookPresentInDatabase(Exception):
    pass

class BookUpdateConflict(Exception):
    pass

class StorageSpaceIsNotSufficient(Exception):
    pass

class BookCopyBorrowed(Exception):
    pass

class BookCopyNotFound(Exception):
    pass

class CustomerMustBeGiven(Exception):
    pass

class CustomerNotFound(Exception):
    pass

class CustomerEmailAlreadyExist(Exception):
    pass

class CustomerPhoneAlreadyExist(Exception):
    pass

class CustomerFullNameAlreadyExist(Exception):
    pass

class EmailValidationError(Exception):
    pass

class PhoneValidationError(Exception):
    pass

class WrongNewStatement(Exception):
    pass

class NullValueNotAllowedException(Exception):
    pass

class ProhibitionOfInsertIDException(Exception):
    pass