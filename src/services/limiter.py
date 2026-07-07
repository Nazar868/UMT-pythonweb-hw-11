from slowapi import Limiter
from slowapi.util import get_remote_address

# Обмежуємо кількість запитів за IP-адресою клієнта.
limiter = Limiter(key_func=get_remote_address)
