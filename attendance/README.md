# Attendance App

Attendance management system for HRMS with check-in/check-out functionality, overtime calculation, and monthly summaries.

## Features

- Check-in/Check-out tracking with timestamps
- Overtime/undertime calculation (in seconds, formatted as "Xh : Ym :Zs")
- Employee-specific attendance tracking
- Monthly attendance summary with compensation tracking
- Day type detection (WORKING_DAY, WEEKEND_OFF, HOLIDAY, HALF_DAY, LEAVE_DAY)
- Admin alerts for missing check-in/check-out
- Integration with holidays app for holiday detection
- Permission-based access control
- Filtering and search capabilities
- API response format: `{error: 0, data: {...}}`

## API Endpoints

### Standard CRUD
- `GET /api/attendance/` - List all attendance (filtered by permissions)
- `GET /api/attendance/{id}/` - Get attendance details
- `POST /api/attendance/` - Create attendance record (Admin only)
- `PATCH /api/attendance/{id}/` - Update attendance (Admin only)
- `DELETE /api/attendance/{id}/` - Delete attendance (Admin only)

### Custom Actions
- `POST /api/attendance/check-in/` - Employee check-in
- `POST /api/attendance/check-out/` - Employee check-out
- `GET /api/attendance/monthly/` - Get monthly attendance summary
  - Query params: `month` (1-12), `year` (e.g., 2025), `userid` (optional)
  - Returns: `{error: 0, data: {attendance: [...], monthSummary: {...}, compensationSummary: {...}, ...}}`
- `GET /api/attendance/today/` - Get today's attendance for logged-in employee
- `GET /api/attendance/my-attendance/` - Get logged-in employee's attendance history

## Models

### Attendance
- Employee relationship (ForeignKey)
- Date, check-in/check-out times
- Working hours and time calculations (in seconds)
- Day type, alerts, and messages
- System fields (created_at, updated_at, created_by, updated_by)

## Usage

### Check-in
```bash
POST /api/attendance/check-in/
{
  "date": "2025-12-01",  # Optional, defaults to today
  "notes": "Optional notes"
}
```

### Check-out
```bash
POST /api/attendance/check-out/
{
  "date": "2025-12-01",  # Optional, defaults to today
  "notes": "Optional notes"
}
```

### Monthly Attendance
```bash
GET /api/attendance/monthly/?month=12&year=2025&userid=838
```

## Integration

- **Employee Model**: ForeignKey relationship
- **Holiday System**: Detects holidays from holidays app
- **Leave System**: Can integrate later to auto-mark absent for approved leave days

