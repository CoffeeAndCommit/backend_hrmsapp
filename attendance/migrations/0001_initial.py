# Generated manually for Attendance app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, help_text='Attendance date')),
                ('in_time', models.DateTimeField(blank=True, help_text='Check-in time', null=True)),
                ('out_time', models.DateTimeField(blank=True, help_text='Check-out time', null=True)),
                ('office_working_hours', models.CharField(default='09:00', help_text="Scheduled working hours (e.g., '09:00', '10:38')", max_length=10)),
                ('orignal_total_time', models.IntegerField(default=32400, help_text='Scheduled total time in seconds (default 32400 = 9 hours)')),
                ('seconds_actual_worked_time', models.IntegerField(default=0, help_text='Actual time worked in seconds')),
                ('seconds_actual_working_time', models.IntegerField(default=0, help_text='Actual working time in seconds')),
                ('seconds_extra_time', models.IntegerField(default=0, help_text='Extra/overtime in seconds (can be negative for undertime)')),
                ('office_time_inside', models.IntegerField(default=0, help_text='Time spent inside office in seconds')),
                ('day_type', models.CharField(choices=[('WORKING_DAY', 'Working Day'), ('FUTURE_WORKING_DAY', 'Future Working Day'), ('WEEKEND_OFF', 'Weekend Off'), ('HOLIDAY', 'Holiday'), ('HALF_DAY', 'Half Day'), ('LEAVE_DAY', 'Leave Day')], default='WORKING_DAY', help_text='Type of day', max_length=20)),
                ('extra_time_status', models.CharField(blank=True, choices=[('+', 'Overtime'), ('-', 'Undertime'), ('', 'No Extra Time')], default='', help_text="Status of extra time (+ for overtime, - for undertime)", max_length=1)),
                ('admin_alert', models.IntegerField(default=0, help_text='Admin alert flag (0 or 1)')),
                ('admin_alert_message', models.CharField(blank=True, help_text="Admin alert message (e.g., 'In/Out Time Missing')", max_length=200)),
                ('day_text', models.TextField(blank=True, help_text="Day text message (e.g., 'Previous month pending time merged!!')")),
                ('text', models.TextField(blank=True, help_text='Additional text field')),
                ('is_day_before_joining', models.BooleanField(default=False, help_text='Is this day before employee joining date')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_attendances', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(help_text='Employee for this attendance record', on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='employees.employee')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_attendances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Attendance',
                'verbose_name_plural': 'Attendances',
                'ordering': ['-date', 'employee'],
            },
        ),
        migrations.AddIndex(
            model_name='attendance',
            index=models.Index(fields=['employee', 'date'], name='attendance_employee_idx'),
        ),
        migrations.AddIndex(
            model_name='attendance',
            index=models.Index(fields=['date'], name='attendance_date_idx'),
        ),
        migrations.AddIndex(
            model_name='attendance',
            index=models.Index(fields=['day_type'], name='attendance_day_type_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('employee', 'date')},
        ),
    ]

