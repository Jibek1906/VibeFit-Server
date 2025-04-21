from django.db import migrations

def reset_water_values(apps, schema_editor):
    DailyNutrition = apps.get_model('nutrition', 'DailyNutrition')
    DailyNutrition.objects.filter(water_intake__isnull=True).update(water_intake=0)

class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0002_alter_dailynutrition_water_intake'),
    ]

    operations = [
        migrations.RunPython(reset_water_values),
    ]
