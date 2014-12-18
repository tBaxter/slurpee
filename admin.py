from django.contrib import admin

from slurpee.models import Source


class SourceAdmin(admin.ModelAdmin):
    model=Source
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title','summary','feed_url','content_type',)
    fieldsets = (
        ('Source feed info', {'fields': ('title','summary', 'feed_url', 'content_type',)}),
        ('Content routing',  {'fields': ('site', 'source','assign_to','import_unpub')}),
        ('Admin fields',     {'fields':('slug',), 'classes': ['collapse',]}),
    )

admin.site.register(Source, SourceAdmin)
