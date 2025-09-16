import copy as c
import string
from ..repositories.orm_models import Author, Book, Customer, BookCopy
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
        tmp = c.deepcopy(author)
        tmp.full_name = FullNameDTO(
            first_name=tmp.first_name,
            last_name=tmp.last_name,
            middle_name=tmp.middle_name
        )
        return AuthorDTO.model_validate(tmp, from_attributes=True, context={"exclude": {"books"}})


class BookMapper:

    @staticmethod
    def dto_to_dict(book: BookDTO) -> dict:
        book_columns = Book.__table__.columns.keys()
        return {k: v for k, v in book.model_dump(exclude_unset=True).items()
                if k in book_columns}

    @staticmethod
    def new_dto_to_dict(book: NewBookDTO) -> dict:
        book_columns = Book.__table__.columns.keys()
        return {k: v for k, v in book.model_dump(exclude_unset=True).items()
                if k in book_columns}


    @staticmethod
    def orm_to_dto(book: Book) -> BookDTO:
        return BookDTO.model_validate(book, from_attributes=True, context={"exclude": {"authors"}})

# TODO
class BookCopyMapper:

    @staticmethod
    def dto_to_dict(book: BookCopyDTO) -> dict:
        pass

    @staticmethod
    def new_dto_to_dict(book: NewBookCopyDTO) -> dict:
        pass

    @staticmethod
    def orm_to_dto(book: BookCopy) -> BookCopyDTO:
        pass

class CustomerMapper:

    @staticmethod
    def dto_to_dict(customer:CustomerDTO) -> dict:
        customer_columns = Customer.__table__.columns.keys()
        customer_dict = customer.model_dump(exclude_unset=True)
        full_name = customer_dict.pop('full_name',{})
        customer_dict.update(full_name)
        return {k: v for k, v in customer_dict.items()
                if k in customer_columns}

    @staticmethod
    def new_dto_to_dict(customer:NewCustomerDTO) -> dict:
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

class PhoneMapper:

    @staticmethod
    def phone_number_to_united_style(phone: str) -> str:
        """Mapped phone number to format: +380 44 123 45 67"""
        MISSED_COUNTRY_CODE = '38'
        SPACES = [2, 4, 7, 9]
        phone_number = "".join( ch for ch in phone if ch not in string.punctuation or not ch.isspace())
        if phone_number[0] == '0':
            phone_number = MISSED_COUNTRY_CODE.join(phone_number)
        return "+".join((ch + " ") if i in SPACES else ch for i, ch in enumerate(phone_number))
