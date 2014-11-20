from django.test import TestCase

from slurpee.importers import import_articles
from slurpee.views import slurp
class SlurpeeViewsTestCase(TestCase):
    
    def test_importers(self):
        #resp = self.client.get('/slurpee/')
        #self.assertEqual(resp.status_code, 200)
        
        # test slurping
        slurp()

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

