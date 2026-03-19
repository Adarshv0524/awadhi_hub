import bcrypt

def hash_password(plain_text):
    if plain_text is None:
        raise ValueError("Password cannot be None")
    pw = plain_text.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw,salt)
    return hashed.decode('utf-8')


def verify_password(plain_text, hashed):
    if plain_text is None or hashed is None:
        return False
    return bcrypt.checkpw(plain_text.encode('utf-8'), hashed.encode('utf-8'))

