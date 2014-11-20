from django.template.defaultfilters import slugify
from video.models import VideoGallery


def from_collection(source):
	"""
	Gets/creates a video gallery from a VMIX collection ID.
	Because the Video app already handles getting videos for a collection,
	we just need to see if the gallery is defined. 
	The actual video importing is done by the save method on video gallery already.
	"""
	slug = slugify(source.title)
	gallery, new_gallery_created = VideoGallery.objects.get_or_create(title=source.title, slug=slug, video_collection = source.vmix_id)

	gallery.save()
	return unicode(gallery)
	