import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

def add_inventory_fields_idempotent(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # device.brand
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'inventory_device' AND column_name = 'brand' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE inventory_device ADD COLUMN brand varchar(100) NOT NULL DEFAULT ''")
        
        # device.condition
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'inventory_device' AND column_name = 'condition' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE inventory_device ADD COLUMN `condition` varchar(20) NOT NULL DEFAULT 'good'")
        
        # device.model_name
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'inventory_device' AND column_name = 'model_name' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE inventory_device ADD COLUMN model_name varchar(200) NOT NULL DEFAULT ''")

        # deviceassignment.condition_at_assignment
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'inventory_deviceassignment' AND column_name = 'condition_at_assignment' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE inventory_deviceassignment ADD COLUMN condition_at_assignment varchar(20) NOT NULL DEFAULT ''")

        # deviceassignment.condition_at_return
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'inventory_deviceassignment' AND column_name = 'condition_at_return' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE inventory_deviceassignment ADD COLUMN condition_at_return varchar(20) NOT NULL DEFAULT ''")

        # deviceassignment.returned_to_id
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'inventory_deviceassignment' AND column_name = 'returned_to_id' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE inventory_deviceassignment ADD COLUMN returned_to_id bigint unsigned NULL")
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name = 'inventory_deviceassignment' AND constraint_name = 'inventory_deviceassignment_returned_to_id_fk' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE inventory_deviceassignment ADD CONSTRAINT inventory_deviceassignment_returned_to_id_fk FOREIGN KEY (returned_to_id) REFERENCES auth_app_user(id)")

        # Indexes
        cursor.execute("SELECT COUNT(*) FROM information_schema.statistics WHERE table_name = 'inventory_device' AND index_name = 'inventory_d_status_458222_idx' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE INDEX inventory_d_status_458222_idx ON inventory_device(status)")

        cursor.execute("SELECT COUNT(*) FROM information_schema.statistics WHERE table_name = 'inventory_deviceassignment' AND index_name = 'inventory_d_returne_eb4ff9_idx' AND table_schema = DATABASE()")
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE INDEX inventory_d_returne_eb4ff9_idx ON inventory_deviceassignment(returned_date)")

def remove_inventory_fields_idempotent(apps, schema_editor):
    pass # No-op for safety in this debug session

class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_employee_slack_user_id'),
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_inventory_fields_idempotent, remove_inventory_fields_idempotent),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='device',
                    name='brand',
                    field=models.CharField(blank=True, help_text='Brand/Manufacturer', max_length=100),
                ),
                migrations.AddField(
                    model_name='device',
                    name='condition',
                    field=models.CharField(choices=[('new', 'New'), ('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], default='good', help_text='Physical condition of the device', max_length=20),
                ),
                migrations.AddField(
                    model_name='device',
                    name='model_name',
                    field=models.CharField(blank=True, help_text='Model name/number of the device', max_length=200),
                ),
                migrations.AddField(
                    model_name='deviceassignment',
                    name='condition_at_assignment',
                    field=models.CharField(blank=True, choices=[('new', 'New'), ('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], help_text='Device condition when assigned', max_length=20),
                ),
                migrations.AddField(
                    model_name='deviceassignment',
                    name='condition_at_return',
                    field=models.CharField(blank=True, choices=[('new', 'New'), ('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], help_text='Device condition when returned', max_length=20),
                ),
                migrations.AddField(
                    model_name='deviceassignment',
                    name='returned_to',
                    field=models.ForeignKey(blank=True, help_text='Admin who received the returned device', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='device_returns_received', to=settings.AUTH_USER_MODEL),
                ),
                migrations.AddIndex(
                    model_name='device',
                    index=models.Index(fields=['status'], name='inventory_d_status_458222_idx'),
                ),
                migrations.AddIndex(
                    model_name='deviceassignment',
                    index=models.Index(fields=['returned_date'], name='inventory_d_returne_eb4ff9_idx'),
                ),
            ]
        ),
    ]
