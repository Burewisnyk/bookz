from sqlite3 import IntegrityError

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.orm import Session, selectinload
from .orm_models import Author, Book, BookAuthor, BookCopy, Customer, Placement
from ..mappers.mappers import AuthorMapper
from ..services.dto_models import NewAuthorDTO, DepositoryDTO, AuthorDTO
from ..enums.enums import *


class BookRepository:

    def __init__(self, session: Session):
        self.session = session

    #Depository
    def get_number_of_depository_lines(self) -> str:
        stmt = (select(func.max(Placement.line_id)))
        return self.session.scalar(stmt)

    def get_number_of_depository_columns_in_line(self) -> int:
        stmt = (select(func.max(Placement.column_id)))
        return self.session.scalar(stmt)

    def get_number_of_depository_shelves_in_column(self) -> str:
        stmt = (select(func.max(Placement.shelf_id)))
        return self.session.scalar(stmt)

    def get_number_of_depository_positions_in_shelve(self) -> int:
        stmt = (select(func.max(Placement.position)))
        return self.session.scalar(stmt)

    def get_number_of_depository_placements(self) -> int:
        stmt = (select(func.count()).select_from(Placement))
        return self.session.scalar(stmt)

    def get_number_books_in_depository(self) -> int:
        stmt = (select(func.count()).select_from(Placement).where(Placement.status == PlacementStatus.OCCUPIED))
        return self.session.scalar(stmt)

    def get_number_of_free_places(self) -> int:
        stmt = (select(func.count()).select_from(Placement).where(Placement.status == PlacementStatus.FREE))
        return self.session.scalar(stmt)

    def find_free_place(self) -> int:
        stmt = (select(Placement.id).where(Placement.status == PlacementStatus.FREE).limit(1))
        return self.session.scalar(stmt)

    #Author
    def find_author(self, author: dict) -> Author | None:
        stmt = (
            select(Author)
            .where((Author.first_name == author["first_name"])
                   & (Author.last_name == author["last_name"])
                   & (Author.middle_name == author["middle_name"]))
            .options(selectinload(Author.books))
        )
        return self.session.scalar(stmt)

    def find_author_by_id(self, author_id: int) -> Author | None:
        stmt = (
            select(Author)
            .where((Author.id == author_id))
            .options(selectinload(Author.books))
        )
        return self.session.scalar(stmt)

    def create_author(self, new_author: dict) -> Author:
        author = self.find_author(new_author)
        if author:
            return author
        stmt = (
            insert(Author)
            .values(new_author)
        )
        author = self.session.execute(stmt).scalar_one()
        return author


    def update_author(self, author: Author) -> Author:
        pass

    def delete_author(self, author: Author) -> None:
        return self.delete_author_by_id(author.id)

    def delete_author_by_id(self, author_id: int) -> None:
        pass

    def create_book(self, book: Book) -> Book:
        pass

    def update_book(self, book: Book) -> Book:
        pass

    def delete_book(self, book: Book) -> None:
        return self.delete_book_by_id(book.id)

    def delete_book_by_id(self, book_id: int) -> None:
        pass
