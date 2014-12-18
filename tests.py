from django.test import TestCase

from .views import slurp


class SlurpeeViewsTestCase(TestCase):

    def test_importers(self):
        resp = self.client.get('/slurpee/')
        self.assertEqual(resp.status_code, 200)

        # test slurping
        slurp()

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

