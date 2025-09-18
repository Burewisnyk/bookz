from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..exceptions.exceptions import *
from ..services.dto_models import (DepositoryDTO, NewDepositoryDTO, AuthorDTO, NewAuthorDTO, BookDTO, NewBookDTO,
                                   BookCopyDTO, NewBookCopyDTO, CustomerDTO, NewCustomerDTO, FullNameDTO, StringDTO)
from ..enums.enums import BookStatus, BookStatement
from ..services.service import BookService
from ..db import get_session
from ..repositories.init_db import init_db

router = APIRouter()


def get_service(db: Session = Depends(get_session)) -> BookService:
    return BookService(db)


#Depository endpoints
@router.post("/depository/new")
def create_new_depository(depo: NewDepositoryDTO):
    return init_db(depo)

@router.get("/depository/status", response_model=DepositoryDTO)
async def get_depository_status(service: BookService = Depends(get_service)) -> DepositoryDTO:
    depo = service.depository_status()
    return depo


#Author endpoints
@router.get("/author/{author_id}")
async def get_author(author_id: int, service: BookService = Depends(get_service)) -> AuthorDTO:
    try:
        return service.find_author_by_id(author_id)
    except AuthorNotFound:
        raise HTTPException(status_code=404, detail="Author not found")


@router.get("/author/fullname")
async def get_author_by_fullname(full_name: FullNameDTO, service: BookService = Depends(get_service)) -> AuthorDTO:
    try:
        return service.find_author_by_full_name(full_name)
    except AuthorNotFound:
        raise HTTPException(status_code=404, detail="Author not found")


@router.post("/author/")
async def create_author(author: NewAuthorDTO, service: BookService = Depends(get_service)) -> AuthorDTO:
    return service.create_author(author)


@router.put("/author/")
async def change_author(author: AuthorDTO, service: BookService = Depends(get_service)) -> AuthorDTO:
    try:
        return service.update_author(author)
    except AuthorNotFound:
        raise HTTPException(status_code=404, detail="Author whit this id not found")
    except AuthorUpdateConflict as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/author/{author_id}")
async def delete_author(author_id: int, service: BookService = Depends(get_service)) -> AuthorDTO:
    try:
        return service.delete_author_by_id(author_id)
    except AuthorNotFound:
        raise HTTPException(status_code=404, detail="Author not found")
    except BookPresentInDatabase as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/author/without-book")
async def delete_authors_without_book(service: BookService = Depends(get_service)) -> list[AuthorDTO]:
    try:
        return service.delete_authors_without_book()
    except AuthorNotFound:
        raise HTTPException(status_code=404, detail="Authors without books not found")


#Book endpoints
@router.get("/book/{book_id}")
async def get_book_by_id(book_id: int, service: BookService = Depends(get_service)) -> BookDTO:
    try:
        return service.find_book_by_id(book_id)
    except BookNotFound:
        raise HTTPException(status_code=404, detail="Book not found")


@router.get("/book/isbn/{isbn}")
async def get_book_by_isbn(isbn: str, service: BookService = Depends(get_service)) -> BookDTO:
    try:
        return service.find_book_by_isbn(isbn)
    except BookNotFound:
        raise HTTPException(status_code=404, detail="Book not found")


@router.post("/book/")
async def create_book(book: NewBookDTO, service: BookService = Depends(get_service)) -> BookDTO:
    try:
        return service.create_book(book)
    except BookPresentInDatabase as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/book/")
async def delete_book(book_id: int, service: BookService = Depends(get_service)) -> BookDTO:
    try:
        return service.delete_book(book_id)
    except BookCopyBorrowed as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BookNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/book/without-copies")
async def delete_books_without_copies(service: BookService = Depends(get_service)) -> list[BookDTO]:
    try:
        return service.delete_books_without_copies()
    except BookNotFound:
        raise HTTPException(status_code=404, detail=f"Books without copies not found")


#BookCopy endpoints
@router.get("/book-copy/{id}")
async def get_book_copy_by_id(book_id: int, service: BookService = Depends(get_service)) -> BookCopyDTO:
    try:
        return service.find_book_copy(book_id)
    except BookCopyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/book-copy/status/{status}")
async def get_book_copy_by_status(status: BookStatus, service: BookService = Depends(get_service)) -> list[BookCopyDTO]:
    try:
        return service.find_book_copies_for_status(status)
    except BookCopyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/book-copy/statement/{status}")
async def get_book_copy_by_status(statement: BookStatement,
                                  service: BookService = Depends(get_service)) -> list[BookCopyDTO]:
    try:
        return service.find_book_copies_for_statement(statement)
    except BookCopyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/book-copy/")
async def create_book_copy(book_copy: NewBookCopyDTO, service: BookService = Depends(get_service)) -> BookCopyDTO:
    try:
        return service.create_book_copy(book_copy)
    except StorageSpaceIsNotSufficient as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BookNotFound as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/book-copy/{id}/status/{status}")
async def change_book_copy_status(copy_id: int, status: BookStatus,
                                  service: BookService = Depends(get_service)) -> BookCopyDTO:
    try:
        return service.change_book_copy_status(copy_id=copy_id, status=status)
    except StorageSpaceIsNotSufficient as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BookCopyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/book-copy/{id}/statement/{statement}")
async def change_book_copy_statement(copy_id: int, statement: BookStatement,
                                     service: BookService = Depends(get_service)) -> BookCopyDTO:
    try:
        return service.change_book_copy_statement(copy_id=copy_id, statement=statement)
    except WrongNewStatement as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BookCopyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/book-copy/{id}")
async def delete_book_copy(copy_id: int, service: BookService = Depends(get_service)) -> BookCopyDTO:
    try:
        return service.delete_book_copy(copy_id=copy_id)
    except BookCopyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BookCopyBorrowed as e:
        raise HTTPException(status_code=409, detail=str(e))


#Customer endpoints
@router.get("/customer/{id}")
async def get_customer(customer_id: int, service: BookService = Depends(get_service)) -> CustomerDTO:
    try:
        return service.find_customer_by_id(customer_id)
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/customer/email/{email}")
async def get_customer_by_email(email: str, service: BookService = Depends(get_service)) -> CustomerDTO:
    try:
        return service.find_customer_by_email(email)
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/customer/phone/{phone}")
async def get_customer_by_phone(phone: str, service: BookService = Depends(get_service)) -> CustomerDTO:
    try:
        return service.find_customer_by_phone(phone)
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("customer/fullname")
async def get_customer_by_fullname(fullname: FullNameDTO, service: BookService = Depends(get_service)) -> CustomerDTO:
    try:
        return service.find_customer_by_fullname(fullname)
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/customer/")
async def create_customer(customer: NewCustomerDTO, service: BookService = Depends(get_service)) -> CustomerDTO:
    try:
        return service.create_customer(customer)
    except EmailValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PhoneValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except CustomerFullNameAlreadyExist as e:
        raise HTTPException(status_code=409, detail=str(e))
    except CustomerPhoneAlreadyExist as e:
        raise HTTPException(status_code=409, detail=str(e))
    except CustomerEmailAlreadyExist as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/customer/{customer_id}/phone/")
async def change_customer_phone_number(customer_id: int, phone: StringDTO,
                                       service: BookService = Depends(get_service)) -> CustomerDTO:
    try:
        return service.change_customer_phone_number(customer_id=customer_id, phone=phone)
    except PhoneValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/customer/{customer_id}/email/")
async def change_customer_email(customer_id: int, email: StringDTO,
                                       service: BookService = Depends(get_service)) -> CustomerDTO:
    try:
        return service.change_customer_email(customer_id, email)
    except EmailValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
