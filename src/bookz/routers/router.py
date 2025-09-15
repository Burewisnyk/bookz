from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..exceptions.exceptions import *
from ..services.dto_models import *
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
async def get_depository_status(db: Session = Depends(get_session)) -> DepositoryDTO:
    service = BookService(db)
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


@router.post("/author/", status_code=status.HTTP_201_CREATED)
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

#BookCopy endpoints
@router.get("/book-copy/{id}")
async def get_book_copy_by_id(book_id: int, service: BookService = Depends(get_service)) -> BookCopyDTO:
    try:
        return service.find_book_copy(book_id)
    except BookCopyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/book-copy/")
async def create_book_copy(book_copy: BookCopyDTO, service: BookService = Depends(get_service)) -> BookCopyDTO:
    pass

@router.put("/book-copy/{id}")
async def update_book_copy(book_copy: BookCopyDTO, service: BookService = Depends(get_service)) -> BookCopyDTO:
    pass

@router.delete("/book-copy/{id}")
async def delete_book_copy(book_id: int, service: BookService = Depends(get_service)) -> None:
    pass

#Customer endpoints
@router.get("/customer/{id}")
async def get_customer(customer_id: int, service: BookService = Depends(get_service)) -> CustomerDTO:
    pass

@router.get("/customer/email/{email}")
async def get_customer_by_email(email: str, service: BookService = Depends(get_service)) -> CustomerDTO:
    pass

@router.get("/customer/phone/{phone}")
async def get_customer_by_phone(phone: str, service: BookService = Depends(get_service)) -> CustomerDTO:
    pass

@router.get("customer/fullname")
async def get_customer_by_fullname(fullname: FullNameDTO, service: BookService = Depends(get_service)) -> CustomerDTO:
    pass
