from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import slugify
from django.utils import safestring
from django.utils.html import strip_tags

import datetime
import feedparser
import time
import urllib
import xmltramp

from articles.helpers import Category
from galleries.models import Gallery, GalleryImage
from slurpee.helpers import clean_text


def copy_file(url, filename, slug):
    """
    Helper function to copy images from source
    """
    f = urllib.urlopen(url).read()
    destination = open(settings.MEDIA_ROOT + 'img/gallery/'+ filename, 'wb+')
    destination.write(f)
    destination.close()


def create_category(title):
    """
    Helper function to create category if it doesn't already exist
    """
    cat = Category(
    	category     = title,
    	slug         = slugify(title),
    )
    cat.save()
    return cat
    
 
def from_workbench(source):
	"""
	Imports gallery from a given workbench XML feed.
	"""
	status = 'attempting to import from feed %s<br>' % source.feed_url 
	feed = urllib.urlopen(source.feed_url)
	xml = xmltramp.parse(feed.read())
	feed.close()
	status = '<br>got feed: %s<br>' % source.feed_url
	
	# Match to section
	try:
		category = Category.objects.get(category=source.title)
	except:
		category = create_category(source.title)
					
	for gallery in xml:
		clean_title = clean_text(str(gallery['name']))
		slug = slugify(clean_title)
		dupe = False            # Set our dupe flag for the following loop
		try:
			existing = Gallery.objects.get(slug=slug) 
			dupe = True
		except:		
			if dupe==False:
				caption = strip_tags(gallery['caption']).replace('\n', '\n\n')
				#for key, val in replacements.items():
				#	caption = caption.replace(key, val)
				
				try:
					i = Gallery(
						title     = clean_title,
						slug         = slug,
						summary      = caption,
						created      = datetime.datetime.now(),
						sellable     = False
					)
					i.save()
					
					i.sections.add(category.id)
					i.site.add(source.site.id)
					status += 'Imported %s<br>' % i.title

				except Exception, inst:
					status +=  'Error importing gallery: %s<br>' % inst
							
				for image in gallery.images:
					url = str(image['url']).replace('.standalone.', '.source.')
					filename = url.rsplit('/', 1)[1]
					conn = urllib.urlopen(url)
					data = conn.read()
					conn.close()
					path = SimpleUploadedFile('img/gallery/'+filename, data)
					#copy_file(url, filename, category.slug)
					img_caption = clean_text(str(image['caption']))
					
					img = GalleryImage(
						image    = path, 
						caption  = img_caption,
						gallery=i,
						)
					img.save() 
					if img.image.height > img.image.width:
					   img.vertical = True
					   img.save() 
				status +='-- Imported images for %s<br>' % i.title
				i.save()
		#status = 'Imported articles from feed'
	return status
	
	
	
	
def from_rss(source):
	"""
	Imports galleries from a given source feed url.
	Is used as a fallback for cases in which we're not pulling workbench galleries
	"""
	status = 'attempting to import from feed %s<br>' % source.feed_url 
	d = feedparser.parse(source.feed_url)
	status = '<br>got feed: %s<br>' % source.feed_url
	slurpee_source = source

	clean_title = clean_text(d['feed']['title'])
	slug = slugify(clean_title)
	
	dupe=False
	try:
		gallery = Gallery.objects.get(slug=slug) 
		dupe = True
	except:		
		if dupe==False:
			gallery = Gallery(
				title        = clean_title,
				slug         = slug,
				created      = datetime.datetime.now(),
				sellable     = False
			)
			gallery.save()
	
	
	for item in d.entries:
		url = str(item.title)
		filename = url.rsplit('/', 1)[1]
		upload_path = 'img/gallery/'+filename
		photo_dupe = False
		try:
			photo = Upload.objects.get(image=upload_path)
			dupe  = True 
		except:
			if dupe == False:
				f = urllib.urlopen(url)
				data = f.read()
				f.close()
				path = SimpleUploadedFile(upload_path, data)
				img_caption = clean_text(unicode(item['description']))

				img = GalleryImage(
					image    = path, 
					caption  = img_caption,
					gallery  = gallery,
					byline   = item['author'],
				)
				img.save()
					
	#status = 'Imported articles from feed'
	return status