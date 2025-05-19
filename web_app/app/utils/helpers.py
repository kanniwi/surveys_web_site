import re

def password_strength(password):
    if re.match(r'^(?=.*\d)(?=.*[A-ZА-ЯЁ])(?=.*[a-zа-яё])[^ ]{8,128}$', password):
        return True
    return False