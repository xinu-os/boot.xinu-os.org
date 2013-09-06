import base64
import hashlib
import hmac
import urllib

from os.path import join
from random import random
from time import time

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils import simplejson as json
from django.views.generic import View

from kernels.models import Kernel


class ProtectedMixin(object):

    @staticmethod
    def is_my_account(obj):
        """Check if the Django CBV user is the same as the request."""
        return obj.request.user.pk == int(obj.kwargs['pk'])

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Prevent users that are not logged in from seeing this view."""
        return super(ProtectedMixin, self).dispatch(*args, **kwargs)


class S3SignerView(View):

    def sign_request(self, request):
        signature = hmac.new(settings.AWS_SECRET_ACCESS_KEY,
                             request,
                             hashlib.sha1)
        signature = base64.encodestring(signature.digest())
        signature = signature.strip()
        return signature

    def make_request(self, object_name, mime_type, expires):
        amazon_headers = "x-amz-acl:public-read"

        put_request = ('PUT\n\n'
                       '{mime_type}\n'
                       '{expires}\n'
                       '{amazon_headers}\n'
                       '/{bucket}/{object_name}')
        put_request = put_request.format(mime_type=mime_type,
                                         expires=expires,
                                         amazon_headers=amazon_headers,
                                         bucket=settings.S3_BUCKET_NAME,
                                         object_name=object_name)
        return put_request

    def signed_request(self, url, expires):
        request = self.make_request(self.object_name, self.mime_type, expires)
        signature = self.sign_request(request)
        params = urllib.urlencode({
            'AWSAccessKeyId': settings.AWS_ACCESS_KEY_ID,
            'Signature': signature,
            'Expires': expires,
        })
        return '{url}?{params}'.format(url=url, params=params)

    def get_hash(self, user):
        h = hashlib.sha1(user.username)
        h.update(str(random()))
        h.update(settings.AWS_SECRET_ACCESS_KEY)
        return h.hexdigest()

    def get_object_name(self, hash_):
        name = hash_ + '.bin'
        return join(Kernel.IMAGE_PATH, name[0:2], name)

    def get_s3_request(self):
        hash_ = self.get_hash(self.request.user)
        self.object_name = self.get_object_name(hash_)
        self.mime_type = self.request.GET.get('s3_object_type')
        # Protect against weird mime types
        if '/' not in self.mime_type:
            self.mime_type = ''

        expires = int(time() + 300)
        url = 'https://{bucket}.s3.amazonaws.com/{object_name}'
        url = url.format(bucket=settings.S3_BUCKET_NAME,
                         object_name=self.object_name)

        signed_request = self.signed_request(url, expires)

        return {'signed_request': signed_request, 'url': url}

    def get_json_response(self, content, **kwargs):
        return HttpResponse(json.dumps(content),
                            content_type='application/json',
                            **kwargs)

    def get(self, request, *args, **kwargs):
        return self.get_json_response(self.get_s3_request())

