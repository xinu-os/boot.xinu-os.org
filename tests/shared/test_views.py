from mock import patch, Mock
from os.path import join

from django.test import TestCase

from kernels.models import Kernel
from shared.views import S3SignerView


class S3SignerTestCase(TestCase):

    def setUp(self):
        # Access Keys from Amazon docs:
        # http://docs.aws.amazon.com/AmazonS3/
        #   latest/dev/RESTAuthentication.html#RESTAuthenticationExamples
        self.AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
        self.AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        self.S3_BUCKET_NAME = 'johnsmith'

        self.signer = S3SignerView()

    def test_sign_request(self):
        request = ('GET\n'
                   '\n'
                   '\n'
                   'Tue, 27 Mar 2007 19:36:42 +0000\n'
                   '/johnsmith/photos/puppy.jpg')
        with patch('shared.views.settings') as mock_conf:
            mock_conf.AWS_SECRET_ACCESS_KEY = self.AWS_SECRET_ACCESS_KEY
            sig = self.signer.sign_request(request)
        expected = 'bWq2s1WEIj+Ydj0vQ697zp+IXMU='
        self.assertEqual(sig, expected)

    def test_make_request(self):
        my_object = 'my_object'
        my_mime = 'test/test'
        my_expires = 987654321
        with patch('shared.views.settings') as mock_conf:
            mock_conf.S3_BUCKET_NAME = self.S3_BUCKET_NAME
            request = self.signer.make_request(my_object, my_mime, my_expires)
        # Make sure all the expected values are present
        self.assertIn(my_object, request)
        self.assertIn(my_mime, request)
        self.assertIn(str(my_expires), request)
        self.assertIn(self.S3_BUCKET_NAME, request)

    @patch('shared.views.random')
    @patch('shared.views.settings')
    def test_get_hash(self, mock_conf, mock_random):
        mock_conf.AWS_SECRET_ACCESS_KEY = self.AWS_SECRET_ACCESS_KEY
        mock_random.return_value = 0
        user = Mock(username='dummy')
        hash_ = self.signer.get_hash(user)
        # Definately don't want name in new name
        hash_value = '62e70cc5bd1896b212958231788453bc2a5b5284'
        self.assertEqual(hash_, hash_value)

    def test_get_object_name(self):
        # wraps up the "hash" with path and name
        name = 'object_name'
        expected = join(Kernel.IMAGE_PATH, name[0:2], name + '.bin')
        actual = self.signer.get_object_name(name)
        self.assertEqual(actual, expected)

    @patch('shared.views.settings')
    @patch('shared.views.S3SignerView.make_request')
    def test_signed_request(self, mock_request, mock_conf):
        mock_conf.AWS_SECRET_ACCESS_KEY = self.AWS_SECRET_ACCESS_KEY
        mock_conf.AWS_ACCESS_KEY_ID = self.AWS_ACCESS_KEY_ID

        object_name = 'photos/puppy.jpg'
        expires = 1175139620
        request = ('GET\n'
                   '\n'
                   '\n'
                   '{expires}\n'
                   ''
                   '/{bucket}/{object_name}')
        # set expires and set make_request
        mock_request.return_value = request.format(expires=expires,
                                                   object_name=object_name,
                                                   bucket=self.S3_BUCKET_NAME)
        self.signer.object_name = None
        self.signer.mime_type = None
        url = 'https://{bucket}.s3.amazonaws.com/{object_name}'
        url = url.format(bucket=self.S3_BUCKET_NAME, object_name=object_name)
        signed = self.signer.signed_request(url, expires)
        expected = {'AWSAccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
                    'Signature': 'NpgCjnDzrM%2BWFzoENXmpNDUsSn8%3D',
                    'Expires': str(expires)}
        self.assertTrue(signed.startswith(url))
        for key, value in expected.iteritems():
            self.assertIn('='.join([key, value]), signed)

    @patch('shared.views.S3SignerView.get_object_name')
    @patch('shared.views.time')
    @patch('shared.views.settings')
    def test_get_s3_request(self, mock_conf, mock_time, mock_hash):
        self.signer.request = Mock(GET={})
        self.signer.request.GET['s3_object_name'] = 'object'
        self.signer.request.GET['s3_object_type'] = 'class/type'
        self.signer.request.user.username = 'dummy'
        mock_time.return_value = 0
        mock_conf.AWS_SECRET_ACCESS_KEY = self.AWS_SECRET_ACCESS_KEY
        mock_conf.AWS_ACCESS_KEY_ID = self.AWS_ACCESS_KEY_ID
        mock_conf.S3_BUCKET_NAME = self.S3_BUCKET_NAME
        mock_hash.return_value = 'object'
        request = self.signer.get_s3_request()
        url = 'https://johnsmith.s3.amazonaws.com/object'
        expected = {'AWSAccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
                    'Expires': '300',
                    'Signature': 'uVp5lXQlyGMfAp7EOuJXa%2F5hp8E%3D'}
        self.assertEqual(request['url'], url)
        self.assertTrue(request['signed_request'].startswith(url))
        for key, value in expected.iteritems():
            self.assertIn('='.join([key, value]), request['signed_request'])

    def test_get_json_response(self):
        response = self.signer.get_json_response({'a': 1})
        self.assertTrue(response.has_header('content-type'))
        self.assertIn('application/json', response._headers['content-type'])
        self.assertEqual('{"a": 1}', response.content)
