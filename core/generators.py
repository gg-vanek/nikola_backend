import random
import string


def slug_generator(slug_length=12):
    def generator():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(slug_length))

    return generator
