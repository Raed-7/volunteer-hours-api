# Volunteer Hours API Documentation

## Base URL
`http://127.0.0.1:8000`

## Authentication
- Register: `POST /auth/register`
- Login: `POST /auth/login`
- Use JWT bearer token for all non-auth endpoints.

## Core Endpoints
- Volunteers CRUD: `/volunteers`
- Events CRUD: `/events`
- Shifts: `/events/{event_id}/shifts`, `/shifts/{id}`
- Attendance: `/shifts/{shift_id}/check-in`, `/shifts/{shift_id}/check-out`
- Volunteer hours: `/volunteers/{id}/hours`
- Analytics:
  - `/analytics/leaderboard`
  - `/analytics/awards`
  - `/analytics/events/{event_id}/coverage`
  - `/analytics/volunteers/{id}/reliability`
- Admin import: `/admin/import`

## Validation Rules
- Shift `end_time` must be after `start_time`.
- Cannot check out before check in.
- Cannot check in twice for same volunteer and shift.
- Check-out without prior check-in returns HTTP 400.

## OpenAPI / PDF Export
1. Run the API.
2. Open `/docs`.
3. Use browser print-to-PDF to export endpoint docs to PDF.
