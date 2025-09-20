import yaml
from pathlib import Path
from ..repositories.orm_models import Author, Book, Customer, BookCopy
from ..services.dto_models import *
from ..logger import app_logger


def class_constructor(loader, node):
    app_logger.debug(f"Calling constructor for class {loader.construct_scalar(node)}")
    class_name = loader.construct_scalar(node)
    try:
        return globals()[class_name]
    except KeyError:
        app_logger.error(f"Error parsing yaml file, !class '{class_name}' that declarated in yaml configuration "
                         f"file not found in scope.")
        raise yaml.constructor.ConstructorError(f"Class '{class_name}' not found.")

yaml.SafeLoader.add_constructor('!class', class_constructor)

try:
    mapper_config_file = Path(__file__).resolve().parent/'mapper_config.yaml'
    app_logger.debug(f"Loading mapper config from {mapper_config_file}")
    with open(mapper_config_file, "r", encoding="utf-8") as f:
        app_logger.debug("Start mapper config download...")
        configuration = yaml.safe_load(f)
        app_logger.debug(f"Mapper config loaded. Configuration: {configuration}")
except FileNotFoundError:
    app_logger.error("File mapper_config.yaml not found")
except yaml.YAMLError:
    app_logger.error("File mapper_config.yaml is not correct")
except Exception:
    app_logger.error("Mapper configuration loading error")

class CustomORMMapper:

    customer_config = configuration["CUSTOMER"]

    @staticmethod
    def map_recursively(orm_instance, config: dict, max_depth: int = 5, _current_depth: int = 0):
        if orm_instance is None or _current_depth >= max_depth:
            return None

        if isinstance(orm_instance, list):
            return [CustomORMMapper.map_recursively(item, config, max_depth, _current_depth) for item in orm_instance]

        if not hasattr(orm_instance, '_sa_instance_state'):
            return orm_instance

        dto_class = config['dto']
        dto_data = {}
        exclude_fields = config.get('exclude', set())

        for field_name, field_info in dto_class.model_fields.items():
            if field_name in exclude_fields:
                continue

            orm_attr_name = field_name

            if 'nested_transform' in config and field_name in config['nested_transform']:
                transform_config = config['nested_transform'][field_name]
                nested_dto_class = transform_config['dto']
                nested_data = {
                    orm_field: getattr(orm_instance, orm_field)
                    for orm_field in transform_config['orm_fields']
                }
                dto_data[field_name] = nested_dto_class(**nested_data)
                continue

            if 'relationships' in config and orm_attr_name in config['relationships']:
                nested_config = config['relationships'][orm_attr_name]
                nested_orm_instance = getattr(orm_instance, orm_attr_name)

                dto_data[field_name] = CustomORMMapper.map_recursively(
                    nested_orm_instance, nested_config, max_depth, _current_depth + 1
                )
                continue

            if hasattr(orm_instance, orm_attr_name):
                dto_data[field_name] = getattr(orm_instance, orm_attr_name)

        return dto_class(**dto_data)


class AuthorMapper(CustomORMMapper):

    author_config = configuration['AUTHOR']

    @staticmethod
    def dto_to_dict(author: AuthorDTO) -> dict:
        app_logger.debug(f"Call AuthorMapper class method dto_to_dict with parameters: {author}")
        author_columns = Author.__table__.columns.keys()
        author_dict = author.model_dump()
        full_name = author_dict.pop('full_name',{})
        author_dict.update(full_name)
        return {k: v for k, v in author_dict.items()
                if k in author_columns}

    @staticmethod
    def new_dto_to_dict(author: NewAuthorDTO) -> dict:
        app_logger.debug(f"Call AuthorMapper class method new_dto_to_dict with parameters: {author}")
        author_columns = Author.__table__.columns.keys()
        author_dict = author.model_dump()
        full_name = author_dict.pop('full_name',{})
        author_dict.update(full_name)
        return {k: v for k, v in author.model_dump(exclude_unset=True).items()
                if k in author_columns}

    @staticmethod
    def orm_to_dto(author: Author) -> AuthorDTO:
        app_logger.debug(f"Call AuthorMapper class method orm_to_dto with parameters: {author}")
        return AuthorMapper.map_recursively(orm_instance=author, config=AuthorMapper.author_config)


