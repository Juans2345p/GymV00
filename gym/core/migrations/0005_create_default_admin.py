from django.db import migrations


def create_admin(apps, schema_editor):
    Usuario = apps.get_model('core', 'Usuario')
    if not Usuario.objects.filter(nombre='admin').exists():
        Usuario.objects.create(nombre='admin', password='admin', admin=1)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_mqttconfig_racha_enabled_and_more'),
    ]

    operations = [
        migrations.RunPython(create_admin, migrations.RunPython.noop),
    ]