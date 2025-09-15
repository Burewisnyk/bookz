from __future__ import annotations
from sqlalchemy import TIMESTAMP, Integer, SmallInteger, Float, String, ForeignKey, UniqueConstraint, Index, Enum as PgEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from ..enums.enums import BookStatus, BookStatement, PlacementStatus
from ..db import Base


class TimestampMixin:
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(),
                                                   onupdate=func.current_timestamp())


class Author(Base, TimestampMixin):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(40), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(40))

    books: Mapped[list[Book]] = relationship("Book", secondary="book_author", back_populates="authors")

    __table_args__ = (UniqueConstraint('first_name', 'last_name', 'middle_name', name='uq_author_full_name'),
                      Index('ix_author_full_name', 'last_name', 'first_name', 'middle_name'))

    def __repr__(self) -> str:
        return (f"Author(id={self.id}, first_name='{self.first_name}', "
                f"last_name='{self.last_name}', middle_name='{self.middle_name}')")


class Book(Base, TimestampMixin):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    publisher: Mapped[str] = mapped_column(String(80), nullable=False)
    place_of_publication: Mapped[str] = mapped_column(String(80), nullable=False)
    published_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float | None] = mapped_column(Float)
    language: Mapped[str | None] = mapped_column(String(3))

    authors: Mapped[list[Author]] = relationship("Author", secondary='book_author', back_populates='books')
    copies: Mapped[list[BookCopy]] = relationship("BookCopy", back_populates='book')

    __table_args__ = (Index('ix_title', 'title'),)

    def __repr__(self) -> str:
        return (f"Book(id={self.id}, title='{self.title}', publisher='{self.publisher}', "
                f"place_of_publication='{self.place_of_publication}', published_year={self.published_year}, "
                f"isbn='{self.isbn}', pages={self.pages}, price={self.price}, language='{self.language}')")


class BookAuthor(Base):
    __tablename__ = 'book_author'

    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), primary_key=True)

    def __repr__(self) -> str:
        return f"BookAuthor(book_id={self.book_id}, author_id={self.author_id})"


class BookCopy(Base, TimestampMixin):
    __tablename__ = 'book_copies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    status: Mapped[BookStatus] = mapped_column(PgEnum(BookStatus, name="book_copy_status"), nullable=False,
                                               default=BookStatus.AVAILABLE)
    placement_id : Mapped[int | None] = mapped_column(ForeignKey('placements.id'), default=None)
    statement: Mapped[BookStatement] = mapped_column(PgEnum(BookStatement), nullable=False, default=BookStatement.NEW)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey('customers.customer_id'), default=None)

    book: Mapped[Book] = relationship("Book", back_populates='copies')
    customer: Mapped[Customer] = relationship("Customer", back_populates='borrowed_books')
    placement: Mapped[Placement] = relationship("Placement", back_populates='book_copy')

    def __repr__(self) -> str:
        return (f"BookCopy(id={self.id}, book={self.book}, status='{self.status.value}', "
                f"placement='{self.placement}', statement='{self.statement.value}')")


class Customer(Base, TimestampMixin):
    __tablename__ = 'customers'

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_name: Mapped[str] = mapped_column(String(40), nullable=False)
    first_name: Mapped[str] = mapped_column(String(40), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    borrowed_books: Mapped[list[BookCopy]] = relationship("BookCopy", back_populates="customer")

    __table_args__ = (Index('ix_customer_full_name', 'last_name', 'first_name', 'middle_name'),
                      UniqueConstraint('last_name', 'first_name', 'middle_name', name='uq_customer_full_name'),
                      Index('ix_customer_email', 'email'),
                      Index('ix_customer_phone', 'phone'))

    def __repr__(self) -> str:
        return (f"Customer(customer_id={self.customer_id}, last_name='{self.last_name}', "
                f"first_name='{self.first_name}', middle_name='{self.middle_name}', "
                f"email='{self.email}', phone='{self.phone}')")


class Placement(Base, TimestampMixin):
    __tablename__ = 'placements'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    line_id: Mapped[str] = mapped_column(String(1), nullable=False)
    column_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    shelf_id: Mapped[str] = mapped_column(String(1), nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[PlacementStatus] = mapped_column(PgEnum(PlacementStatus, name="placement_status"), nullable=False,
                                                    default=PlacementStatus.FREE)

    book_copy = relationship("BookCopy", back_populates="placement")

    def __repr__(self) -> str:
        return (f"Placement(id={self.id}, line_id='{self.line_id}', column_id={self.column_id}, "
                f"shelf_id='{self.shelf_id}', position={self.position}, "
                f"book_copy={self.book_copy}, status='{self.status.value}')")