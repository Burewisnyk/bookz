from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from psycopg2.errors import UniqueViolation
from .dto_models import (DepositoryDTO, AuthorDTO, NewAuthorDTO, FullNameDTO, BookDTO, NewBookDTO, BookCopyDTO,
                         NewBookCopyDTO, CustomerDTO, StringDTO, NewCustomerDTO)
from ..enums.enums import BookStatus, PlacementStatus, BookStatement
from ..repositories.repository import BookRepository
from ..mappers.mappers import AuthorMapper, FullNameMapper, BookMapper, BookCopyMapper, CustomerMapper, PhoneMapper
from ..exceptions.exceptions import *
from ..validators.validators import PhoneValidator, EmailValidator


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
        try:
            with self.session.begin():
                present_author = self.find_author_by_full_name(author.full_name)
                if present_author:
                    return present_author
                author = self.repo.create_author(author=AuthorMapper.new_dto_to_dict(author))
            return AuthorMapper.orm_to_dto(author)
        except IntegrityError:
            #TODO
            raise Exception

    def update_author(self, author: AuthorDTO) -> AuthorDTO:
        try:
            with self.session.begin():
                author_by_id = self.repo.find_author_by_id(author.id)
                if not author_by_id:
                    raise AuthorNotFound(f"Author with id {author.id} not found")
                unique_author = self.find_author_by_full_name(author.full_name)
                if unique_author and (author_by_id.id != unique_author.id):
                    raise AuthorUpdateConflict(f"Author with full name: {str(author.full_name)} is available in database")
                author = self.repo.update_author(AuthorMapper.dto_to_dict(author))
            return AuthorMapper.orm_to_dto(author)
        except IntegrityError:
            #TODO
            raise Exception

    def delete_author_by_id(self, author_id: int) -> AuthorDTO:
        book_author = self.repo.find_books_by_author_id(author_id)
        if not book_author:
            raise BookPresentInDatabase(f"{len(book_author)} book(s) is present in repository. Delete author books "
                                        f"before deleting the author")
        author = self.repo.delete_author_by_id(author_id)
        if not author:
            raise AuthorNotFound(f"Author with id {author_id} not found")
        return AuthorMapper.orm_to_dto(author)

    def delete_authors_without_book(self) -> list[AuthorDTO]:
        with self.session.begin():
            authors = self.repo.find_authors_without_book(for_update=True)
            if not authors:
                raise AuthorNotFound(f"Author without books not found")
            authors = self.repo.delete_authors_by_ids(authors)
            authorsDTO: list[AuthorDTO] = []
            for author in authors:
                authorsDTO.append(AuthorMapper.orm_to_dto(author))
        return authorsDTO

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
            places = available_places.copy()
            if len(available_places) < book.new_copies:
                raise StorageSpaceIsNotSufficient(f"Free place for {book.new_copies} of {book.title} is`t available ")
            new_book_copies: list[dict] = []
            for _ in book.copies:
                place = available_places.pop()
                new_book_copies.append(BookCopyMapper.new_dto_to_dict(
                    NewBookCopyDTO(book_id=book.id,
                                   status=BookStatus.AVAILABLE,
                                   statement=book.copy_statement,
                                   placement_id=place)))
            self.repo.create_book_copies(new_book_copies)
            self.repo.change_places_status(place_ids=places, status=PlacementStatus.OCCUPIED)
        return self.find_book_by_isbn(book.isbn)

    def delete_book(self, book_id: int) -> BookDTO:
        with self.session.begin() as session:
            book = self.repo.find_book_by_id(book_id, for_update=True)
            if not book:
                raise BookNotFound(f"Book with id {book_id} not found")
            place_ids: list[int] = []
            copy_ids: list[int] = []
            for copy in book.copies:
                if copy.status == BookStatus.BORROWED:
                    raise BookCopyBorrowed(f"Book copy {copy.id}  of book '{book.title}' is borrowed. "
                                           f"Change its status before delete")
                if copy.status == BookStatus.AVAILABLE:
                    place_ids.append(copy.placement_id)
                copy_ids.append(copy.id)
            self.repo.delete_book_copies_by_ids(ids=copy_ids)
            self.repo.change_places_status(place_ids = place_ids, status=PlacementStatus.FREE)
            self.repo.delete_book_by_id(book.id) #type: ignore
        return book

    def delete_books_without_copies(self) -> list[BookDTO]:
        with self.session.begin() as session:
            books = self.repo.find_book_without_copy(for_update=True)
            if not books:
                raise BookNotFound(f"Books without copy found")
            book_ids: list[int] = []
            booksDTO: list[BookDTO] = []
            for book in books:
                book_ids.append(book.id)  #type: ignore
                booksDTO.append(BookMapper.orm_to_dto(book))
            books = self.repo.delete_books(bok_ids=book_ids)
        deleted_books: list[BookDTO] = []
        for book in books:
            deleted_books.append(BookMapper.orm_to_dto(book))
        return deleted_books

    # Book copies functions
    def find_book_copy(self, id: int) -> BookCopyDTO:
        book_copy = self.repo.find_book_copy(id)
        if not book_copy:
            raise BookCopyNotFound(f"Book copy with id {id} not found")
        return BookCopyMapper.orm_to_dto(book_copy)

    def find_book_copies_for_status(self, status: BookStatus) -> list[BookCopyDTO]:
        book_copies = self.repo.find_book_copies_for_status(status)
        if not book_copies:
            raise BookCopyNotFound(f"Book copy(ies) with status {status} not found")
        copies = []
        for book_copy in book_copies:
            copies.append(BookCopyMapper.orm_to_dto(book_copy))
        return copies

    def find_book_copies_for_statement(self, statement: BookStatement) -> list[BookCopyDTO]:
        book_copies = self.repo.find_book_copies_for_statement(statement)
        if not book_copies:
            raise BookCopyNotFound(f"Book copy(ies) with statement {statement} not found")
        copies = []
        for book_copy in book_copies:
            copies.append(BookCopyMapper.orm_to_dto(book_copy))
        return copies

    def create_book_copy(self, book_copy: NewBookCopyDTO) -> BookCopyDTO:
        with self.session.begin() as session:
            place = self.repo.find_free_place(1)
            if not place:
                raise StorageSpaceIsNotSufficient(f"Free place in depository for new book copy is`t available ")
            book = self.repo.find_book_by_id(book_copy.book_id, for_update=True)
            if not book:
                raise BookNotFound(f"Book for this book copy not found. Add first the book")
            book_copy.placement = place
            book_copy = self.repo.create_book_copy(BookCopyMapper.new_dto_to_dict(book_copy))
            self.repo.change_place_status(place_id=place.pop(), status=PlacementStatus.OCCUPIED)
            book_copy = self.repo.find_book_by_id(book_copy.id)  #type: ignore
        return BookCopyMapper.orm_to_dto(book_copy)

    def change_book_copy_status(self, id: int, status: BookStatus, customer_id: int | None = None) -> BookCopyDTO:
        if status==BookStatus.BORROWED and not customer_id:
            raise CustomerMustBeGiven(f"When book copi is borrowed, customer id is required")
        book_copy = self.repo.find_book_by_id(id, for_update=True)
        if not book_copy:
            raise BookCopyNotFound(f"Book copy with id {id} not found")
        with self.session.begin() as session:
            if status == BookStatus.AVAILABLE:
                place = self.repo.find_free_place(1)
                if not place:
                    raise StorageSpaceIsNotSufficient(f"Free place in depository for book copy is`t available ")
                self.repo.change_place_status(place_id=place.pop(), status=PlacementStatus.OCCUPIED)
                book_copy = self.repo.update_book_copy(id=id, book_copy={"status": status, "customer": None})
                return BookCopyMapper.orm_to_dto(book_copy)
            elif status == BookStatus.BORROWED:
                customer = self.repo.find_customer_by_id(customer_id)
                if not customer:
                    raise CustomerNotFound(f"Customer with id {customer_id} not found")
                book_copy = self.repo.update_book_copy(id=id, book_copy={"status": status, "customer": customer_id})
                return BookCopyMapper.orm_to_dto(book_copy)
            else:
                book_copy = self.repo.update_book_copy(id=id, book_copy={"status": status, "customer": None})
        return BookCopyMapper.orm_to_dto(book_copy)

    def change_book_copy_statement(self, id: int, statement: BookStatement) -> BookCopyDTO:
        with self.session.begin() as session:
            book_copy = self.repo.find_book_by_id(id, for_update=True)
            if not book_copy:
                raise BookCopyNotFound(f"Book copy with id {id} not found")
            current_statement = book_copy.statement
            if (current_statement == BookStatement.NEW) \
                or (current_statement == BookStatement.GOOD and statement != BookStatement.NEW) \
                or ((current_statement == BookStatement.DAMAGED or current_statement == BookStatement.UNUSABLE) \
                     and statement == BookStatement.REPAIR) \
                or (current_statement == BookStatement.DAMAGED and statement == BookStatement.UNUSABLE):
                new_book_copy = self.repo.update_book_copy(id=id, book_copy={"statement": statement})
                return BookCopyMapper.orm_to_dto(new_book_copy)
            else :
                raise WrongNewStatement(f"Book copy with id {id} with current statement {current_statement} do not "
                                        f"might be changed for new statement: {statement}")

    def delete_book_copy(self, id: int) -> BookCopyDTO:
        with self.session.begin() as session:
            delete_book_copy = self.repo.find_book_by_id(id, for_update=True)
            if not delete_book_copy:
                raise BookCopyNotFound(f"Book copy with id {id} not found")
            if delete_book_copy.satus == BookStatus.BORROWED:
                raise BookCopyBorrowed(f"You cannot delete book copy when it is borrowed. First change status")
            deleted_book_copy = self.repo.delete_book_copy(id)
        return BookCopyMapper.orm_to_dto(deleted_book_copy)

    #Customer
    def find_customer_by_id(self, id: int) -> CustomerDTO:
        customer = self.repo.find_customer_by_id(id)
        if not customer:
            raise CustomerNotFound(f"Customer with id {id} not found")
        return CustomerMapper.orm_to_dto(customer)

    def find_customer_by_email(self, email: str) -> CustomerDTO:
        customer = self.repo.find_customer_by_email(email)
        if not customer:
            raise CustomerNotFound(f"Customer with email {email} not found")
        return CustomerMapper.orm_to_dto(customer)

    def find_customer_by_phone(self, phone: str) -> CustomerDTO:
        phone = PhoneMapper.phone_number_to_united_style(phone)
        customer = self.repo.find_customer_by_phone(phone)
        if not customer:
            raise CustomerNotFound(f"Customer with phone {phone} not found")
        return CustomerMapper.orm_to_dto(customer)

    def find_customer_by_fullname(self, fullname: FullNameDTO) -> CustomerDTO:
        fullname = FullNameMapper.dto_to_dict(fullname)
        customer = self.repo.find_customer_by_fullname(fullname)
        if not customer:
            raise CustomerNotFound(f"Customer with full name {fullname} not found")
        return CustomerMapper.orm_to_dto(customer)

    def create_customer(self, customer: NewCustomerDTO) -> CustomerDTO:
        if not EmailValidator.validate_email(str(customer.email)):
            raise EmailValidationError(f"Invalid email: {customer.email}")
        if not PhoneValidator.validate_phone_number(customer.phone):
            raise PhoneValidationError(f"Invalid phone: {customer.phone}")
        try:
            customer = self.repo.create_customer(CustomerMapper.new_dto_to_dict(customer=customer))
            return CustomerMapper.orm_to_dto(customer)
        except IntegrityError as e:
            original_error = e.orig
            if isinstance(original_error, UniqueViolation):
                constraint_name = original_error.diag.constraint_name
                if constraint_name == 'uq_email':
                    raise CustomerEmailAlreadyExist(f"Customer with email: {customer.email} is already exist "
                                                    f"in database") from e
                elif constraint_name == 'uq_phone':
                    raise CustomerPhoneAlreadyExist(f"Customer with phone: {customer.phone} is already exist "
                                                    f"in database") from e
                elif constraint_name == 'uq_customer_full_name':
                    raise CustomerFullNameAlreadyExist(f"Customer with fullname {str(customer.full_name)} is "
                                                       f"already exist in database") from e
                else: raise e
            else: raise e

    def change_customer_phone_number(self, customer_id: int, phone: StringDTO):
        phone = phone.string
        if not PhoneValidator.validate_phone_number(phone):
            raise PhoneValidationError(f"Invalid phone number format: {phone}")
        phone = PhoneMapper.phone_number_to_united_style(phone)
        try:
            with self.session.begin() as session:
                customer = self.repo.update_customer(customer_id=customer_id, new_customer={"phone": phone})
                customer = self.repo.find_customer_by_id(customer.customer_id)  #type: ignore
            return CustomerMapper.orm_to_dto(customer)
        except IntegrityError as e:
            orig = e.orig
            if isinstance(orig, UniqueViolation) and orig.diag.constraint_name == 'uq_phone':
                raise CustomerPhoneAlreadyExist(f"Customer with phone: {customer.phone} is already exist in "
                                                f"database") from e
            else: raise e

    def change_customer_email(self, customer_id: int, email: StringDTO) -> CustomerDTO:
        email = email.string
        if not self.repo.find_customer_by_id(customer_id):
            raise CustomerNotFound(f"Customer with id {customer_id} not found")
        try:
            with self.session.begin() as session:
                self.repo.update_customer(customer_id=customer_id, new_customer={"email": email})
                customer = self.repo.find_customer_by_id(customer_id)
            return CustomerMapper.orm_to_dto(customer)
        except IntegrityError as e:
            orig = e.orig
            if isinstance(orig, UniqueViolation) and orig.diag.constraint_name == 'uq_email':
                raise CustomerEmailAlreadyExist(f"Customer with email: {customer.email} is already exist "
                                                f"in database") from e
            else: raise e












