
import uuid
import random
import string


def uid() -> str:
    return str(uuid.uuid4())


def gen_entry_no(prefix: str = 'JE') -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def gen_iban(country: str = 'TR') -> str:
    body = ''.join(random.choice(string.digits) for _ in range(22))
    return f"{country}{''.join(random.choice(string.digits) for _ in range(2))}{body}"
