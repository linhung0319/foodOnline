# Generated by Django 5.0.6 on 2024-06-15 09:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendor", "0004_alter_vendor_vendor_name_alter_vendor_vendor_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="vendor_name",
            field=models.CharField(max_length=50),
        ),
    ]