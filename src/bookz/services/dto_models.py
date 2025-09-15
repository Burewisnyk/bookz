from __future__ import  annotations
from pydantic import Field, BaseModel, ConfigDict, EmailStr
from ..enums.enums import BookStatus, BookStatement, PlacementStatus


class AuthorDTO(BaseModel):
    id: int = Field(..., ge=0)
    full_name: FullNameDTO = Field(...)
    books: list['BookDTO'] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)

class NewAuthorDTO(BaseModel):
    full_name: FullNameDTO = Field(...)

    model_config = ConfigDict(from_attributes=True)


class PlacementDTO(BaseModel):
    id: int = Field(..., ge=0)
    line_id: str = Field(..., min_length=1, max_length=1)
    column_id: int = Field(..., ge=1)
    shelf_id: str = Field(...,min_length=1, max_length=1)
    position: int = Field(..., ge=1)


class BookCopyDTO(BaseModel):
    id: int | None = Field(..., ge=0) # None when creation
    book: BookDTO
    status: BookStatus = Field(BookStatus.UNKNOWN)
    statement: BookStatement = Field(BookStatement.NEW)
    placement: PlacementDTO | None = Field(None)

    model_config = ConfigDict(from_attributes=True)

class NewBookCopyDTO(BaseModel):
    book_id: int = Field(..., ge=0)
    status: BookStatus = Field(BookStatus.UNKNOWN)
    statement: BookStatement = Field(BookStatement.NEW)
    placement: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)

class BookDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    publisher: str = Field(..., min_length=1, max_length=80)
    place_of_publication: str | None = Field(None, min_length=3, max_length=80)
    published_year: int | None = Field(None, ge=1700, le=2100)
    isbn: str | None = Field(None,min_length=10, max_length=20)
    pages: int | None = Field(None, ge=1)
    price: float | None = Field(None, ge=0)
    authors: list[AuthorDTO] | None = Field(None)
    book_copies: list[BookCopyDTO] | None = Field(None)
    language: str | None = Field(None, min_length=2, max_length=3)

    model_config = ConfigDict(from_attributes=True)


class NewBookDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    publisher: str = Field(..., min_length=1, max_length=80)
    place_of_publication: str | None = Field(None, min_length=3, max_length=80)
    published_year: int | None = Field(None, ge=1700, le=2100)
    isbn: str | None = Field(None,min_length=10, max_length=20)
    pages: int | None = Field(None, ge=1)
    price: float | None = Field(None, ge=0)
    authors: list[NewAuthorDTO] | None = Field(None)
    new_copies: int = Field(..., ge=1)
    copy_statement: BookStatement = Field(BookStatement.NEW)


class CustomerDTO(BaseModel):
    full_name: FullNameDTO = Field(...)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{1,6}$',
                       max_length=20)
    landed_books: list[BookCopyDTO] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)


class NewCustomerDTO(BaseModel):
    full_name: FullNameDTO = Field(...)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{1,6}$',
                       max_length=20)

class FullNameDTO(BaseModel):
    first_name: str = Field(..., min_length=3, max_length=40)
    last_name: str = Field(..., min_length=3, max_length=80)
    middle_name: str | None = Field(None, min_length=3, max_length=40)

class DepositoryDTO(BaseModel):
    max_lines: str = Field(..., min_length=1, max_length=1)
    max_columns: int = Field(..., ge=1)
    max_shelves: str = Field(..., min_length=1, max_length=1)
    max_positions: int = Field(..., ge=1)
    total_places: int| None = Field(None, ge=0)
    books_in_storage: int | None = Field(None, ge=0)
    free_places: int | None = Field(None, ge=0)


class NewDepositoryDTO(BaseModel):
    lines: int = Field(6, ge=1, le=26)
    columns: int = Field(4, ge=1)
    shelves: int = Field(8, ge=1, le=26)
    positions: int = Field(20, ge=1)
    books_number: int = Field(200, ge=0)
    max_books_copies_per_book: int = Field(5, ge=1)
    authors_number: int = Field(50, ge=0)
    customers_number: int = Field(100, ge=0)



