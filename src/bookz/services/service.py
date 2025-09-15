from sqlalchemy.orm import Session
from .dto_models import *
from ..repositories.repository import BookRepository
from ..mappers.mappers import *
from ..exceptions.exceptions import *


class BookService:

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = BookRepository(session)

    def depository_status(self) -> DepositoryDTO:
        depo = DepositoryDTO(
            max_lines=self.repo.get_number_of_depository_lines(),
            max_columns=self.repo.get_number_of_depository_columns_in_line(),
            max_shelves=self.repo.get_number_of_depository_shelves_in_column(),
            max_positions=self.repo.get_number_of_depository_positions_in_shelve(),
            total_places=self.repo.get_number_of_depository_placements(),
            books_in_storage=self.repo.get_number_books_in_depository(),
            free_places=self.repo.get_number_of_free_places()
        )
        return depo

    # Author functions
    def find_author_by_id(self, author_id: int) -> AuthorDTO | None:
        author = self.repo.find_author_by_id(author_id)
        if not author:
            raise AuthorNotFound(f"Author with id {author_id} not found")
        return AuthorMapper.orm_to_dto(author)

    def find_author_by_full_name(self, author: FullNameDTO) -> AuthorDTO | None:
        author = self.repo.find_author(author=FullNameMapper.dto_to_dict(author))
        if not author:
            raise AuthorNotFound(f"Author with full name {author.last_name} {author.first_name} {author.middle_name}  "
                                 f"not found")
        return AuthorMapper.orm_to_dto(author)

    def create_author(self, author: NewAuthorDTO) -> AuthorDTO:
        with self.session.begin() as session:
            present_author = self.find_author_by_full_name(author.full_name)
            if present_author:
                return present_author
            author = self.repo.create_author(AuthorMapper.new_dto_to_dict(author=author))
            return AuthorMapper.orm_to_dto(author)

    def update_author(self, author: AuthorDTO) -> AuthorDTO:
        with self.session.begin() as session:
            author_by_id = self.repo.find_author_by_id(author.id)
            if not author_by_id:
                raise AuthorNotFound(f"Author with id {author.id} not found")
            unique_author = self.find_author_by_full_name(author.full_name)
            if unique_author and (author_by_id.id != unique_author.id):
                raise AuthorUpdateConflict(f"Author with full name {author.last_name} {author.first_name} "
                                           f"{author.middle_name} present in database")
            author = self.repo.update_author(AuthorMapper.dto_to_dict(author))
            return AuthorMapper.orm_to_dto(author)

    def delete_author_by_id(self, author_id: int) -> AuthorDTO:
        book_author = self.repo.find_books_by_author_id(author_id)
        if not book_author:
            raise BookPresentInDatabase(f"{len(book_author)} book(s) is present in repository. Delete before author "
                                        f"his book(s)")
        author = self.repo.delete_author_by_id(author_id)
        if not author:
            raise AuthorNotFound(f"Author with id {author_id} not found")
        return AuthorMapper.orm_to_dto(author)

    # Book functions
    def find_book_by_id(self, book_id: int) -> BookDTO:
        book = self.repo.find_book_by_id(book_id)
        if not book:
            raise BookNotFound(f"Book with id {book_id} not found")
        return BookMapper.orm_to_dto(book)

    def find_book_by_isbn(self, isbn: str) -> BookDTO:
        book = self.repo.find_book_by_isbn(isbn)
        if not book:
            raise BookNotFound(f"Book with isbn {isbn} not found")
        return BookMapper.orm_to_dto(book)

    def create_book(self, book: NewBookDTO) -> BookDTO:
        present_book = self.find_book_by_isbn(book.isbn)
        if not present_book:
            raise BookPresentInDatabase(f"Book with isbn {book.isbn} present in database")
        with self.session.begin() as session:
            new_book = self.repo.create_book(BookMapper.new_dto_to_dict(book))
            for author in book.authors:
                ath = self.repo.find_author(AuthorMapper.new_dto_to_dict(author))
                if not ath:
                    ath = self.repo.create_author(AuthorMapper.new_dto_to_dict(author))
                self.repo.create_author_book_rel(book_id=new_book.id, author_id=ath.id)  #type: ignore
            available_places = self.repo.find_free_place(book.new_copies)
            if len(available_places) < book.new_copies:
                raise StorageSpaceIsNotSufficient(f"Free place for {book.new_copies} of {book.title} is`t available ")
            for _ in book.copies:
                place = available_places.pop()
                new_book_copy = NewBookCopyDTO(
                    book_id=book.id,
                    status=BookStatus.AVAILABLE,
                    statement=book.copy_statement,
                    placement=place
                )
                self.repo.create_book_copy(BookCopyMapper.new_dto_to_dict(new_book_copy))
                self.repo.update_place_status(place_id=place, status=PlacementStatus.OCCUPIED)
        return self.find_book_by_isbn(book.isbn)

    def delete_book(self, book_id: int) -> BookDTO:
        book_copies = self.repo.find_book_copies_by_book_id(book_id)
        for book_copy in book_copies:
            if book_copy.status == BookStatus.BORROWED:
                raise BookCopyBorrowed(f"Book copy {book_copy.id}  of book {book_copy.book_id} is borrowed. "
                                     f"Change its status before delete")
        with self.session.begin() as session:
            book = self.repo.find_book_by_id(book_id)
            if not book:
                raise BookNotFound(f"Book with id {book_id} not found")
            for copy in book.copies:
                if copy.status == BookStatus.AVAILABLE:
                    self.repo.update_place_status(place_id=copy.place_id, status=PlacementStatus.FREE)
                self.repo.delete_book_copy(copy.id)
            return book

    # Book copies functions
    def find_book_copy(self, id: int) -> BookCopyDTO:
        book_copy = self.repo.find_book_copy(id)
        if not book_copy:
            raise BookCopyNotFound(f"Book copy with id {id} not found")
        return BookCopyMapper.orm_to_dto(book_copy)

    def


