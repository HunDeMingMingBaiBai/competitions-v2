"""
Common utilities to interact with Azure Storage.
"""

from pathlib import Path
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from qcloud_cos import CosConfig, CosS3Client
import logging

logger = logging.getLogger('CosStorage')

@deconstructible()
class CosStorage(Storage):
    def __init__(self, *args, **kwargs):
        secret_id = settings.COS_SECRET_ID
        secret_key = settings.COS_SECRET_KEY
        region = settings.COS_REGION
        token = settings.COS_TOKEN
        if 'cos_bucket' in kwargs:
            self.bucket = kwargs['cos_bucket']
        else:
            self.bucket = settings.COS_BUCKET_PUBLIC

        self.config = CosConfig(Region=region,
                                SecretId=secret_id,
                                SecretKey=secret_key,
                                Token=token)

    def _open(self, name, mode='rb'):

        logger.debug('=*' * 50)
        logger.debug(name)
        logger.debug(type(name))

        client = CosS3Client(self.config)
        response = client.get_object(self.bucket, name)

        tmpf = Path('/', name)

        logger.debug('@@' * 50)

        parent = tmpf.parent

        if not parent.exists():
            # @TODO, replace pathlib.Path to os.path
            parent.mkdir(parents=True) # add by cg 3.7
        response['Body'].get_stream_to_file(tmpf.as_posix())
        return open(tmpf.as_posix(), mode)

    def _save(self, name, content):
        client = CosS3Client(self.config)
        res = client.put_object(self.bucket, content.read(), name)
        return name

    def exists(self, name):
        client = CosS3Client(self.config)
        response = client.object_exists(self.bucket, name)
        return response

    def url(self, name):
        if getattr(settings, 'COS_URL', ''):
            url = "{}/{}".format(settings.COS_URL, name)
        elif getattr(settings, 'COS_FAST_CDN', False):
            url = "https://{}.file.myqcloud.com/{}".format(
                self.bucket, name)
        else:
            url = "https://{}.cos.{}.myqcloud.com/{}".format(
                self.bucket, settings.COS_REGION, name
            )

        return url

    def size(self, name):
        client = CosS3Client(self.config)
        response = client.head_object(self.bucket, name)
        return response['Content-Length']

    def delete(self, name):
        client = CosS3Client(self.config)
        client.delete_object(self.bucket, name)

    def make_cos_url(self, name, permission, duration):
        client = CosS3Client(self.config)
        url = client.get_presigned_url(
            Bucket=self.bucket,
            Key=name,
            Method='GET' if permission == 'r' else 'PUT',
            Expired=duration,
        )
        return url

# TODO figure out the meaning of this argument
PREFERRED_STORAGE_COS_VERSION = '2019-11-27'
