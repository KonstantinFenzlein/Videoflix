# Generated migration for TokenBlacklist model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenBlacklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blacklisted_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Token Blacklist',
                'verbose_name_plural': 'Token Blacklists',
                'db_table': 'token_blacklist',
            },
        ),
        migrations.AddIndex(
            model_name='tokenblacklist',
            index=models.Index(fields=['token'], name='token_blacklist_token_idx'),
        ),
        migrations.AddIndex(
            model_name='tokenblacklist',
            index=models.Index(fields=['expires_at'], name='token_blacklist_expires_at_idx'),
        ),
    ]
