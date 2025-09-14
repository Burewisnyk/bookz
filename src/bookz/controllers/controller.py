from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from ..repositories.orm_models import Book
from ..services.dto_models import *
from ..services.service import BookService
from ..db import get_session, close_db
from ..repositories.init_db import init_db

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(NewDepositoryDTO())
    yield
    close_db()



#Depository endpoints
@app.post("/depository/new")
async def create_new_depository(depo: NewDepositoryDTO):
    return init_db(depo)

@app.get("/depository/status")
async def get_depository_status() -> DepositoryDTO:
    service = BookService(session=get_session())
    depo = service.depository_status()
    return depo

#Author endpoints
@app.get("/author/{author_id}")
async def get_author(author_id: int) -> AuthorDTO:
    return service.find_author_by_id(author_id)

@app.get("/author/fullname")
async def get_author_by_fullname(full_name: FullNameDTO) -> AuthorDTO:
    return service.find_author_by_full_name(full_name)

@app.post("/author/", status_code=status.HTTP_201_CREATED)
async def create_author(author: NewAuthorDTO) -> AuthorDTO:
    return service.create_author(author)

@app.put("/author/")
async def change_author(author: AuthorDTO) -> AuthorDTO:
    pass

@app.delete("/author/{author_id}")
async def delete_author(author_id: int) -> None:
    pass

#Book endpoints
@app.get("/book/{book_id}")
async def get_book_by_id(book_id: int) -> BookDTO:
    pass

@app.get("/book/isbn/{isbn}")
async def get_book_by_isbn(isbn: str) -> BookDTO:
    pass

@app.post("/book/")
async def create_book(book: NewBookDTO) -> Book:
    pass

@app.put("/book/")
async def update_book(book: BookDTO) -> Book:
    pass

@app.delete("/book/")
async def delete_book(book_id: int) -> Book:
    pass

#BookCopy endpoints
@app.get("/book-copy/{id}")
async def get_book_copy_by_id(book_id: int) -> BookCopyDTO:
    pass

@app.post("/book-copy/")
async def create_book_copy(book_copy: BookCopyDTO) -> BookCopyDTO:
    pass

@app.put("/book-copy/{id}")
async def update_book_copy(book_copy: BookCopyDTO) -> BookCopyDTO:
    pass

@app.delete("/book-copy/{id}")
async def delete_book_copy(book_id: int) -> None:
    pass

#Customer endpoints
@app.get("/customer/{id}")
async def get_customer(customer_id: int) -> CustomerDTO:
    pass

@app.get("/customer/email/{email}")
async def get_customer_by_email(email: str) -> CustomerDTO:
    pass

@app.get("/customer/phone/{phone}")
async def get_customer_by_phone(phone: str) -> CustomerDTO:
    pass

@app.get("customer/fullname")
async def get_customer_by_fullname(fullname: FullNameDTO) -> CustomerDTO:
    pass
