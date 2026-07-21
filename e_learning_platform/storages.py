from storages.backends.s3 import S3Storage
from django.conf import settings


class SupabasePublicStorage(S3Storage):
    """
    Supabase ko S3-compatible endpoint (storage.supabase.co/storage/v1/s3/...)
    signed/authenticated access ko lagi ho — browser le directly load garda
    403 dincha.

    Public image/video serve garna Supabase ko arkai URL format chahincha:
    https://<project>.supabase.co/storage/v1/object/public/<bucket>/<path>

    Yo class le .url() override garera tyo public URL banauxa.
    Bucket "Public" configured huna paryo Supabase dashboard ma.
    """

    def url(self, name, parameters=None, expire=None):
        name = self._normalize_name(self._clean_name(name))
        base_url = settings.SUPABASE_PROJECT_URL.rstrip('/')
        return f"{base_url}/storage/v1/object/public/{self.bucket_name}/{name}"