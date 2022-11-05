import string, random

def generate_code(digits=6):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=digits))
    return key


def generate_digits_code(length=6):
    key = ''.join(random.choices(string.digits, k=length))
    return key