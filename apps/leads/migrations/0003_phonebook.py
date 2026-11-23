from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_ga4_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Telefon numarası',
                'verbose_name_plural': 'Telefon rehberi (tüm formlar)',
                'managed': False,
                'default_permissions': ('view',),
            },
        ),
    ]
