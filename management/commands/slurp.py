from django.core.management.base import BaseCommand, CommandError
from slurpee.views import slurp

# management command
class Command(BaseCommand):
	help = 'Slurps content from workbench'

	def handle(self, *args, **options):	
		slurp()
		self.stdout.write('Successfully slurped content.')
		
		


# if running from cron
if __name__ == "__main__":
	import sys, os
	# this needs to be a passed argument a la newsgate importer.
	PROJECT_NAME = 'joco913'
	# JASON'S LAPTOP
	# sys.path.append('C:/Python27/Lib/site-packages/django')
	# sys.path.append('c:/users/jgoldstein/django/django-projects/apps')
	# sys.path.append('c:/users/jgoldstein/django/django-projects/utils')
	# sys.path.append('c:/users/jgoldstein/django/django-projects')
	# sys.path.append('c:/users/jgoldstein/django/django-projects/%s' % PROJECT_NAME)
	# os.environ['DJANGO_SETTINGS_MODULE'] = '%s.local-settings' % PROJECT_NAME
	
	# RACKSPACE
	sys.path.append('/opt/Python2.7/lib/python2.7/site-packages/django')
	sys.path.append('/var/www/html/sites/django_projects/apps')
	sys.path.append('/var/www/html/sites/django_projects/utils')
	sys.path.append('/var/www/html/sites/django_projects')
	sys.path.append('/var/www/html/sites/django_projects/%s' % PROJECT_NAME)
	os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % PROJECT_NAME
	
	slurp()
	sys.exit()


