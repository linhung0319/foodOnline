# Generated by Django 5.0.6 on 2024-06-15 09:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendor", "0002_rename_vender_name_vendor_vendor_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="vendor",
            name="vendor_slug",
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]
