import hashlib

from django.conf import settings
from django.core.files.storage import get_storage_class
from storages.backends.azure_storage import AzureStorage


class CodalabAzureStorage(AzureStorage):

    def __init__(self, *args, **kwargs):
        if 'azure_container' in kwargs:
            self.azure_container = kwargs.pop('azure_container')
        super().__init__(*args, **kwargs)


# Setup actual storage classes we use on the project
StorageClass = get_storage_class(settings.DEFAULT_FILE_STORAGE)

if settings.STORAGE_IS_S3:
    BundleStorage = StorageClass(bucket=settings.AWS_STORAGE_PRIVATE_BUCKET_NAME)
    PublicStorage = StorageClass(bucket=settings.AWS_STORAGE_BUCKET_NAME)
elif settings.STORAGE_IS_GCS:
    BundleStorage = StorageClass(bucket_name=settings.GS_PRIVATE_BUCKET_NAME)
    PublicStorage = StorageClass(bucket_name=settings.GS_PUBLIC_BUCKET_NAME)
elif settings.STORAGE_IS_AZURE:
    BundleStorage = StorageClass(azure_container=settings.BUNDLE_AZURE_CONTAINER)
    PublicStorage = StorageClass(azure_container=settings.AZURE_CONTAINER)
elif settings.STORAGE_IS_COS:
    BundleStorage = StorageClass(cos_bucket=settings.COS_BUCKET_PRIVATE)
    PublicStorage = StorageClass(cos_bucket=settings.COS_BUCKET_PUBLIC)
else:
    raise NotImplementedError()


def md5(filename):
    """Given some file return its md5, works well on large files"""
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
