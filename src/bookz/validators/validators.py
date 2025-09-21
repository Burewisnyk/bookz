import re


class PhoneValidator:
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        pattern = r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{1,6}$'
        return bool(re.match(pattern, phone))

class EmailValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))