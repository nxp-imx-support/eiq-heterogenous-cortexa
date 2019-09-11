__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.contrib import admin
from .models import ImageDatabase, LogsDatabase

class Image(admin.ModelAdmin):
    fields = (
        'id',
        'name',
        'face',
        'thumbnail'
    )

    readonly_fields = (
        'id',
        'thumbnail',
    )

class ImageTimestamp(admin.ModelAdmin):
    fields = (
        'id',
        'name',
        'timestamp',
        'thumbnail',
        'known',
    )

    readonly_fields = (
        'id',
        'name',
        'timestamp',
        'thumbnail',
        'known',
    )

# Register your models here.
admin.site.register(ImageDatabase, Image)
admin.site.register(LogsDatabase, ImageTimestamp)
