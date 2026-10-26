from django.db import migrations
from django.utils import timezone


def verify_existing_realtors(apps, schema_editor):
    Realtor = apps.get_model('realtors', 'Realtor')
    Realtor.objects.all().update(is_verified=True, verified_at=timezone.now())


def unverify_realtors(apps, schema_editor):
    Realtor = apps.get_model('realtors', 'Realtor')
    Realtor.objects.all().update(is_verified=False, verified_at=None, verified_by_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('realtors', '0002_realtor_is_verified_realtor_verified_at_and_more'),
    ]

    operations = [
        migrations.RunPython(verify_existing_realtors, unverify_realtors),
    ]
