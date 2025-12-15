from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(max_length=160, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='DonationLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('url', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Донат-ссылка',
                'verbose_name_plural': 'Донат-ссылки',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
            ],
            options={'verbose_name': 'Тег', 'verbose_name_plural': 'Теги', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=220, unique=True)),
                ('description', models.CharField(blank=True, max_length=400)),
                ('full_description', models.TextField(blank=True)),
                (
                    'type',
                    models.CharField(
                        choices=[
                            ('manual', 'Мануал / Гайд'),
                            ('script', 'Скрипт / Сниппет'),
                            ('file', 'Файл / Шпаргалка'),
                            ('book', 'Книга'),
                            ('podcast', 'Подкаст'),
                            ('footage', 'Футаж / Медиа'),
                            ('ai_tools', 'AI-инструменты'),
                            ('other', 'Другое'),
                        ],
                        default='other',
                        max_length=20,
                    ),
                ),
                (
                    'difficulty',
                    models.CharField(
                        choices=[('beginner', 'Новичок'), ('intermediate', 'Средний'), ('advanced', 'Продвинутый')],
                        default='beginner',
                        max_length=20,
                    ),
                ),
                ('language', models.CharField(default='ru', max_length=10)),
                ('download_url', models.URLField(blank=True)),
                ('external_url', models.URLField(blank=True)),
                ('affiliate_url', models.URLField(blank=True)),
                ('source_name', models.CharField(blank=True, max_length=200)),
                ('source_url', models.URLField(blank=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'category',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='archive.category'
                    ),
                ),
                ('tags', models.ManyToManyField(blank=True, related_name='resources', to='archive.tag')),
            ],
            options={'verbose_name': 'Ресурс', 'verbose_name_plural': 'Ресурсы', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Bundle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=220, unique=True)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('is_active', models.BooleanField(default=True)),
                ('purchase_url', models.URLField(blank=True)),
                ('resources', models.ManyToManyField(blank=True, related_name='bundles', to='archive.resource')),
            ],
            options={
                'verbose_name': 'Подборка / Bundle',
                'verbose_name_plural': 'Подборки / Bundles',
                'ordering': ['title'],
            },
        ),
    ]
