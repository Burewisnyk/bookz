from ..repositories.orm_models import Author, Book, Customer
from ..enums import *
from ..services.dto_models import *



class AuthorMapper:

    @staticmethod
    def dto_to_dict(author: AuthorDTO) -> dict:
        author_columns = Author.__table__.columns.keys()
        author_dict = author.model_dump()
        full_name = author_dict.pop('full_name',{})
        author_dict.update(full_name)
        return {k: v for k, v in author_dict.items()
                if k in author_columns}

    @staticmethod
    def new_dto_to_dict(author: NewAuthorDTO) -> dict:
        author_columns = Author.__table__.columns.keys()
        author_dict = author.model_dump()
        full_name = author_dict.pop('full_name',{})
        author_dict.update(full_name)
        return {k: v for k, v in author.model_dump(exclude_unset=True).items()
                if k in author_columns}


    @staticmethod
    def orm_to_dto(author: Author) -> AuthorDTO:
        return AuthorDTO.model_validate(author)


class BookMapper:

    @staticmethod
    def dto_to_dict(book: BookDTO) -> dict:
        book_columns = Book.__table__.columns.keys()
        return {k: v for k, v in book.model_dump(exclude_unset=True).items()
                if k in book_columns}

    @staticmethod
    def orm_to_dto(book: Book) -> BookDTO:
        return BookDTO.model_validate(book)


class CustomMapper:

    @staticmethod
    def dto_to_dict(customer:CustomerDTO) -> dict:
        customer_columns = Customer.__table__.columns.keys()
        customer_dict = customer.model_dump(exclude_unset=True)
        full_name = customer_dict.pop('full_name',{})
        customer_dict.update(full_name)
        return {k: v for k, v in customer_dict.items()
                if k in customer_columns}

    @staticmethod
    def orm_to_dto(customer:Customer) -> CustomerDTO:
        return CustomerDTO.model_validate(customer)

class FullNameMapper:

    @staticmethod
    def dto_to_dict(full_name: FullNameDTO) -> dict:
        full_name_dict = full_name.model_dump(exclude_unset=True)
        return full_name_dict