class BookMapper(CustomORMMapper):

    book_config = configuration['BOOK']


    @staticmethod
    def dto_to_dict(book: BookDTO) -> dict:
        app_logger.debug(f"Call BookMapper class method dto_to_dict with parameters: {book}")
        book_columns = Book.__table__.columns.keys()
        return {k: v for k, v in book.model_dump(exclude_unset=True).items()
                if k in book_columns}

    @staticmethod
    def new_dto_to_dict(book: NewBookDTO) -> dict:
        app_logger.debug(f"Call BookMapper class method new_dto_dict with parameters: {book}")
        book_columns = Book.__table__.columns.keys()
        return {k: v for k, v in book.model_dump(exclude_unset=True).items()
                if k in book_columns}

    @staticmethod
    def orm_to_dto(book: Book) -> BookDTO:
        app_logger.debug(f"Call BookMapper class method orm_to_dto with parameters: {book}")
        return BookMapper.map_recursively(orm_instance=book, config=BookMapper.book_config)


class BookCopyMapper(CustomORMMapper):

    book_copy_config = configuration['BOOK_COPY']

    @staticmethod
    def dto_to_dict(book: BookCopyDTO) -> dict:
        app_logger.debug(f"Call BookCopyMapper class method dto_to_dict with parameters: {book}")
        book_columns = Book.__table__.columns.keys()
        return {k: v for k, v in book.model_dump(exclude_unset=True).items()
                if k in book_columns}

    @staticmethod
    def new_dto_to_dict(book: NewBookCopyDTO) -> dict:
        app_logger.debug(f"Call BookCopyMapper class method new_dto_to_dict with parameters: {book}")
        book_columns = Book.__table__.columns.keys()
        return {k: v for k, v in book.model_dump(exclude_unset=True).items()
                if k in book_columns}

    @staticmethod
    def orm_to_dto(book: BookCopy) -> BookCopyDTO:
        app_logger.debug(f"Call BookCopyMapper class method orm_to_dto with parameters: {book}")
        return BookCopyMapper.map_recursively(orm_instance=book, config=BookCopyMapper.book_copy_config)

class CustomerMapper(CustomORMMapper):

    customer_config = configuration['CUSTOMER']

    @staticmethod
    def dto_to_dict(customer:CustomerDTO) -> dict:
        app_logger.debug(f"Call CustomerMapper class method dto_to_dict with parameters: {customer}")
        customer_columns = Customer.__table__.columns.keys()
        customer_dict = customer.model_dump(exclude_unset=True)
        full_name = customer_dict.pop('full_name',{})
        customer_dict.update(full_name)
        return {k: v for k, v in customer_dict.items()
                if k in customer_columns}

    @staticmethod
    def new_dto_to_dict(customer:NewCustomerDTO) -> dict:
        app_logger.debug(f"Call CustomerMapper class method new_dto_to_dict with parameters: {customer}")
        customer_columns = Customer.__table__.columns.keys()
        customer_dict = customer.model_dump(exclude_unset=True)
        full_name = customer_dict.pop('full_name',{})
        customer_dict.update(full_name)
        return {k: v for k, v in customer_dict.items()
                if k in customer_columns}

    @staticmethod
    def orm_to_dto(customer:Customer) -> CustomerDTO:
        app_logger.debug(f"Call CustomerMapper class method orm_to_dto with parameters: {customer}")
        return CustomerMapper.map_recursively(orm_instance=customer, config=CustomerMapper.customer_config)

class FullNameMapper:

    @staticmethod
    def dto_to_dict(full_name: FullNameDTO) -> dict:
        app_logger.debug(f"Call FullNameMapper class method dto_to_dict with parameters: {full_name}")
        full_name_dict = full_name.model_dump(exclude_unset=True)
        return full_name_dict

class PhoneMapper:

    @staticmethod
    def phone_number_to_united_style(phone: str) -> str:
        """Mapped phone number to format: +380 44 123 45 67"""
        app_logger.debug(f"Call PhoneMapper class method phone_number_to_united_style with parameters: {phone}")
        MISSED_COUNTRY_CODE = '38'
        SPACES = [2, 4, 7, 9]
        phone_number = "".join( ch for ch in phone if ch.isdigit())
        if phone_number[0] == '0':
            phone_number = MISSED_COUNTRY_CODE + phone_number
        return "+" + "".join((ch + " ") if i in SPACES else ch for i, ch in enumerate(phone_number))