from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.orm import Session, selectinload, joinedload
from .orm_models import Author, Book, BookAuthor, BookCopy, Customer, Placement
from ..enums.enums import PlacementStatus,BookStatus, BookStatement


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
        stmt = (select(Placement.id)
                .where(Placement.status == PlacementStatus.FREE)
                .with_for_update()
                .limit(number))
        return list(self.session.scalars(stmt).all())

    def change_place_status(self, place_id: int, status: PlacementStatus) -> Placement:
        stmt = (
            update(Placement)
            .where(Placement.id == place_id)
            .values(status=status)
            .returning(Placement)
        )
        return self.session.scalar(stmt)

    def change_places_status(self, place_ids: list[int], status: PlacementStatus) -> list[Placement]:
        stmt = (
            update(Placement)
            .where(Placement.id.in_(place_ids))
            .values(status=status)
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

    def find_author_by_id(self, author_id: int, by_update: bool = False) -> Author | None:
        stmt = (
            select(Author)
            .where((Author.id == author_id))
            .options(selectinload(Author.books))
        )
        if by_update:
            stmt = stmt.with_for_update()
        return self.session.scalar(stmt)

    def find_authors_without_book(self, for_update: bool = False) -> list[int]:
        stmt = (
            select(Author.id)
            .outerjoin(Author.books)
            .filter(Author.books == None)
        )
        if for_update:
            stmt = stmt.with_for_update()
        return list(self.session.scalars(stmt).all())

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
        return self.delete_author_by_id(author.id)  #type: ignore

    def delete_author_by_id(self, author_id: int) -> Author:
        stmt = (
            delete(Author)
            .where(Author.id == author_id)
            .returning(Author)
        )
        return self.session.scalar(stmt)

    def delete_authors_by_ids(self, author_ids: list[int]) -> list[Author]:
        stmt = (
            delete(Author)
            .where(Author.id.in_(author_ids))
            .returning(Author)
        )
        return list(self.session.scalars(stmt).all())

    #Book
    def find_book_by_id(self, book_id: int, for_update: bool = False) -> Book | None:
        stmt = (
            select(Book)
            .where((Book.id == book_id))
            .options(selectinload(Book.authors), joinedload(Book.copies))
        )
        if for_update:
            stmt = stmt.with_for_update(of=(Book, BookCopy))
        return self.session.scalars(stmt).one_or_none()

    def find_book_by_isbn(self, isbn: str) -> Book | None:
        stmt = (
            select(Book)
            .where((Book.isbn == isbn))
            .options(selectinload(Book.authors), selectinload(Book.copies))
        )
        return self.session.scalar(stmt)

    def find_book_without_copy(self, for_update: bool = False) -> list[Book]:
        stmt = (
            select(Book)
            .outerjoin(Book.copies)
            .where(Book.copies == None)
        )
        if for_update:
            stmt = stmt.with_for_update()
        return list(self.session.scalars(stmt).all())

    def create_book(self, book: dict) -> Book:
        stmt = (
            insert(Book)
            .values(book)
            .returning(Book)
        )
        return self.session.scalar(stmt)

    def delete_books(self, book_ids: list[int]) -> list[Book]:
        stmt = (
            delete(Book)
            .where(Book.book_id.in_(book_ids))
            .returning(Book)
        )
        return list(self.session.scalars(stmt).all())

    def delete_book_by_id(self, book_id: int) -> Book:
        stmt = (
            delete(Book)
            .where(Book.id == book_id)
            .returning(Book)
        )
        return self.session.scalar(stmt)

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
            .values({"book_id": book_id, "author_id": author_id})
            .returning(BookAuthor)
        )
        return self.session.scalar(stmt)

    #BookCopies
    def find_book_copy(self, copy_id: int) -> BookCopy | None:
        stmt = (
            select(BookCopy)
            .where((BookCopy.id == copy_id))
            .options(joinedload(BookCopy.book).options(joinedload(Book.authors)),
                     selectinload(BookCopy.customer))
        )
        return self.session.scalar(stmt)

    def find_book_copies_by_ids(self, ids: list[int]) -> list[BookCopy]:
        stmt = (
            select(BookCopy)
            .where(BookCopy.id.in_(ids))
            .options(joinedload(BookCopy.book).options(joinedload(BookCopy.authors)),
                     selectinload(BookCopy.customer))
        )
        return list(self.session.scalars(stmt).all())

    def find_book_copies_by_book_id(self, book_id: int, for_update: bool = False) -> list[BookCopy]:
        stmt = (
            select(BookCopy)
            .where(BookCopy.book_id == book_id)
            .options(joinedload(BookCopy.book).options(joinedload(Book.authors)),
                     selectinload(BookCopy.customer))
        )
        if for_update:
            stmt = stmt.with_for_update()
        return list(self.session.scalars(stmt).all())

    def find_book_copies_for_status(self, status: BookStatus) -> list[BookCopy]:
        stmt = (
            select(BookCopy)
            .where(BookCopy.status == status)
            .options(joinedload(BookCopy.book).options(joinedload(Book.authors)),
                     selectinload(BookCopy.customer))
        )
        return list(self.session.scalars(stmt).all())

    def find_book_copies_for_statement(self, statement: BookStatement) -> list[BookCopy]:
        stmt = (
            select(BookCopy)
            .where(BookCopy.statement == statement)
            .options(selectinload(BookCopy.customer),
                     selectinload(BookCopy.book),
                     selectinload(BookCopy.placement))
        )
        return list(self.session.scalars(stmt).all())

    def create_book_copy(self, book_copy: dict) -> BookCopy:
        stmt = (
            insert(BookCopy)
            .values(book_copy)
            .returning(BookCopy)
        )
        return self.session.scalar(stmt)

    def create_book_copies(self, book_copies: list[dict]) -> list[BookCopy]:
        stmt = (
            insert(BookCopy)
            .values(book_copies)
            .returning(BookCopy.id)
        )
        ids = list(self.session.scalars(stmt).all())
        return self.find_book_copies_by_ids(ids)

    def update_book_copy(self, copy_id: int, book_copy: dict) -> BookCopy:
        stmt = (
            update(BookCopy)
            .where(BookCopy.id == copy_id)
            .values(book_copy)
        )
        self.session.execute(stmt)
        return self.find_book_copy(copy_id)

    def delete_book_copy(self, copy_id: int) -> BookCopy | None:
        stmt = (
            delete(BookCopy)
            .where(BookCopy.id == copy_id)
            .returning(BookCopy)
        )
        return self.session.scalar(stmt)

    def delete_book_copies_by_ids(self, ids: list[int]) -> list[BookCopy]:
        stmt = (
            delete(BookCopy)
            .where(BookCopy.id.in_(ids))
            .returning(BookCopy)
        )
        return list(self.session.scalars(stmt).all())

    #Customer
    def find_customer_by_id(self, customer_id: int, for_update: bool = False) -> Customer | None:
        stmt = (
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .options(joinedload(Customer.borrowed_books)
                     .options(joinedload(BookCopy.book)
                              .options(joinedload(Book.authors)))
                    )
        )
        if for_update:
            stmt = stmt.with_for_update(of=(Customer, BookCopy))
        return self.session.scalars(stmt).one_or_none()

    def find_customer_by_email(self, email: str, for_update: bool = False) -> Customer | None:
        stmt = (
            select(Customer)
            .where(Customer.email == email)
            .options(joinedload(Customer.borrowed_books)
                     .options(joinedload(BookCopy.book)
                              .options(joinedload(Book.authors)))
                    )
        )
        if for_update:
            stmt = stmt.with_for_update(of=(Customer, BookCopy))
        return self.session.scalars(stmt).one_or_none()

    def find_customer_by_phone(self, phone: str, for_update: bool = False) -> Customer | None:
        stmt = (
            select(Customer)
            .where(Customer.phone == phone)
            .options(joinedload(Customer.borrowed_books)
                     .options(joinedload(BookCopy.book)
                              .options(joinedload(Book.authors)))
                    )
        )
        if for_update:
            stmt = stmt.with_for_update(of=(Customer, BookCopy))
        return self.session.scalars(stmt).one_or_none()

    def find_customer_by_fullname(self, fullname: dict, for_update: bool = False) -> Customer | None:
        stmt=(
            select(Customer)
            .where((Customer.first_name == fullname['first_name'])
                   & (Customer.last_name == fullname['last_name'])
                   & (Customer.middle_name == fullname['middle_name']))
            .options(joinedload(Customer.borrowed_books)
                     .options(joinedload(BookCopy.book)
                              .options(joinedload(Book.authors)))
                     )
        )
        if for_update:
            stmt = stmt.with_for_update(of=(Customer, BookCopy))
        return self.session.scalars(stmt).one_or_none()


    def create_customer(self, new_customer: dict) -> Customer:
        stmt = (
            insert(Customer)
            .values(new_customer)
            .returning(Customer)
        )
        return self.session.scalar(stmt)
    def update_customer(self, customer_id: int, new_customer: dict) -> Customer:
        stmt = (
            update(Customer)
            .where(Customer.customer_id == customer_id)
            .values(new_customer)
            .returning(Customer)
        )
        return self.session.scalar(stmt)
