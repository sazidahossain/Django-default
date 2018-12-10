# Generated by Django 2.1.4 on 2018-12-10 16:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('traffic', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accident',
            name='user',
        ),
        migrations.RemoveField(
            model_name='population',
            name='name',
        ),
        migrations.AddField(
            model_name='accident',
            name='involved',
            field=models.ManyToManyField(to='traffic.Population'),
        ),
        migrations.AddField(
            model_name='population',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='accident',
            name='images',
            field=models.ImageField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='accident',
            name='status',
            field=models.CharField(choices=[('Accepted', 'accepted'), ('Pending', 'pending'), ('Expired', 'expired')], default='Pending', max_length=120),
        ),
    ]
