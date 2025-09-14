import os
import random
import string
from sqlalchemy import select
from .orm_models import *
from ..enums.enums import BookStatus, BookStatement, PlacementStatus
from ..services.dto_models import NewDepositoryDTO
from ..db import reset_db, get_session
from data_generator.data_generator import *

def init_db(depo: NewDepositoryDTO) -> None:

    reset_db()
    session = get_session()

    # Insert fake data in DB
    with (session):
        # Create placement
        line_ids = list(string.ascii_uppercase[:depo.lines])
        shelf_ids = list(string.ascii_uppercase[:depo.shelves])
        for line in line_ids:
            for column in range(1, depo.columns + 1): #type: ignore
                for shelf in shelf_ids:
                    for position in range(1, depo.positions + 1): # type: ignore
                        placement = Placement(
                            line_id=line,
                            column_id=column,
                            shelf_id=shelf,
                            position=position
                        )
                        session.add(placement)

        # Create authors
        authors = generate_fake_authors(depo.authors_number)
        for author in authors:
            session.add(author)

        # Create books
        books = generate_fake_books(200)
        for book in books:
            session.add(book)

        # Create customers
        customers = generate_fake_customers(100)
        for customer in customers:
            session.add(customer)

        # Create book-author relations
        author_ids = session.scalar(select(Author.id)).all()
        book_ids = session.scalar(select(Book.id)).all()
        for book_id in book_ids:
            num_of_authors = random.randint(0, 3)
            if not num_of_authors:
                break
            selected_authors = random.sample(author_ids, num_of_authors)
            for author_id in selected_authors:
                session.add(BookAuthor(
                    book_id=book_id[0],
                    author_id=author_id[0]
                ))

        # Create book copies
        book_ids = session.scalar(select(Book.id)).all()
        placements = session.scalar(select(Placement.id).where(Placement.status == PlacementStatus.FREE)).all()
        customers = session.scalar(select(Customer.customer_id)).all
        for book_id in book_ids:
            num_of_copies = random.randint(1, depo.max_books_copies_per_book)
            for copy in range(num_of_copies): #type: ignore
                status = random.choices([BookStatus.AVAILABLE, BookStatus.LANDED,
                                         BookStatus.LOST], weights=(70, 25, 5))[0]
                statement = random.choices([BookStatement.NEW, BookStatement.GOOD,
                                            BookStatement.REPAIR, BookStatement.DAMAGED],
                                            weights=(20, 50, 20, 10))[0]
                if status == BookStatus.AVAILABLE:
                    session.add(BookCopy(
                        book_id=book_id[0],
                        status=status,
                        statement=statement,
                        placement=placements.pop(random.randint(0, len(placements) - 1))[0]
                    ))
                elif status == BookStatus.LANDED:
                    session.add(BookCopy(
                        book_id=book_id[0],
                        status=status,
                        statement=statement,
                        customer_id=random.choice(customers)[0]
                    ))
                else:
                    session.add(BookCopy(
                        book_id=book_id[0],
                        status=status,
                        statement=statement
                    ))
        session.commit()