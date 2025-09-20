from __future__ import  annotations
from pydantic import Field, BaseModel, ConfigDict, EmailStr, computed_field


from ..enums.enums import BookStatus, BookStatement


class AuthorDTO(BaseModel):
    id: int = Field(..., ge=0, description='Author id in database', examples=[1078, 204567])
    full_name: FullNameDTO = Field(..., description='Author full name. Must be unique', examples=[{
        "first_name": "Mark",
        "last_name": "Twen",
        "middle_name": None
    }])
    books: list['BookDTO'] | None = Field(None, description='List of books in library that this author has')

    model_config = ConfigDict(from_attributes=True)

class NewAuthorDTO(BaseModel):
    full_name: FullNameDTO = Field(..., description='New author full name. Must be unique', examples=[{
        "first_name": "",
        "last_name": "Savchu",
        "middle_name": None
    }])

    model_config = ConfigDict(from_attributes=True)


class PlacementDTO(BaseModel):
    id: int = Field(..., ge=0, examples=[578, 1265])
    line_id: str = Field(..., min_length=1, max_length=1, examples=["C", "D"])
    column_id: int = Field(..., ge=1, examples=[5, 7])
    shelf_id: str = Field(...,min_length=1, max_length=1, examples=["A", "F"])
    position: int = Field(..., ge=1, examples=[7, 12])

    @computed_field
    def position_code(self) -> str:
        return (self.line_id + str(self.column_id) + self.shelf_id + str(self.position)).upper()


class BookCopyDTO(BaseModel):
    copy_id: int = Field(..., ge=0, examples=[2490, 8732])
    book: BookDTO
    status: BookStatus = Field(BookStatus.UNKNOWN, examples=[BookStatus.AVAILABLE, BookStatus.BORROWED])
    statement: BookStatement = Field(BookStatement.NEW, examples=[BookStatement.NEW, BookStatement.REPAIR])
    placement: PlacementDTO | None = Field(None, examples=[{
        'id': 578,
        'line_id': "A",
        'column_id': 5,
        'shelf_id': "C",
        'position': 12,
        'position_code': "A5C12",
    }, None])
    customer: CustomerDTO | None = Field(None, examples=[None, {
        'full_name': {
            'first_name': "John",
            'last_name': "Doe"
        },
        'email': 'JohnDoe@gmail.com',
        'phone': '+380 66 644 3227',
        'landed_books': None
    }])

    model_config = ConfigDict(from_attributes=True)

class NewBookCopyDTO(BaseModel):
    book_id: int = Field(..., ge=0, examples=[490, 762])
    status: BookStatus = Field(BookStatus.UNKNOWN, examples=[BookStatus.AVAILABLE, BookStatus.BORROWED])
    statement: BookStatement = Field(BookStatement.NEW, examples=[BookStatement.NEW, BookStatement.REPAIR])
    placement_id: int | None = Field(None, examples=[32349, 1232])

    model_config = ConfigDict(from_attributes=True)

class BookDTO(BaseModel):
    book_id: int = Field(..., ge=0, examples=[238, 162])
    title: str = Field(..., min_length=1, max_length=120, examples=["1984"])
    publisher: str = Field(..., min_length=1, max_length=80, examples=["Penguin"])
    place_of_publication: str | None = Field(None, min_length=3, max_length=80, examples=["London"])
    published_year: int | None = Field(None, ge=1700, le=2100, examples=[2008])
    isbn: str | None = Field(None,min_length=10, max_length=20, examples=["978-01-41-036144"])
    pages: int | None = Field(None, ge=1, examples=[336])
    price: float | None = Field(None, ge=0, examples=[854.0])
    language: str | None = Field(None, min_length=2, max_length=3, examples=['en'])
    authors: list['AuthorDTO'] = Field(None, examples=[{
        'id': 48,
        'full_name': {
            'first_name': "George",
            'last_name': "Orwell"
        },
        'books': None
    }])
    book_copies: list[BookCopyDTO] | None = Field(None, examples=[{
        'id': 8217,
        'book': None,
        'status': BookStatus.AVAILABLE,
        'statement': BookStatement.NEW,
        'placement': {
            'id': 80328,
            'line_id': "H",
            'column_id': 8,
            'shelf_id': "D",
            'position': 18
        },
        'customer': None
    }])


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
    customer_id: int = Field(..., ge=0, examples=[490, 762])
    full_name: FullNameDTO = Field(...)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{1,6}$',
                       max_length=20)
    borrowed_books: list[BookCopyDTO] | None = Field(None)

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

    def __str__(self) -> str:
        return f"{self.last_name.upper()} {self.first_name} {self.middle_name if self.middle_name else ''}"

class DepositoryDTO(BaseModel):
    max_lines: str = Field(..., min_length=1, max_length=1)
    max_columns: int = Field(..., ge=1)
    max_shelves: str = Field(..., min_length=1, max_length=1)
    max_positions: int = Field(..., ge=1)
    total_places: int| None = Field(None, ge=0)
    books_in_storage: int | None = Field(None, ge=0)
    free_places: int | None = Field(None, ge=0)


class NewDepositoryDTO(BaseModel):
    lines: int = Field(6, ge=1, le=26, examples=[5])
    columns: int = Field(4, ge=1, examples=[6])
    shelves: int = Field(8, ge=1, le=26, examples=[8])
    positions: int = Field(20, ge=1, examples=[20])
    books_number: int = Field(200, ge=0, examples=[1200])
    max_books_copies_per_book: int = Field(5, ge=1, examples=[20])
    authors_number: int = Field(50, ge=0, examples=[500])
    customers_number: int = Field(100, ge=0, examples=[1000])


class StringDTO(BaseModel):
    string: str = Field(...)



