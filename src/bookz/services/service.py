
from sqlalchemy.orm import Session

from .dto_models import *
from ..repositories.repository import BookRepository
from ..mappers.mappers import *

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

    def find_author_by_id(self, author_id: int) -> AuthorDTO | None:
        author = self.repo.find_author_by_id(author_id)
        if not author:
            return None
        return AuthorMapper.orm_to_dto(author)

    def find_author_by_full_name(self, author: FullNameDTO) -> AuthorDTO | None:
        author = self.repo.find_author(author=FullNameMapper.dto_to_dict(author))
        if not author:
            return None
        return AuthorDTO.model_validate(author)

    def create_author(self, author: NewAuthorDTO) -> AuthorDTO:
        author = AuthorMapper.new_dto_to_dict(author)
        author = self.repo.create_author(AuthorMapper.dto_to_dict(author))
        return AuthorDTO.model_validate(author)


