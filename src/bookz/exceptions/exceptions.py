

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