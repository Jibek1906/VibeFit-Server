# Generated by Django 5.1.6 on 2025-04-22 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0011_fooditem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fooditem',
            options={'ordering': ['name'], 'verbose_name': 'Food Item', 'verbose_name_plural': 'Food Items'},
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='calories',
            field=models.PositiveIntegerField(help_text='Calories per 100g'),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='carbs',
            field=models.DecimalField(decimal_places=1, help_text='Carbs per 100g', max_digits=5),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='fats',
            field=models.DecimalField(decimal_places=1, help_text='Fats per 100g', max_digits=5),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='proteins',
            field=models.DecimalField(decimal_places=1, help_text='Proteins per 100g', max_digits=5),
        ),
    ]
