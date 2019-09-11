__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.db import models
from django.db.models.query import QuerySet

# Based on https://stackoverflow.com/questions/1471909/django-model-delete-not-triggered

class ImageQueryMixin(object):
    """ Methods that appear both in the manager and queryset. """
    def delete(self):
        # Use individual queries to the attachment is removed.
        for entry in self.all():
            entry.delete()


class ImageQuerySet(ImageQueryMixin, QuerySet):
    pass

class ImageDatabaseManager(models.Manager):

    def __init__(self):
        super(ImageDatabaseManager, self).__init__()

    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)

class LogsDatabaseManager(models.Manager):

    def __init__(self):
        super(LogsDatabaseManager, self).__init__()

    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)        