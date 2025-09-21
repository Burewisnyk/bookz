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
from ..logger import app_logger


class BookService:

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = BookRepository(session)

    def depository_status(self) -> DepositoryDTO:
        app_logger.info("Calling depository_status function")
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
    def find_author_by_id(self, author_id: int) -> AuthorDTO:
        app_logger.info(f"Calling find_author_by_id function with parameter: {author_id}")
        author = self.repo.find_author_by_id(author_id)
        if not author:
            app_logger.warning(f"Author with id {author_id} not found")
            raise AuthorNotFound(f"Author with id {author_id} not found")
        app_logger.info(f"Author:{author}, books: {author.books}, {author.books[0].copies}")
        return AuthorMapper.orm_to_dto(author)

    def find_author_by_full_name(self, author: FullNameDTO) -> AuthorDTO:
        app_logger.info(f"Calling find_author_by_full_name function with parameter: {author}")
        find_author = self.repo.find_author(author=FullNameMapper.dto_to_dict(author))
        if not author:
            app_logger.warning(f"Author with full name \"{author}\" not found")
            raise AuthorNotFound(f"Author with full name {author} not found")
        return AuthorMapper.orm_to_dto(find_author)

    def create_author(self, author: NewAuthorDTO) -> AuthorDTO:
        app_logger.info(f"Calling create_author function with parameter: {author}")
        try:
            with self.session.begin():
                author = self.repo.create_author(AuthorMapper.new_dto_to_dict(author))
            return AuthorMapper.orm_to_dto(author)
        except IntegrityError as e:
            orig = e.orig
            if isinstance(orig, UniqueViolation) and orig.diag.constraint_name == 'uq_author_full_name':
                app_logger.warning(f"Author with full name {str(author.full_name)} already exists in database")
                raise AuthorFullNameAlreadyExist(f"Author with full name: {str(author.full_name)} is already exist "
                                                f"in database") from e
            else: raise e

    def update_author(self, author: AuthorDTO) -> AuthorDTO:
        app_logger.info(f"Calling update_author function with parameters: {author}")
        try:
            with self.session.begin():
                author_by_id = self.repo.find_author_by_id(author.id)
                if not author_by_id:
                    raise AuthorNotFound(f"Author with id {author.id} not found")
                author = self.repo.update_author(AuthorMapper.dto_to_dict(author))
            return AuthorMapper.orm_to_dto(author)
        except IntegrityError as e:
            orig = e.orig
            if isinstance(orig, UniqueViolation) and orig.diag.constraint_name == 'uq_author_full_name':
                app_logger.warning(f"Author with full name: {str(author.full_name)} already exists in database")
                raise AuthorFullNameAlreadyExist(f"Author with fullname {str(author.full_name)} is "
                                                 f"already exist in database") from e

    def delete_author_by_id(self, author_id: int) -> AuthorDTO:
        app_logger.info(f"Calling delete_author_by_id function with parameter: {author_id}")
        book_author = self.repo.find_books_by_author_id(author_id)
        if book_author:
            app_logger.warning(f"Author with id {author_id} not found")
            raise BookPresentInDatabase(f"{len(book_author)} book(s) is present in repository. Delete author books "
                                        f"before deleting the author")
        author = self.repo.delete_author_by_id(author_id)
        if not author:
            app_logger.warning(f"Author with id {author_id} not found")
            raise AuthorNotFound(f"Author with id {author_id} not found")
        return AuthorMapper.orm_to_dto(author)

    def delete_authors_without_book(self) -> list[AuthorDTO]:
        app_logger.info(f"Calling delete_authors_without_book function")
        with self.session.begin():
            authors = self.repo.find_authors_without_book(for_update=True)
            if not authors:
                app_logger.info(f"Author without books not found")
                raise AuthorNotFound(f"Author without books not found")
            authors = self.repo.delete_authors_by_ids(authors)
            authorDTOs: list[AuthorDTO] = []
            for author in authors:
                authorDTOs.append(AuthorMapper.orm_to_dto(author))
        return authorDTOs

    # Book functions
    def find_book_by_id(self, book_id: int) -> BookDTO:
        app_logger.info(f"Calling find_book_by_id function with parameter: {book_id}")
        book = self.repo.find_book_by_id(book_id)
        if not book:
            app_logger.warning(f"Book with id {book_id} not found")
            raise BookNotFound(f"Book with id {book_id} not found")
        return BookMapper.orm_to_dto(book)

    def find_book_by_isbn(self, isbn: str) -> BookDTO:
        app_logger.info(f"Calling find_book_by_isbn function with parameter: {isbn}")
        book = self.repo.find_book_by_isbn(isbn)
        if not book:
            app_logger.warning(f"Book with isbn {isbn} not found")
            raise BookNotFound(f"Book with isbn {isbn} not found")
        return BookMapper.orm_to_dto(book)

    def create_book(self, book: NewBookDTO) -> BookDTO:
        app_logger.info(f"Calling create_book function with parameter: {book}")
        present_book = self.find_book_by_isbn(book.isbn)
        if present_book:
            app_logger.warning(f"Book not created. Book with isbn {book.isbn} present in database")
            raise BookPresentInDatabase(f"Book with isbn {book.isbn} present in database")
        try:
            with self.session.begin():
                new_book = self.repo.create_book(BookMapper.new_dto_to_dict(book))
                for author in book.authors:
                    ath = self.repo.find_author(AuthorMapper.new_dto_to_dict(author))
                    if not ath:
                        ath = self.repo.create_author(AuthorMapper.new_dto_to_dict(author))
                    self.repo.create_author_book_rel(book_id=new_book.book_id, author_id=ath.id)  #type: ignore
                available_places = self.repo.find_free_place(book.new_copies)
                places = available_places.copy()
                if len(available_places) < book.new_copies:
                    raise StorageSpaceIsNotSufficient(f"Free place for {book.new_copies} of {book.title} is`t available ")
                new_book_copies: list[dict] = []
                for _ in book.copies:
                    place = available_places.pop()
                    new_book_copies.append(BookCopyMapper.new_dto_to_dict(
                        NewBookCopyDTO(
                            book_id=book.id,
                            status=BookStatus.AVAILABLE,
                            statement=book.copy_statement,
                            placement_id=place)))
                self.repo.create_book_copies(new_book_copies)
                self.repo.change_places_status(place_ids=places, status=PlacementStatus.OCCUPIED)
        except IntegrityError as e:
            orig = e.orig
            if isinstance(orig, IntegrityError) and orig.diag.constraint_name == 'uq_isbn':
                app_logger.warning(f"Book with isbn {book.isbn} present in database")
                raise BookPresentInDatabase(f"Book with isbn {book.isbn} present in database") from e
        return self.find_book_by_isbn(book.isbn)

    def delete_book(self, book_id: int) -> BookDTO:
        app_logger.info(f"Calling delete_book function with parameter: {book_id}")
        with self.session.begin():
            book = self.repo.find_book_by_id(book_id, for_update=True)
            if not book:
                raise BookNotFound(f"Book with id {book_id} not found")
            place_ids: list[int] = []
            copy_ids: list[int] = []
            borrowed_copies_ids: list[int] = []
            for copy in book.book_copies:
                if copy.status == BookStatus.BORROWED:
                    borrowed_copies_ids.append(copy.id)
                if copy.status == BookStatus.AVAILABLE:
                    place_ids.append(copy.placement_id)
                copy_ids.append(copy.id)
            if borrowed_copies_ids:
                app_logger.warning(f"Attempt to delete book {book.title} with isbn {book.isbn} whose copies "
                                   f"{borrowed_copies_ids} are borrowed")
                raise BookCopyBorrowed(f"Book copies {borrowed_copies_ids}  of book '{book.title}' is borrowed. "
                                       f"Change its status before delete")
            self.repo.delete_book_copies_by_ids(ids=copy_ids)
            self.repo.change_places_status(place_ids = place_ids, status=PlacementStatus.FREE)
            self.repo.delete_book_by_id(book.book_id) #type: ignore
        return book

    def delete_books_without_copies(self) -> list[BookDTO]:
        with self.session.begin():
            books = self.repo.find_book_without_copy(for_update=True)
            if not books:
                raise BookNotFound(f"Books without copy found")
            book_ids: list[int] = []
            for book in books:
                book_ids.append(book.book_id)  #type: ignore
            books = self.repo.delete_books(book_ids=book_ids)
        deleted_books: list[BookDTO] = []
        for book in books:
            deleted_books.append(BookMapper.orm_to_dto(book))
        return deleted_books

    # Book copies functions
    def find_book_copy(self, copy_id: int) -> BookCopyDTO:
        app_logger.info(f"Calling find_book_copy function with parameter: {copy_id}")
        book_copy = self.repo.find_book_copy(copy_id)
        if not book_copy:
            app_logger.warning(f"Book with id {copy_id} not found")
            raise BookCopyNotFound(f"Book copy with id {copy_id} not found")
        return BookCopyMapper.orm_to_dto(book_copy)

    def find_book_copies_for_status(self, status: BookStatus) -> list[BookCopyDTO]:
        app_logger.info(f"Calling find_book_copies_for_status function with parameter: {status}")
        book_copies = self.repo.find_book_copies_for_status(status)
        if not book_copies:
            app_logger.warning(f"Book copies with status: {status} not found")
            raise BookCopyNotFound(f"Book copy(ies) with status {status} not found")
        copies = []
        for book_copy in book_copies:
            copies.append(BookCopyMapper.orm_to_dto(book_copy))
        return copies

    def find_book_copies_for_statement(self, statement: BookStatement) -> list[BookCopyDTO]:
        app_logger.info(f"Calling find_book_copies_for_statement function with parameter: {statement}")
        book_copies = self.repo.find_book_copies_for_statement(statement)
        if not book_copies:
            app_logger.warning(f"Book copies with statement: {statement} not found")
            raise BookCopyNotFound(f"Book copy(ies) with statement {statement} not found")
        copies = []
        for book_copy in book_copies:
            copies.append(BookCopyMapper.orm_to_dto(book_copy))
        return copies

    def create_book_copy(self, book_copy: NewBookCopyDTO) -> BookCopyDTO:
        app_logger.info(f"Calling create_book_copy function with parameter: {book_copy}")
        with self.session.begin():
            place = self.repo.find_free_place(1)
            if not place:
                app_logger.warning("Free place in depository for new book copy not found")
                raise StorageSpaceIsNotSufficient(f"Free place in depository for new book copy is`t available ")
            book = self.repo.find_book_by_id(book_copy.book_id, for_update=True)
            if not book:
                app_logger.warning(f"Book with book_id: {book_copy.book_id} for this book copy not found")
                raise BookNotFound(f"Book for this book copy not found. Add first the book")
            book_copy.placement = place
            book_copy = self.repo.create_book_copy(BookCopyMapper.new_dto_to_dict(book_copy))
            self.repo.change_place_status(place_id=place.pop(), status=PlacementStatus.OCCUPIED)
            book_copy = self.repo.find_book_by_id(book_copy.copy_id)  #type: ignore
        return BookCopyMapper.orm_to_dto(book_copy)

    def change_book_copy_status(self, copy_id: int, status: BookStatus, customer_id: int | None = None) -> BookCopyDTO:
        app_logger.info(f"Calling change_book_copy_status function with parameter: copy_id: {copy_id}, "
                        f"status: {status}, customer_id: {customer_id}")
        if status==BookStatus.BORROWED and not customer_id:
            app_logger.warning(f"Bad function parameters. For status BORROWED customer_id must be not NULL")
            raise CustomerMustBeGiven(f"When book copy is borrowed, customer id is required")
        book_copy = self.repo.find_book_copy(copy_id, for_update=True)
        if not book_copy:
            app_logger.warning(f"Book with copy_id: {copy_id} not found")
            raise BookCopyNotFound(f"Book copy with id {copy_id} not found")
        with self.session.begin():
            if status == BookStatus.AVAILABLE:
                place = self.repo.find_free_place(1)
                if not place:
                    app_logger.warning("Free place in depository for new book copy is`t available ")
                    raise StorageSpaceIsNotSufficient(f"Free place in depository for book copy is`t available ")
                self.repo.change_place_status(place_id=place.pop(), status=PlacementStatus.OCCUPIED)
                book_copy = self.repo.update_book_copy(copy_id=copy_id, book_copy={"status": status, "customer": None})
                return BookCopyMapper.orm_to_dto(book_copy)
            elif status == BookStatus.BORROWED:
                customer = self.repo.find_customer_by_id(customer_id)
                if not customer:
                    app_logger.warning(f"Customer with id {customer_id} not found")
                    raise CustomerNotFound(f"Customer with id {customer_id} not found")
                book_copy = self.repo.update_book_copy(copy_id=copy_id, book_copy={"status": status,
                                                                                   "customer": customer_id})
                return BookCopyMapper.orm_to_dto(book_copy)
            else:
                book_copy = self.repo.update_book_copy(copy_id=copy_id, book_copy={"status": status, "customer": None})
        return BookCopyMapper.orm_to_dto(book_copy)

    def change_book_copy_statement(self, copy_id: int, statement: BookStatement) -> BookCopyDTO:
        app_logger.info(f"Calling change_book_copy_statement function with parameter: copy_id: {copy_id}, "
                        f"statement: {statement}")
        with self.session.begin():
            book_copy = self.repo.find_book_by_id(copy_id, for_update=True)
            if not book_copy:
                app_logger.warning(f"Book with copy_id: {copy_id} not found")
                raise BookCopyNotFound(f"Book copy with id {copy_id} not found")
            current_statement = book_copy.statement
            if (current_statement == BookStatement.NEW) \
                or (current_statement == BookStatement.GOOD and statement != BookStatement.NEW) \
                or ((current_statement == BookStatement.DAMAGED or current_statement == BookStatement.UNUSABLE)
                     and statement == BookStatement.REPAIR) \
                or (current_statement == BookStatement.DAMAGED and statement == BookStatement.UNUSABLE):
                new_book_copy = self.repo.update_book_copy(copy_id=copy_id, book_copy={"statement": statement})
                return BookCopyMapper.orm_to_dto(new_book_copy)
            else :
                app_logger.warning(f"Bad new statement {statement} for current book copy statement {current_statement}")
                raise WrongNewStatement(f"Book copy with id {copy_id} with current statement {current_statement} do "
                                        f"not might be changed for new statement: {statement}")

    def delete_book_copy(self, copy_id: int) -> BookCopyDTO:
        app_logger.info(f"Calling delete_book_copy function with parameter: copy_id: {copy_id}")
        with self.session.begin():
            delete_book_copy = self.repo.find_book_by_id(copy_id, for_update=True)
            if not delete_book_copy:
                app_logger.warning(f"Book with copy_id: {copy_id} not found")
                raise BookCopyNotFound(f"Book copy with id {copy_id} not found")
            if delete_book_copy.satus == BookStatus.BORROWED:
                app_logger.warning(f"Book with copy_id: {copy_id} borrowed. You cannot delete it")
                raise BookCopyBorrowed(f"You cannot delete book copy when it is borrowed. First change status")
            deleted_book_copy = self.repo.delete_book_copy(copy_id)
        return BookCopyMapper.orm_to_dto(deleted_book_copy)

    #Customer
    def find_customer_by_id(self, cust_id: int) -> CustomerDTO:
        app_logger.info(f"Calling find_customer_by_id function with parameter: copy_id: {cust_id}")
        customer = self.repo.find_customer_by_id(cust_id)
        if not customer:
            app_logger.warning(f"Customer with copy_id: {cust_id} not found")
            raise CustomerNotFound(f"Customer with id {cust_id} not found")
        return CustomerMapper.orm_to_dto(customer)

    def find_customer_by_email(self, email: str) -> CustomerDTO:
        app_logger.info(f"Calling find_customer_by_email function with parameter: email: {email}")
        customer = self.repo.find_customer_by_email(email)
        if not customer:
            app_logger.warning(f"Customer with email: {email} not found")
            raise CustomerNotFound(f"Customer with email {email} not found")
        return CustomerMapper.orm_to_dto(customer)

    def find_customer_by_phone(self, phone: str) -> CustomerDTO:
        app_logger.info(f"Calling find_customer_by_phone function with parameter: {phone}")
        phone = PhoneMapper.phone_number_to_united_style(phone)
        customer = self.repo.find_customer_by_phone(phone)
        if not customer:
            app_logger.warning(f"Customer with phone: {phone} not found")
            raise CustomerNotFound(f"Customer with phone {phone} not found")
        return CustomerMapper.orm_to_dto(customer)

    def find_customer_by_fullname(self, fullname: FullNameDTO) -> CustomerDTO:
        app_logger.info(f"Calling find_customer_by_fullname function with parameter: {fullname}")
        fullname = FullNameMapper.dto_to_dict(fullname)
        customer = self.repo.find_customer_by_fullname(fullname)
        if not customer:
            app_logger.warning(f"Customer with fullname: {fullname} not found")
            raise CustomerNotFound(f"Customer with full name {fullname} not found")
        return CustomerMapper.orm_to_dto(customer)

    def create_customer(self, customer: NewCustomerDTO) -> CustomerDTO:
        app_logger.info(f"Calling create_customer function with parameter: {customer}")
        if not EmailValidator.validate_email(str(customer.email)):
            app_logger.warning(f"Invalid email: {customer.email}")
            raise EmailValidationError(f"Invalid email: {customer.email}")
        if not PhoneValidator.validate_phone_number(customer.phone):
            app_logger.warning(f"Invalid phone: {customer.phone}")
            raise PhoneValidationError(f"Invalid phone: {customer.phone}")
        try:
            customer = self.repo.create_customer(CustomerMapper.new_dto_to_dict(customer=customer))
            return CustomerMapper.orm_to_dto(customer)
        except IntegrityError as e:
            original_error = e.orig
            if isinstance(original_error, UniqueViolation):
                constraint_name = original_error.diag.constraint_name
                if constraint_name == 'uq_email':
                    app_logger.warning("Customer with email: {customer.email} already exists")
                    raise CustomerEmailAlreadyExist(f"Customer with email: {customer.email} is already exist "
                                                    f"in database") from e
                elif constraint_name == 'uq_phone':
                    app_logger.warning(f"Customer with phone: {customer.phone} already exists")
                    raise CustomerPhoneAlreadyExist(f"Customer with phone: {customer.phone} is already exist "
                                                    f"in database") from e
                elif constraint_name == 'uq_customer_full_name':
                    app_logger.warning(f"Customer with full name: {customer.fullname} already exists")
                    raise CustomerFullNameAlreadyExist(f"Customer with fullname {str(customer.full_name)} is "
                                                       f"already exist in database") from e
                else: raise e
            else: raise e

    def change_customer_phone_number(self, customer_id: int, phone: StringDTO):
        app_logger.info(f"Calling change_customer_phone_number function with parameter: {phone}")
        phone = phone.string
        if not PhoneValidator.validate_phone_number(phone):
            app_logger.warning(f"Invalid phone: {phone}")
            raise PhoneValidationError(f"Invalid phone number format: {phone}")
        phone = PhoneMapper.phone_number_to_united_style(phone)
        try:
            with self.session.begin():
                customer = self.repo.update_customer(customer_id=customer_id, new_customer={"phone": phone})
                customer = self.repo.find_customer_by_id(customer.customer_id)  #type: ignore
            return CustomerMapper.orm_to_dto(customer)
        except IntegrityError as e:
            orig = e.orig
            if isinstance(orig, UniqueViolation) and orig.diag.constraint_name == 'uq_phone':
                app_logger.warning(f"Customer with phone: {phone} already exists")
                raise CustomerPhoneAlreadyExist(f"Customer with phone: {customer.phone} is already exist in "
                                                f"database") from e
            else: raise e

    def change_customer_email(self, customer_id: int, email: StringDTO) -> CustomerDTO:
        app_logger.info(f"Calling change_customer_email function with parameter: {email}")
        email = email.string
        try:
            with self.session.begin():
                if not self.repo.find_customer_by_id(customer_id, for_update=True):
                    app_logger.warning(f"Customer with id: {customer_id} not found")
                    raise CustomerNotFound(f"Customer with id {customer_id} not found")
                self.repo.update_customer(customer_id=customer_id, new_customer={"email": email})
                customer = self.repo.find_customer_by_id(customer_id)
            return CustomerMapper.orm_to_dto(customer)
        except IntegrityError as e:
            orig = e.orig
            if isinstance(orig, UniqueViolation) and orig.diag.constraint_name == 'uq_email':
                app_logger.warning(f"Customer with email: {email} already exists in database")
                raise CustomerEmailAlreadyExist(f"Customer with email: {customer.email} is already exist "
                                                f"in database") from e
            else: raise e












