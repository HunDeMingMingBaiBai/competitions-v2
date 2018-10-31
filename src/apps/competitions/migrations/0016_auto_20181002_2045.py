# Generated by Django 2.1 on 2018-10-02 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0005_auto_20181002_2045'),
        ('competitions', '0015_auto_20180820_2329'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='zip_file',
        ),
        migrations.AddField(
            model_name='submission',
            name='data',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='datasets.Data'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='submission',
            name='description',
            field=models.CharField(blank=True, default='', max_length=240, null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.DecimalField(blank=True, decimal_places=10, default=None, max_digits=20, null=True),
        ),
    ]
