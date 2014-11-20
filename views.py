from slurpee.models import Source
from django.conf import settings

from django.views.generic.list_detail import object_list
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.defaultfilters import truncatewords
from django.views.decorators.cache import never_cache

from slurpee.importers import import_articles, import_blogs, import_video, import_galleries

import feedparser

from django.utils.html import strip_tags

import datetime
from datetime import datetime


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