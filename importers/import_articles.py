import xmltramp
import time
import datetime
import urllib
import feedparser
import simplejson

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import slugify

from articles.models import Article, ArticleImage
from articles.helpers import Category
from slurpee.helpers import copy_file, clean_text, workbench_to_markdown

media = xmltramp.Namespace("http://search.yahoo.com/mrss")


def get_image_path(filename, pub_date):
    """
    Helper function to clean upload filenames and store them away tidily on the server.
    """
    clean_name = filename.lower().replace(' ','_')
    return 'img/articles/%s/%s/%s' % (pub_date.year, pub_date.month, clean_name)



def from_feed(source):
    """
    Imports articles from a given source RSS feed url.
    The JSON version below is generally more reliable and fuller-featured,
    so it is preferred.
    """
    status = 'attempting to import from feed %s<br>' % source.feed_url
    d = feedparser.parse(source.feed_url)
    status = '<br>got feed: %s<br>' % source.feed_url
    slurpee_source = source

    # Match to section, if one has been assigned.
    slug=slugify(source.title)
    if source.assign_to:
        category = source.assign_to
    else:
        category = Category.objects.get_or_create(category=source.title, slug=slug)

    # check if stories should be published.
    publication_status = "Published"
    if source.import_unpub:
        publication_status = "Draft"

    for item in d.entries:
        clean_title = unicode(item.title)
        clean_title = clean_text(clean_title)
        clean_title = item.title
        slug = slugify(clean_title)
        dupe = False            # Set our dupe flag for the following loop
        try:
            dupe = Article.all_objects.get(slug=slug) # note use of all_objects manager, to check against killed stories, too.
        except:
            if dupe==False:
                item.description = clean_text(item.description)
                cleanbody = item.description
                try:
                    pub_date = time.strftime("%Y-%m-%d %H:%M:%S", item.updated_parsed)
                except:
                    pub_date = datetime.datetime.now()
                i = None

                author = ''
                if item.has_key('author'):
                    author = item.author

                if slurpee_source.source:
                    source = slurpee_source.source
                else:
                    try:
                        source = settings.SOURCE
                    except:
                        source = 'Unknown'
                try:
                    i = Article(
                        headline     = clean_title,
                        other_author = author,
                        slug         = slug,
                        source       = source,
                        summary      = cleanbody[:200].rsplit(' ', 1)[0]+'...',
                        body         = cleanbody,
                        publication  = publication_status,
                        opinion      = source.opinion,
                    )
                    i.save()
                    i.created      = pub_date
                    i.save()

                    i.sections.add(category[0].id)
                    status += 'Imported %s<br>' % i.headline

                except Exception, inst:
                    status +=  'Error importing article: %s<br>' % inst

                if i and item.has_key('media_content'):
                    status += "-- Found media_content. Attempting to import<br>"

                    for m in item.media_content:
                        url = m['url'].replace('.St.', '.So.').replace('.WiPh.', '.So.').replace('.Hi.', '.So.')
                        #if settings.DEFAULT_FILE_STORAGE:
                        try:
                            conn = urllib.urlopen(url)
                        except: #failed to open
                            url = m['url']
                            conn = urllib.urlopen(url)

                        filename = url.rsplit('/', 1)[1]
                        data = conn.read()
                        conn.close()

                        full_path = get_image_path(filename, pub_date)

                        # make sure we haven't already uploaded this sucker
                        if full_path not in i.image_set.values_list('image', flat=True):
                            path = SimpleUploadedFile(full_path, data)

                            if item.media_description:
                                item.media_description = clean_text(item.media_description)
                                caption = item.media_description
                            else:
                                caption = ''
                            byline =''
                            if item.has_key('media_credit'):
                                byline = item['media_credit']

                            img = ArticleImage(
                                image   = path,
                                caption = caption,
                                byline  = byline,
                                article=i
                            )
                            img.save()
                        status +=  '-- Imported new images from media_content for %s<br>' % i.headline
                    i.save()

                if item.links:
                    for link in item.links:
                        if link['rel'] == 'enclosure':
                            status += "-- Found enclosure. Attempting to import<br>"
                            url = link['href'].replace('.St.', '.So.').replace('.WiPh.', '.So.').replace('.Hi.', '.So.')
                            filename = url.rsplit('/', 1)[1]
                            copy_file(url, filename, slug)

                            img = ArticleImage(
                                image="img/articles/" + filename,
                                article=i
                            )
                            img.save()
                            status +='-- Imported images from enclosure for %s<br>' % i.headline
                        i.save()
        #status = 'Imported articles from feed'
    return status




