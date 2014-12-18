from django.core.management.base import BaseCommand

from slurpee.views import slurp

# management command
class Command(BaseCommand):
    help = 'Slurps content from defined sources'

    def handle(self, *args, **options):
        slurp()
        self.stdout.write('Successfully slurped content.')


if __name__ == "__main__":
    slurp()
