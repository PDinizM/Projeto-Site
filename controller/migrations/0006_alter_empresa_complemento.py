# Generated by Django 5.2.3 on 2025-06-15 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0005_alter_empresa_numero_endereco'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='complemento',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
