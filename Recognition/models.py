__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe
from .managers import ImageDatabaseManager
from .managers import LogsDatabaseManager
from Recognition import recognition_common

import os
import logging

# logger config is done in __init__ for each module
logger = logging.getLogger(__name__)

# Create your models here.
class ImageDatabase(models.Model):
    name = models.CharField(max_length=100, default="Unknown")
    face = models.ImageField(default="")

    objects = ImageDatabaseManager()

    def __str__(self):
        return self.name

    def thumbnail(self):
        return mark_safe('<img src="{}" width="{}" height="{}" />'.format(self.face.url, self.face.width, self.face.height))

    def delete(self, *args, **kwargs):
        """
        This method can be called directly as a result
        """
        logger.info("   >>>[ImageDatabase][delete]: " + self.name)
        recognition_common.deleteTrainSamplesForId(str(self.id))
        recognition_common.clearRecognitionModel()
        super(ImageDatabase, self).delete(*args, **kwargs)


class LogsDatabase(models.Model):
    name = models.CharField(max_length=100, default="Unknown")
    face = models.ImageField(upload_to="timestamps", default="")
    timestamp = models.CharField(max_length=20, default="20000101000000")
    known = models.BooleanField(default=False)

    objects = LogsDatabaseManager()

    def __str__(self):
        return self.name

    def thumbnail(self):
        return mark_safe('<img src="{}" width="{}" height="{}" />'.format(self.face.url, self.face.width, self.face.height))

    def delete(self, *args, **kwargs):
        recognition_common.deleteLogsForTimestamp(str(self.timestamp))
        recognition_common.clearRecognitionModel()
        super(LogsDatabase, self).delete(*args, **kwargs)
