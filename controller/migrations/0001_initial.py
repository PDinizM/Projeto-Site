# Generated by Django 5.2.3 on 2025-06-15 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnpj', models.CharField(max_length=14, unique=True)),
                ('nome_empresarial', models.CharField(max_length=255)),
                ('data_abertura', models.DateTimeField()),
                ('cep', models.CharField(max_length=8)),
                ('logradouro', models.CharField(max_length=255)),
                ('complemento', models.CharField(max_length=255)),
                ('data_situacao', models.DateTimeField()),
                ('numero_endereco', models.IntegerField()),
                ('bairro', models.CharField(max_length=50)),
            ],
        ),
    ]
