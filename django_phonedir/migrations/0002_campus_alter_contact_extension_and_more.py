import django.db.models.deletion
from django.db import migrations, models


def handle_location_migration(apps, schema_editor):
    cursor = schema_editor.connection.cursor()

    # Check for existing non-empty location data before doing any schema work
    cursor.execute("SELECT 1 FROM django_phonedir_contact WHERE location != '' LIMIT 1")
    has_data = cursor.fetchone() is not None
    if not has_data:
        cursor.execute("SELECT 1 FROM django_phonedir_faxnumber WHERE location != '' LIMIT 1")
        has_data = cursor.fetchone() is not None

    Contact = apps.get_model('django_phonedir', 'Contact')
    FaxNumber = apps.get_model('django_phonedir', 'FaxNumber')
    Location = apps.get_model('django_phonedir', 'Location')

    contact_old = Contact._meta.get_field('location')
    faxnumber_old = FaxNumber._meta.get_field('location')

    if has_data:
        Campus = apps.get_model('django_phonedir', 'Campus')
        Building = apps.get_model('django_phonedir', 'Building')

        # Rename location → location_text to preserve data while the new FK column is added
        contact_temp = contact_old.clone()
        contact_temp.name = contact_temp.attname = contact_temp.column = 'location_text'
        schema_editor.alter_field(Contact, contact_old, contact_temp)

        faxnumber_temp = faxnumber_old.clone()
        faxnumber_temp.name = faxnumber_temp.attname = faxnumber_temp.column = 'location_text'
        schema_editor.alter_field(FaxNumber, faxnumber_old, faxnumber_temp)

        # Add new FK columns (creates location_id in the DB)
        from django.db.models import ForeignKey
        from django.db.models.deletion import SET_NULL

        contact_fk = ForeignKey(Location, on_delete=SET_NULL, null=True, blank=True, related_name='contacts')
        contact_fk.set_attributes_from_name('location')
        schema_editor.add_field(Contact, contact_fk)

        faxnumber_fk = ForeignKey(Location, on_delete=SET_NULL, null=True, blank=True, related_name='fax_numbers')
        faxnumber_fk.set_attributes_from_name('location')
        schema_editor.add_field(FaxNumber, faxnumber_fk)

        # Migrate old strings into Location objects
        default_campus, _ = Campus.objects.get_or_create(name='Unknown')
        default_building, _ = Building.objects.get_or_create(name='Unknown', campus=default_campus)

        cursor.execute("SELECT id, location_text FROM django_phonedir_contact WHERE location_text != ''")
        for row_id, room in cursor.fetchall():
            loc, _ = Location.objects.get_or_create(room=room, building=default_building)
            cursor.execute(
                "UPDATE django_phonedir_contact SET location_id = %s WHERE id = %s",
                [loc.id, row_id],
            )

        cursor.execute("SELECT id, location_text FROM django_phonedir_faxnumber WHERE location_text != ''")
        for row_id, room in cursor.fetchall():
            loc, _ = Location.objects.get_or_create(room=room, building=default_building)
            cursor.execute(
                "UPDATE django_phonedir_faxnumber SET location_id = %s WHERE id = %s",
                [loc.id, row_id],
            )

        # Drop the temporary text columns
        schema_editor.remove_field(Contact, contact_temp)
        schema_editor.remove_field(FaxNumber, faxnumber_temp)

    else:
        # No existing data — drop old CharField and add new FK without any rename
        schema_editor.remove_field(Contact, contact_old)
        schema_editor.remove_field(FaxNumber, faxnumber_old)

        from django.db.models import ForeignKey
        from django.db.models.deletion import SET_NULL

        contact_fk = ForeignKey(Location, on_delete=SET_NULL, null=True, blank=True, related_name='contacts')
        contact_fk.set_attributes_from_name('location')
        schema_editor.add_field(Contact, contact_fk)

        faxnumber_fk = ForeignKey(Location, on_delete=SET_NULL, null=True, blank=True, related_name='fax_numbers')
        faxnumber_fk.set_attributes_from_name('location')
        schema_editor.add_field(FaxNumber, faxnumber_fk)


class Migration(migrations.Migration):

    dependencies = [
        ('django_phonedir', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='extension',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='faxnumber',
            name='description',
            field=models.CharField(blank=True, max_length=64),
        ),

        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buildings', to='django_phonedir.campus')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.CharField(max_length=64)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='django_phonedir.building')),
            ],
        ),

        # Conditionally handles rename, data migration, and cleanup based on whether
        # existing location strings are present. Uses schema_editor directly so that
        # SQLite's table-recreation constraints are respected.
        migrations.RunPython(handle_location_migration, migrations.RunPython.noop),

        # Resync Django's migration state to reflect what RunPython did at the DB level.
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(model_name='contact', name='location'),
                migrations.AddField(
                    model_name='contact',
                    name='location',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='contacts',
                        to='django_phonedir.location',
                    ),
                ),
                migrations.RemoveField(model_name='faxnumber', name='location'),
                migrations.AddField(
                    model_name='faxnumber',
                    name='location',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='fax_numbers',
                        to='django_phonedir.location',
                    ),
                ),
            ],
        ),
    ]
