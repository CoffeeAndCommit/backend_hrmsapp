# 🏖️ Leave Management System - API Documentation

This documentation provides a detailed guide to all Leave-related APIs, including sample request and response structures.

---

## �️ Authentication
**Endpoint:** `POST /auth/login/`

**Request Body:**
```json
{
  "username": "medha",
  "password": "password123"
}
```
**Response:** `200 OK`
```json
{
  "refresh": "eyJ0eXAi...",
  "access": "eyJ0eXAi...",
  "is_first_login": false
}
```
*Note: Include the `access` token in all subsequent headers: `Authorization: Bearer <token>`*

---

## � Balance APIs

### 1. Get All Leave Balances
**Endpoint:** `GET /api/leaves/balance/`

**Detailed Response:**
```json
{
  "error": 0,
  "data": {
    "Casual Leave": {
      "allocated": 12.0,
      "used": 3.0,
      "pending": 0.0,
      "available": 9.0,
      "carried_forward": 0.0
    },
    "Sick Leave": {
      "allocated": 10.0,
      "used": 0.0,
      "pending": 0.0,
      "available": 10.0,
      "carried_forward": 0.0
    },
    "rh": {
      "allocated": 2,
      "used": 1,
      "available": 1
    }
  }
}
```

### 2. Get Restricted Holiday (RH) Balance Only
**Endpoint:** `GET /api/leaves/rh-balance/`

**Detailed Response:**
```json
{
  "error": 0,
  "data": {
    "rh_allocated": 2,
    "rh_used": 1,
    "rh_available": 1
  }
}
```

---

## 📅 Utility APIs

### 3. Calculate Working Days
**Endpoint:** `POST /api/leaves/calculate-days/`

**Request Body:**
```json
{
  "start_date": "2026-01-12",
  "end_date": "2026-01-14"
}
```

**Detailed Response:**
```json
{
  "error": 0,
  "data": {
    "start_date": "2026-01-12",
    "end_date": "2026-01-14",
    "working_days": 3,
    "holidays": 0,
    "weekends": 0,
    "days": [
      {
        "type": "working",
        "sub_type": "",
        "sub_sub_type": "",
        "full_date": "2026-01-12"
      },
      {
        "type": "working",
        "sub_type": "",
        "sub_sub_type": "",
        "full_date": "2026-01-13"
      },
      {
        "type": "working",
        "sub_type": "",
        "sub_sub_type": "",
        "full_date": "2026-01-14"
      }
    ],
    "message": ""
  }
}
```

---

## 🏖️ Leave Application APIs

### 4. Submit Leave Request
**Endpoint:** `POST /api/leaves/submit-leave/`

**Request Body (Normal Leave):**
```json
{
  "from_date": "2026-01-12",
  "to_date": "2026-01-12",
  "no_of_days": 1.0,
  "reason": "Personal work",
  "leave_type": "Casual Leave"
}
```

**Request Body (Restricted Holiday):**
```json
{
  "from_date": "2026-01-14",
  "to_date": "2026-01-14",
  "no_of_days": 1.0,
  "reason": "Festival",
  "leave_type": "Restricted Holiday",
  "rh_id": 1
}
```

**Detailed Response:**
```json
{
  "error": 0,
  "data": {
    "message": "Leave applied successfully.",
    "leave_id": 42,
    "status": "Pending",
    "is_restricted": true
  }
}
```

---

## 📜 History & Management

### 5. List My Leaves / History
**Endpoint:** `GET /api/leaves/`

**Detailed Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "from_date": "2026-01-14",
      "to_date": "2026-01-14",
      "no_of_days": 1.0,
      "reason": "Festival",
      "leave_type": "Restricted Holiday",
      "is_restricted": true,
      "status": "Pending",
      "day_status": null,
      "late_reason": null,
      "doc_link": null,
      "doc_link_url": null,
      "rejection_reason": null,
      "rh_dates": [],
      "created_at": "2026-01-05T12:00:00.000000+05:30",
      "restricted_holiday": 1
    }
  ]
}
```

### 6. Update Status (Approve/Reject/Cancel)
**Endpoint:** `PATCH /api/leaves/{id}/`

**Request Body (Admin Approve):**
```json
{ "status": "Approved" }
```

**Request Body (Admin Reject):**
```json
{ 
  "status": "Rejected", 
  "rejection_reason": "Insufficient coverage for the team." 
}
```

**Request Body (User Cancel):**
```json
{ "status": "Cancelled" }
```

**Detailed Response:**
```json
{
  "id": 42,
  "from_date": "2026-01-14",
  "to_date": "2026-01-14",
  "no_of_days": 1.0,
  "reason": "Festival",
  "leave_type": "Restricted Holiday",
  "is_restricted": true,
  "status": "Approved",
  "day_status": null,
  "late_reason": null,
  "doc_link": null,
  "doc_link_url": null,
  "rejection_reason": null,
  "rh_dates": [],
  "created_at": "2026-01-05T12:00:00.000000+05:30",
  "restricted_holiday": 1
}
```
