import faker
from ..orm_models import Author, Book, Customer


fake_gen = faker.Faker("uk_UA")
male_patronymic_suffixes = ['ович', 'евич', 'ич', 'ійович', 'йович', 'ов', 'ев', 'ій']
female_patronymic_suffixes = ['івна', 'ївна', 'ична', 'ївна', 'ївна', 'ова', 'ева', 'ія']


def generate_fake_authors(quantity: int) -> list[Author]:
    fake_authors: list[Author] = []
    for _ in range(quantity):
        sex = fake_gen.random_element(elements=('M', 'F'))
        if sex == 'M':
            last_name = fake_gen.last_name_male()
            first_name = fake_gen.first_name_male()
            middle_name = fake_gen.first_name_male() + fake_gen.random_element(
                male_patronymic_suffixes) if fake_gen.boolean(chance_of_getting_true=70) else None
        else:
            last_name = fake_gen.last_name_female()
            first_name = fake_gen.first_name_female()
            middle_name = fake_gen.first_name_male() + fake_gen.random_element(
                female_patronymic_suffixes) if fake_gen.boolean(chance_of_getting_true=70) else None
        author = Author(first_name=first_name, last_name=last_name, middle_name=middle_name)
        fake_authors.append(author)
    return fake_authors


def generate_fake_books(quantity: int) -> list[Book]:
    faker_books: list[Book] = []
    for _ in range(quantity):
        title = fake_gen.sentence(nb_words=4).rstrip('.')
        publisher = fake_gen.company()
        place_of_publication = fake_gen.city()
        published_year = fake_gen.year()
        isbn = fake_gen.isbn13(separator="-")
        pages = fake_gen.random_int(min=50, max=1000)
        price = round(fake_gen.pyfloat(left_digits=3, right_digits=2, positive=True, min_value=5.0, max_value=200.0),
                      2) if fake_gen.boolean(chance_of_getting_true=80) else None
        language = fake_gen.language_code() if fake_gen.boolean(chance_of_getting_true=70) else None
        faker_books.append(Book(title=title, publisher=publisher, place_of_publication=place_of_publication,
                                published_year=int(published_year), isbn=isbn, pages=pages, price=price,
                                language=language))
    return faker_books


def generate_fake_customers(quantity: int) -> list[Customer]:
    fake_customers: list[Customer] = []
    for _ in range(quantity):
        sex = fake_gen.random_element(elements=('M', 'F'))
        if sex == 'M':
            last_name = fake_gen.last_name_male()
            first_name = fake_gen.first_name_male()
            middle_name = fake_gen.first_name_male() + fake_gen.random_element(
                male_patronymic_suffixes) if fake_gen.boolean(chance_of_getting_true=70) else None
        else:
            last_name = fake_gen.last_name_female()
            first_name = fake_gen.first_name_female()
            middle_name = fake_gen.first_name_female() + fake_gen.random_element(
                female_patronymic_suffixes) if fake_gen.boolean(chance_of_getting_true=70) else None
        email = fake_gen.unique.email()
        phone = fake_gen.unique.phone_number()
        fake_customers.append(Customer(first_name=first_name, last_name=last_name, middle_name=middle_name,
                                       email=email, phone=phone))
    return fake_customers


