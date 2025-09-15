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

    def find_free_place(self, number: int) -> list[int]:
        stmt = (select(Placement.id).where(Placement.status == PlacementStatus.FREE).limit(number))
        return list(self.session.scalars(stmt).all())

    def update_place_status(self, place_id: int, status: PlacementStatus) -> Placement:
        stmt = (
            update(Placement)
            .where(Placement.id == place_id)
            .values(status=status)
            .returning(Placement)
        )
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

    def find_author_by_id_for_update(self, author_id: int) -> Author | None:
        stmt = (
            select(Author)
            .where(Author.id == author_id)
            .with_for_update()
            .options(selectinload(Author.books))
        )
        return self.session.scalar(stmt)

    def create_author(self, new_author: dict) -> Author:
        stmt = (
            insert(Author)
            .values(new_author)
            .returning(Author)
        )
        author = self.session.scalar(stmt)
        return author

    def update_author(self, new_author: dict) -> Author | None:
        stmt = (
            update(Author)
            .values(new_author)
            .where(Author.id == new_author["id"])
            .returning(Author)
        )
        return self.session.scalar(stmt)

    def delete_author(self, author: Author) -> Author:
        return self.delete_author_by_id(author.id)

    def delete_author_by_id(self, author_id: int) -> Author:
        stmt = (
            delete(Author)
            .where(Author.id == author_id)
            .returning(Author)
        )
        return self.session.scalar(stmt)

    def find_book_by_id(self, book_id: int) -> Book | None:
        stmt = (
            select(Book)
            .where((Book.id == book_id))
            .options(selectinload(Book.authors), selectinload(Book.copies))
        )
        return self.session.scalar(stmt)

    def find_book_by_isbn(self, isbn: str) -> Book | None:
        stmt = (
            select(Book)
            .where((Book.isbn == isbn))
            .options(selectinload(Book.authors), selectinload(Book.copies))
        )
        return self.session.scalar(stmt)

    def create_book(self, book: dict) -> Book:
        stmt =(
            insert(Book)
            .values(book)
            .returning(Book)
        )
        return self.session.scalar(stmt)

    def delete_book(self, book: Book) -> None:
        return self.delete_book_by_id(book.id)

    def delete_book_by_id(self, book_id: int) -> None:
        pass

    #Book-Author relation
    def find_books_by_author_id(self, author_id: int) -> list[int]:
        stmt = (
            select(BookAuthor.book_id)
            .where(BookAuthor.author_id == author_id)
        )
        return list(self.session.scalars(stmt).all())

    def create_author_book_rel(self, book_id: int, author_id: int) -> BookAuthor:
        stmt = (
            insert(BookAuthor)
            .values({"book_id" : book_id, "author_id" : author_id})
            .returning(BookAuthor)
        )
        return self.session.scalar(stmt)


    #BookCopies
    def find_book_copy(self, id: int) -> BookCopy | None:
        stmt = (
            select(BookCopy)
            .where((BookCopy.id == id))
            .options(selectinload(BookCopy.customer),
                     selectinload(BookCopy.book),
                     selectinload(BookCopy.placement))
        )
        return self.session.scalar(stmt)

    def find_book_copies_by_book_id(self, book_id: int) -> list[BookCopy]:
        stmt = (
            select(BookCopy)
            .where(BookCopy.book_id == book_id)
            .options(selectinload(BookCopy.customer), selectinload(BookCopy.book))
        )
        return list(self.session.scalars(stmt).all())

    def create_book_copy(self, book_copy: dict) -> BookCopy:
        stmt = (
            insert(BookCopy)
            .values(book_copy)
            .returning(BookCopy)
        )
        return self.session.scalar(stmt)

    def delete_book_copy(self, id: int) -> BookCopy:
        stmt = (
            delete(BookCopy)
            .where(BookCopy.id == id)
            .returning(BookCopy)
        )
        return self.session.scalar(stmt)

