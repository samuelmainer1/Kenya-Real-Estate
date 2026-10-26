from django.db import migrations
import uuid

def gen_uuid(apps, schema_editor):
    BlogSubscription = apps.get_model("blog", "BlogSubscription")
    for row in BlogSubscription.objects.all():
        row.unsubscribe_token = uuid.uuid4()
        row.save(update_fields=["unsubscribe_token"])

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0002_blogsubscription_is_active_and_more'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
