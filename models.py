from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from articles.helpers import Category

CONTENT_TYPE_CHOICES = (
   ('1', 'Article'),
   ('2', 'Blog'),
   ('3', 'Photo Gallery'),
   ('4', 'Videos'),
)  


class Source(models.Model):
    title             = models.CharField(max_length=200)
    summary           = models.CharField(max_length=200, blank=True, null=True)
    slug              = models.SlugField(max_length=200, blank=True, null=True)
    feed_url          = models.CharField(max_length=200, blank=True, help_text="URL of external RSS or JSON feed")
    site              = models.ForeignKey(Site)
    content_type      = models.CharField(max_length=1,  choices=CONTENT_TYPE_CHOICES, default="1")
    use_dropbox       = models.BooleanField(default=False, 
    								help_text="""
    									Rather than use a feed, pull stories from CCI dropbox. 
    									Note: Make sure the CCI Dropbox is actually configured and working.
    								""")
    vmix_id           = models.CharField('VMIX video collection ID', max_length=20, blank=True)
    source            = models.CharField("Originating source", max_length=100, blank=True, 
    								help_text="Allows you to specify originating source. Example: 'Wichita Eagle'")
    assign_to         = models.ForeignKey(Category, blank=True, null=True, limit_choices_to={ 'sites__id':settings.SITE_ID},
    								help_text="Routes feed into existing section. If one is not selected, Slurpee will create a matching section as needed." )
    opinion           = models.BooleanField('Source is opinion', default=False)
    import_unpub      = models.BooleanField('Import Unpublished', default=False, help_text="If checked, content will be imported but marked unpublished")

    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return self.slug
        
        
        
        

    
