# Generated migration to add booking_type field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0007_auto_20251013_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='booking_type',
            field=models.CharField(
                choices=[('viewing', 'Property Viewing'), ('airbnb', 'Airbnb Booking')],
                default='viewing',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('confirmed', 'Confirmed'),
                    ('checked_out', 'Checked Out'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AlterConstraint(
            model_name='booking',
            name='unique_viewing_booking',
            constraint=models.UniqueConstraint(
                condition=models.Q(('booking_type', 'viewing')),
                fields=('listing', 'date', 'time'),
                name='unique_viewing_booking'
            ),
        ),
    ]