def from_json(source):
    """
    Imports articles from a given source json url.
    """
    status   = 'attempting to import from json %s<br>' % source.feed_url
    conn = urllib.urlopen(source.feed_url)
    raw_json = conn.read()
    conn.close()
    raw_json = raw_json.decode("cp1252").encode("utf-8")
    try:
        json     = simplejson.loads(raw_json)
    except:
        return "Error " + status
    status   = '<br>got json: %s<br>' % source.feed_url

    # check if stories should be published.
    publication_status = "Published"
    if source.import_unpub:
        publication_status = "Draft"

    articles   = json['section']
    # Match to section
    if source.assign_to:
        category = source.assign_to
    else:
        slug=slugify(articles['section_name'])
        category = Category.objects.get_or_create(category=source.title, slug=slug)[0]
    status   += '<br>got category: ' + category.category
    status   += '<br>looping through stories<br>'

    for story_id, story in articles['stories'].items():
        updateable = False
        article    = None

        current_images = []
        if article:
            new = False
                    else:
            updateable = True
            new        = True
            status += 'need to create new article<br>'

        if updateable:
            # do some cleanup
            story['body']     = workbench_to_markdown(clean_text(story['body']))
            story['summary']  = clean_text(story['summary'])
            story['author']   = clean_text(story['author'])
            story['headline'] = clean_text(story['headline'])
            pub_date          = datetime.datetime.strptime(story['pub_date'], '%m/%d/%y %H:%M:%S')

            if story['credit_line']:                     # first try to get the source from the story itself
                story_source = story['credit_line']
            elif source.source:                          # then from the slurpee source
                story_source = source.source
            else:
                try:
                    story_source = settings.SOURCE         # or from settings
                except:
                    story_source = 'Unknown'  # or just fallback

            if new:
                status += 'creating story: %s <br>' % story['headline']
                article = Article(
                    headline     = story['headline'],
                    other_author = story['author'],
                    slug         = slugify(story['headline']),
                    source       = story_source,
                    summary      = story['summary'],
                    body         = story['body'],
                    publication  = publication_status,
                    opinion      = source.opinion,
                    cci_id       = story_id,
                    cci_slug     = story['slug'],
                    dateline     = story['dateline'],
                    overline     = clean_text(story['overline']),
                    endnote      = clean_text(story['shirttail']),
                )
                article.save()  # has to be saved before we can override pub date
                article.created = pub_date
                article.sections.add(category.id)
                article.site.add(source.site.id)

                if article.id and story.has_key('images'):
                    status += "-- Found media_content. Attempting to import<br>"
                    for photo_id, photo in story['images'].items():
                        dupe = False
                        filename = photo['source_url'].rsplit('/', 1)[1]
                        path_str = get_image_path(filename, pub_date)
                        shortname = path_str.split('.')[0] # get file name before the first period.

                        if path_str not in current_images:
                            conn = urllib.urlopen(photo['source_url'])
                            data = conn.read()
                            conn.close()
                            path     = SimpleUploadedFile(path_str, data)
                            img      = ArticleImage(
                                image   = path,
                                caption = clean_text(photo['caption']),
                                byline  = photo['photographer'],
                                article = article
                            )
                            img.save()
                    status +=  '-- Imported images for new story %s<br>' % article.headline
            else:
                if article.headline != story['headline']:
                    article.headline  = story['headline']
                if article.summary  != story['summary']:
                    article.summary   = story['summary']
                if article.body     != story['body']:
                    article.body      = story['body']
                    status += 'updating story: %s <br>' % article.headline
                if article.dateline  != story['dateline']:
                    article.dateline = story['dateline']
                if article.overline  != story['overline']:
                    article.overline = story['overline']

                if article.id and story.has_key('images'):
                    img_count = 0
                    for photo_id, photo in story['images'].items():
                        dupe = False
                        filename = photo['source_url'].rsplit('/', 1)[1]
                        path_str = get_image_path(filename, pub_date)
                        shortname = path_str.split('.')[0] # get file name before the first period. Ex: /img/articles/mypic
                        #print shortname
                        #if shortname in current_images:
                        #   print 'found dupe'
                        #   dupe = True
                        #   status += "found match for %s in current_images: %s, skipping<br>" % (shortname, current_images)
                        #   break
                        for i, s in enumerate(current_images):
                            if shortname in s:
                                print 'found dupe'
                                dupe = True
                                status += "found match for %s in current_images, skipping<br>" % (shortname)
                                break

                        #   #print "i: %s" % i
                        #   print "s: %s" % s
                        #
                        #   if shortname in s:
                        #       print 'found %s in %s' % (shortname, s)
                        #       dupe = True
                        #       #status += "found match for %s in current_images: %s, skipping<br>" % (shortname, s)
                        #       break

                        if not dupe:
                            status += "no match for %s, adding<br>" % (shortname)
                            conn = urllib.urlopen(photo['source_url'])
                            data = conn.read()
                            conn.close()
                            path     = SimpleUploadedFile(path_str, data)
                            img      = ArticleImage(
                                image   = path,
                                caption = clean_text(photo['caption']),
                                byline  = photo['photographer'],
                                article = article
                            )
                            img.save()
                            img_count +1

                        """"
                        shortname = filename.replace('.jpg','')
                        for img in article.articleimage_set.values_list('image', flat=True):
                            if shortname in img:
                                photo['dupe'] = True
                            else:
                                photo['dupe'] = False

                        if 'dupe' in photo and photo['dupe'] == False:

                            data     = urllib.urlopen(photo['source_url']).read()
                            filename = photo['source_url'].rsplit('/', 1)[1]
                            path_str = 'img/articles/'+filename
                            path     = SimpleUploadedFile(path_str, data)

                            try:
                                img = ArticleImage.objects.get(image=filename)
                            except:
                                img      = ArticleImage(
                                    image   = path,
                                    caption = clean_text(photo['caption']),
                                    byline  = photo['photographer'],
                                    article = article
                                )
                                img.save()
                        """
                    if img_count > 0:
                        status +=  '-- Imported %s new images for existing story: %s<br>' % (img_count, article.headline)

            article.save()

            """"
            if dupe==False:
                # do some cleanup
                story['body']    = workbench_to_markdown(clean_text(story['body']))
                story['summary'] = clean_text(story['summary'])
                story['author'] = clean_text(story['author'])
                story['headline'] = clean_text(story['headline'])
                # try:
                pub_date = datetime.datetime.strptime(story['pub_date'], '%m/%d/%y %H:%M:%S')
                # except:
                    # pub_date = datetime.datetime.now()
                i = None
                if story['credit_line']:                   # first try to get the source from the story itself
                    story_source = story['credit_line']
                elif source.source:                        # then from the slurpee source
                    story_source = source.source
                else:
                    try:
                        story_source = settings.SOURCE             # or from settings
                    except:
                        story_source = 'The Kansas City Star'      # or just fallback
                try:
                    i = Article(
                        headline     = story['headline'],
                        other_author = story['author'],
                        slug         = slugify(story['headline']),
                        source       = story_source,
                        summary      = story['summary'],
                        body         = story['body'],
                        publication  = publication_status,
                        opinion      = source.opinion,
                        cci_id       = story_id,
                    )
                    i.save()
                    i.created      = pub_date
                    i.save()
                    i.sections.add(category.id)
                    i.site.add(source.site.id)
                    status += 'Imported %s<br>' % i.headline
                except Exception, inst:
                    status +=  'Error importing article: %s<br>' % inst
                if i.id and story.has_key('images'):
                    status += "-- Found media_content. Attempting to import<br>"
                    for photo_id, photo in story['images'].items():
                        data     = urllib.urlopen(photo['source_url']).read()
                        filename = photo['source_url'].rsplit('/', 1)[1]
                        path     = SimpleUploadedFile('img/articles/'+filename, data)
                        photo['caption'] = clean_text(photo['caption'])
                        img      = ArticleImage(
                            image   = path,
                            caption = photo['caption'],
                            byline  = photo['photographer'],
                            article = i
                        )
                        img.save()
                    status +=  '-- Imported images for %s<br>' % i.headline
                    i.save()
            """
        #status = 'Imported articles from feed'
    return status
