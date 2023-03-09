from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
"""
six.text_type - это строковый тип данных, который совместим со старыми и новыми версиями языка Python.

Код from six import text_type импортирует text_type из библиотеки six. 
Библиотека six используется для обеспечения обратной совместимости между Python 2 и Python 3, 
поэтому импортирование text_type из этой библиотеки обеспечивает совместимость кода между разными версиями языка Python.

Когда в коде необходимо создать строку, необходимо использовать text_type вместо str. 
text_type будет использовать unicode в Python 2 и str в Python 3, 
что обеспечивает корректную обработку символов Unicode в обеих версиях языка Python.
"""


class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)


token_generator = AppTokenGenerator()

