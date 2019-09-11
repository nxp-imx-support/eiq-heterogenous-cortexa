__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

import os
import getpass
import sys
import platform

# https://stackoverflow.com/a/47700752/10907391
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SmartDoor.settings")

import django
django.setup()

from django.contrib.auth.models import User
from django.db.utils import IntegrityError

# https://developer.ibm.com/answers/questions/257377/how-can-i-run-python-managepy-createsuperuser-inte/#
class AdminCreate(object):
    """
    Wrapper for Django's create_superuser method.
    Calling manage.py with createsuperuser option hangs after the user
    has been created.
    """

    def __init__(self):
        self._os = platform.system()

        try:
             self._prompt_username()
             self._prompt_email()
             self._prompt_password()
             User.objects.create_superuser (username = self._user,
                                            password = self._passw,
                                            email    = self._email)

             print('Superuser created successfully.')
        except IntegrityError as e:
             sys.stderr.write('Username already exits. Try again.\n')

    def _prompt_username(self):
        self._user = ""
        first_loop = True

        while self._user == "":
            if not first_loop:
                sys.stderr.write('Username cannot be empty.\n')
            first_loop = False

            print("Username: ", end = "")
            sys.stdout.flush()
            self._user = input()

    def _prompt_email(self):
        self._email = ""
        first_loop = True

        while not self._email_validated(self._email) or first_loop:
            if not first_loop:
                sys.stderr.write('Invalid email.\n')
            first_loop = False

            print("Email: ", end = "")
            sys.stdout.flush()
            self._email = input()

    def _prompt_password(self):
        self._passw = ""
        passw_again = ""
        first_loop = True

        while self._passw == "":
            if not first_loop:
                sys.stderr.write('Password cannot be empty.\n')
            first_loop = False

            self._passw = getpass.getpass()
            if self._passw == "":
                continue
            passw_again = getpass.getpass("Password (again): ")

            if self._passw != passw_again:
                self._passw = ""
                first_loop = True
                sys.stderr.write('Passwords do not match.\n')
                continue

            if len(self._passw) < 8:
                pass_too_short_str = 'This password is too short. It must contain at least 8 characters.'
                if self._os == 'Windows':
                    print(pass_too_short_str)
                elif self._os == 'Linux':
                    sys.stderr.write('\033[91m' + pass_too_short_str + '\033[0m\n')

                print('Bypass password validation and create user anyway? [y/N]: ', end = '')
                sys.stdout.flush()

                answer = input()
                if answer.strip() != 'y' and answer.strip() != 'Y':
                    self._passw = ""
                    first_loop = True
                    continue

    def _email_validated(self, email):
        return (('@' in email    and '.' in email and  # '@' and '.' chars in email
                email.find('.') != len(email) - 1 and  # '.' is not the last char
                email.find('.') - email.find('@') > 1) # 'example@.com' is not valid
                or (email == ""))                      # empty email is valid

if __name__ == "__main__":
    AdminCreate()
