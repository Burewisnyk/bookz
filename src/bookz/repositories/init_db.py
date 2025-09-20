import random
import string
from pathlib import Path
import yaml
from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.exc import InterfaceError, DatabaseError
from ..enums.enums import BookStatus, BookStatement, PlacementStatus
from ..services.dto_models import NewDepositoryDTO
from ..db import reset_db, get_session, is_database_exists, start_db
from .data_generator.data_generator import generate_fake_customers, generate_fake_books, generate_fake_authors
from .orm_models import BookAuthor, Placement, Author, Book, Customer, BookCopy
from ..logger import app_logger,db_logger

def init_db_from_config():
    #Read data from init config file
    if is_database_exists():
        app_logger.info(f"Database already exists, skipping.")
        return
    else:
        app_logger.info(f"Database doesn't exist, creating it.")
        start_db()
    path_for_config_file = Path(__file__).resolve().parent.parent.parent.parent/"config"/"init_db_config.yaml"
    app_logger.info("Start reading config file...")
    depo = None
    try:
        with open(path_for_config_file,"r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        depo = NewDepositoryDTO(**config['NewDepository'])
    except FileNotFoundError:
        app_logger.error("File init_db_config.yaml not found.")
    except yaml.YAMLError:
        app_logger.error("File init_db_config.yaml is not correct.")
    except ValidationError:
        app_logger.error("Error validating config file.")
    app_logger.info(f"Config file read. Config: {str(depo)}")
    init_db(depo)

def init_db(depo: NewDepositoryDTO) -> None:

    app_logger.info("Reset database...")
    db_logger.warning("Reset database...")
    reset_db()
    app_logger.info("Reset database complete.")
    db_logger.warning("Reset database complete.")

    # Insert fake data in DB
    try:
        with (get_session() as session):
            app_logger.info("Start creation fake dates for database...")
            # Create placement
            line_ids = list(string.ascii_uppercase[:depo.lines])
            shelf_ids = list(string.ascii_uppercase[:depo.shelves])
            for line in line_ids:
                for column in range(1, depo.columns + 1): #type: ignore
                    for shelf in shelf_ids:
                        for position in range(1, depo.positions + 1): # type: ignore
                            placement = Placement(line_id=line, column_id=column, shelf_id=shelf, position=position)
                            session.add(placement)

            # Create authors
            app_logger.info(f"Start generation {depo.authors_number} fake authors...")
            authors = generate_fake_authors(depo.authors_number)
            for author in authors:
                session.add(author)

            # Create books
            app_logger.info(f"Start generation {depo.books_number} fake books...")
            books = generate_fake_books(depo.books_number)
            for book in books:
                session.add(book)

            # Create customers
            customers = generate_fake_customers(depo.customers_number)
            for customer in customers:
                session.add(customer)

            session.flush()

            # Create book-author relations
            author_ids = session.scalars(select(Author.id)).all()
            book_ids = session.scalars(select(Book.book_id)).all()
            for book_id in book_ids:
                num_of_authors = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
                if not num_of_authors:
                    continue
                selected_authors = random.sample(author_ids, num_of_authors)
                for author_id in selected_authors:
                    session.add(BookAuthor(
                        book_id=book_id,
                        author_id=author_id
                    ))

            # Create book copies
            book_ids = session.scalars(select(Book.book_id)).all()
            placements = session.scalars(select(Placement.id).where(Placement.status == PlacementStatus.FREE)).all()
            customers = session.scalars(select(Customer.customer_id)).all()
            for book_id in book_ids:
                num_of_copies = random.randint(1, depo.max_books_copies_per_book)
                for copy in range(num_of_copies): #type: ignore
                    status = random.choices([BookStatus.AVAILABLE, BookStatus.BORROWED,
                                             BookStatus.LOST], weights=(70, 25, 5))[0]
                    statement = random.choices([BookStatement.NEW, BookStatement.GOOD,
                                                BookStatement.REPAIR, BookStatement.DAMAGED],
                                                weights=(20, 50, 20, 10))[0]
                    if status == BookStatus.AVAILABLE:
                        placement = placements.pop(random.randint(0, len(placements) - 1))
                        session.add(BookCopy(
                            book_id=book_id,
                            status=status,
                            statement=statement,
                            placement_id=placement
                        ))
                        stmt = (
                            update(Placement)
                            .values(status=PlacementStatus.OCCUPIED)
                            .where(Placement.id == placement)
                        )
                        session.execute(stmt)
                    elif status == BookStatus.BORROWED:
                        session.add(BookCopy(
                            book_id=book_id,
                            status=status,
                            statement=statement,
                            customer_id=random.choice(customers)
                        ))
                    else:
                        session.add(BookCopy(
                            book_id=book_id,
                            status=status,
                            statement=statement
                        ))
            session.commit()
    except InterfaceError as e:
        app_logger.error(f"InterfaceError for database initialization. Error type {e.__class__.__name__}. "
                        f"Error message: {str(e)}")
        db_logger.error(f"InterfaceError for database initialization. Error type {e.__class__.__name__}. "
                        f"Error message: {str(e)}")
    except DatabaseError as e:
        app_logger.error(f"DatabaseError for database initialization. Error type {e.__class__.__name__}. "
                         f"Error message: {str(e)}")
        db_logger.error(f"DatabaseError for database initialization. Error type {e.__class__.__name__}. "
                        f"Error message: {str(e)}")
    except Exception as e:
        app_logger.critical(f"Unexpected error. Error type {e.__class__.__name__}. Error message: {str(e)}")
