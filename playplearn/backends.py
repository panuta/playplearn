import re

from domain.models import UserAccount

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain


class EmailAuthenticationBackend(object):
    def authenticate(self, email=None, password=None):
        if email_re.search(email):
            users = UserAccount.objects.filter(email__iexact=email)
            if users.count() > 0:
                user = users[0]

                if user.check_password(password):
                    return user

        return None

    def get_user(self, user_id):
        try:
            return UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return None
