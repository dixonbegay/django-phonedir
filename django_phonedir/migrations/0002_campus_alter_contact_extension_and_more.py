import django.db.models.deletion
from django.db import migrations, models


def handle_location_migration(apps, schema_editor):
    cursor = schema_editor.connection.cursor()

    # Check for existing non-empty location data before doing any schema work.
    # schema_editor.*_field() methods call column_sql() which requires field.concrete,
    # an attribute set only via contribute_to_class in Django 6.x — unavailable on
    # historical model fields. Raw SQL avoids that entirely.
    cursor.execute("SELECT 1 FROM django_phonedir_contact WHERE location != '' LIMIT 1")
    has_data = cursor.fetchone() is not None
    if not has_data:
        cursor.execute("SELECT 1 FROM django_phonedir_faxnumber WHERE location != '' LIMIT 1")
        has_data = cursor.fetchone() is not None

    if has_data:
        Location = apps.get_model('django_phonedir', 'Location')
        Campus = apps.get_model('django_phonedir', 'Campus')
        Building = apps.get_model('django_phonedir', 'Building')

        schema_editor.execute("ALTER TABLE django_phonedir_contact RENAME COLUMN location TO location_text")
        schema_editor.execute("ALTER TABLE django_phonedir_faxnumber RENAME COLUMN location TO location_text")
        schema_editor.execute("ALTER TABLE django_phonedir_contact ADD COLUMN location_id INTEGER NULL")
        schema_editor.execute("ALTER TABLE django_phonedir_faxnumber ADD COLUMN location_id INTEGER NULL")

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

        schema_editor.execute("ALTER TABLE django_phonedir_contact DROP COLUMN location_text")
        schema_editor.execute("ALTER TABLE django_phonedir_faxnumber DROP COLUMN location_text")

    else:
        schema_editor.execute("ALTER TABLE django_phonedir_contact DROP COLUMN location")
        schema_editor.execute("ALTER TABLE django_phonedir_faxnumber DROP COLUMN location")
        schema_editor.execute("ALTER TABLE django_phonedir_contact ADD COLUMN location_id INTEGER NULL")
        schema_editor.execute("ALTER TABLE django_phonedir_faxnumber ADD COLUMN location_id INTEGER NULL")


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
