# Generated by Django 5.0.1 on 2024-01-14 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_alter_product_options_alter_product_product_img_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={},
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='email_is_verified',
            new_name='token_used',
        ),
    ]
