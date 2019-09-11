__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

import subprocess
import time
import sys

def migrate_with_timeout(timeout = 8):
    """
    Wrapper for Django's migrate method.
    Calling manage.py with migrate option hangs after the migrations had run.
    The migration process is killed after (default) 8 seconds.

    `manage.py migrate` needs to be called twice due to SQL IntegrityError
    being raised when adding a new user
    """

    p = subprocess.Popen([sys.executable, "manage.py", "migrate"], stderr = subprocess.DEVNULL)
    time.sleep(timeout)
    p.terminate()

    p = subprocess.Popen([sys.executable, "manage.py", "makemigrations"], stderr = subprocess.DEVNULL)
    time.sleep(timeout)
    p.terminate()

    p = subprocess.Popen([sys.executable, "manage.py", "migrate"], stderr = subprocess.DEVNULL)
    time.sleep(timeout)
    p.terminate()

if __name__ == "__main__":
    migrate_with_timeout()
