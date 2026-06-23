import secrets
import string

class PasswordGenerator:
    def __init__(self):
        self.min_lowercase = 1
        self.min_uppercase = 1
        self.length = 30
        self.min_digits = 1
        self.special_chars = ["@", "/", " ", "$", "%", "^"]
        self.min_special_chars = 1
        self.password = []

    def get_minimum(self, population: list[any], k: int):
        return secrets.SystemRandom().choices(population, k=k)
    
    def get_password(self):
        all_min = []

        all_min += self.get_minimum(string.ascii_lowercase, self.min_lowercase) + \
            self.get_minimum(string.ascii_uppercase, self.min_uppercase) + \
            self.get_minimum(string.digits, self.min_digits) + \
            self.get_minimum(self.special_chars, self.min_special_chars)
        
        length_to_fill = self.length - len(all_min)

        final_pass = all_min + secrets.SystemRandom().choices(
            list(string.ascii_letters + string.digits) + self.special_chars, 
            k = length_to_fill
        )

        secrets.SystemRandom().shuffle(final_pass)

        return ''.join(final_pass)
