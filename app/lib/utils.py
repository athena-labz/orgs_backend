import random
import string


def string_generator(size=128, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))