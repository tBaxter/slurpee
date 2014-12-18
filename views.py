from django.conf import settings

from django.http import HttpResponse

from .importers import import_articles, import_blogs, import_video, import_galleries
from .models import Source


def slurp(request=None):
    """
    Routes to correct importer based on Source parameters and content type.
    Valid content types are:
    ('1', 'Article'),
    ('2', 'Blog'),
    ('3', 'Photo Gallery'),
    ('4', 'Videos')
    """
    full_status = status = ""
    for source in Source.objects.filter(site__id=settings.SITE_ID):
        if source.content_type == "1": # Articles
            if source.feed_url:
                if source.feed_url.find('v-json'):
                    status = import_articles.from_json(source)
                else:
                    status = import_articles.from_feed(source)
            elif source.dropbox:
                # We'll add a dropbox importer when we know how it would work.
                continue
            else:
                return HttpResponse("No article source found")
        full_status += unicode(status)

        if source.content_type == "2": # Blogs
            status = import_blogs.from_feed(source)
            full_status += unicode(status)

        if source.content_type == "3": #PHOTO GALLERY
            if source.feed_url.find('v-full/index.xml'):
                status = import_galleries.from_workbench(source)
            else:
                status = import_galleries.from_rss(source)
            full_status += unicode(status)

        if source.content_type == "4": #Video
            status = import_video.from_collection(source)
            full_status += unicode(status)
    if request:
        return HttpResponse(full_status)
    else:
        print full_status.replace('<br>','\n')
