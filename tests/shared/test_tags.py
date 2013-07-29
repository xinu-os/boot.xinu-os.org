from mock import PropertyMock

from django.test import TestCase

from shared.templatetags import shared_tags


class SharedTagsTestCase(TestCase):
    def test_blank_url(self):
        url = '/'
        request = PropertyMock(path=url)
        context = {'request': request}
        active = shared_tags.active(context, url)
        self.assertEqual(active, 'active')

    def test_actual_url(self):
        url = '/about'
        request = PropertyMock(path=url)
        context = {'request': request}
        active = shared_tags.active(context, url)
        self.assertEqual(active, 'active')

    def test_other_url(self):
        url = '/about'
        request = PropertyMock(path='/kernels')
        context = {'request': request}
        active = shared_tags.active(context, url)
        self.assertNotEqual(active, 'active')

    def test_anti_spam(self):
        pre = 'fake-email+address@example.org'
        post = 'fake {dash} email {plus} address {at} example {dot} org'
        real = shared_tags.anti_spam(pre)
        self.assertEqual(post, real)
