from django.db import migrations

def fix_water_intake(apps, schema_editor):
    DailyNutrition = apps.get_model('nutrition', 'DailyNutrition')
    # Set null/negative values to 0
    DailyNutrition.objects.filter(water_intake__isnull=True).update(water_intake=0)
    DailyNutrition.objects.filter(water_intake__lt=0).update(water_intake=0)

class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0004_auto_20250421_1625'),
    ]

    operations = [
        migrations.RunPython(fix_water_intake),
    ]