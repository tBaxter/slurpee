from django.contrib import admin
from slurpee.models import *

class SourceAdmin(admin.ModelAdmin):
    model=Source
    prepopulated_fields = {'slug': ('title',)} 
    list_display = ('title','summary','feed_url','content_type','use_dropbox','vmix_id',)
    fieldsets = (
        ('Source feed info', {'fields': ('title','summary', 'feed_url', 'content_type',)}),
        ('Content routing',  {'fields': ('site', 'source','assign_to','import_unpub')}),
        ('Article fields',   {'fields': ('opinion','use_dropbox')}),
        ('Video fields',     {'fields': ('vmix_id',)}),
        ('Admin fields',     {'fields':('slug',), 'classes': ['collapse',]}),         
    )

admin.site.register(Source, SourceAdmin)


