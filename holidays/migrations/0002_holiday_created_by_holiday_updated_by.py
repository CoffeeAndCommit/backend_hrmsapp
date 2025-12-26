import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

def add_holiday_tracking_idempotent(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # created_by
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'holidays_holiday' AND column_name = 'created_by_id' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE holidays_holiday ADD COLUMN created_by_id bigint unsigned NULL")
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name = 'holidays_holiday' AND constraint_name = 'holidays_holiday_created_by_id_fk' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE holidays_holiday ADD CONSTRAINT holidays_holiday_created_by_id_fk FOREIGN KEY (created_by_id) REFERENCES auth_app_user(id)")

        # updated_by
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'holidays_holiday' AND column_name = 'updated_by_id' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE holidays_holiday ADD COLUMN updated_by_id bigint unsigned NULL")
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name = 'holidays_holiday' AND constraint_name = 'holidays_holiday_updated_by_id_fk' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE holidays_holiday ADD CONSTRAINT holidays_holiday_updated_by_id_fk FOREIGN KEY (updated_by_id) REFERENCES auth_app_user(id)")

def remove_holiday_tracking_idempotent(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE holidays_holiday DROP FOREIGN KEY IF EXISTS holidays_holiday_created_by_id_fk")
        cursor.execute("ALTER TABLE holidays_holiday DROP COLUMN IF EXISTS created_by_id")
        cursor.execute("ALTER TABLE holidays_holiday DROP FOREIGN KEY IF EXISTS holidays_holiday_updated_by_id_fk")
        cursor.execute("ALTER TABLE holidays_holiday DROP COLUMN IF EXISTS updated_by_id")

class Migration(migrations.Migration):

    dependencies = [
        ('holidays', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_holiday_tracking_idempotent, remove_holiday_tracking_idempotent),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='holiday',
                    name='created_by',
                    field=models.ForeignKey(blank=True, help_text='User who created this holiday', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_holidays', to=settings.AUTH_USER_MODEL),
                ),
                migrations.AddField(
                    model_name='holiday',
                    name='updated_by',
                    field=models.ForeignKey(blank=True, help_text='User who last updated this holiday', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_holidays', to=settings.AUTH_USER_MODEL),
                ),
            ]
        ),
    ]
