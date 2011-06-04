from re_eat.tests.common import TestCase
from re_eat.models import Tag, Session

class TagTestCase(TestCase):
    def setUp(self):
        super(TagTestCase, self).setUp()

    def test_get_existing_tag(self):
        t = Tag('yay')
        Session.add(t)

        self.assertEqual(t, Tag.get('yay'))

    def test_new_tag(self):
        t = Tag.get('yay')

        self.assertEqual(t.name, 'yay')
