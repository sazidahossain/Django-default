# Generated by Django 2.1.4 on 2018-12-22 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0002_auto_20181222_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accident',
            name='status',
            field=models.CharField(choices=[('Accepted', 'accepted'), ('Pending', 'pending'), ('Expired', 'expired'), ('New', 'new')], default='New', max_length=120),
        ),
        migrations.AlterField(
            model_name='accident',
            name='status_for_staff',
            field=models.CharField(blank=True, choices=[('Declined', 'declined'), ('Accepted', 'accepted')], max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='civil_id',
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
