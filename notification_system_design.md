# Campus Notifications Microservice Architecture Design

---

## Stage 1: REST API Design & Contracts

### 1. Core Action Endpoints

#### A. Send Notification
* **Endpoint:** `POST /api/v1/notifications`
* **Description:** Dispatches real-time placement, event, or exam results telemetry notices to targeted student lists.
* **Payload Structure (JSON):**
```json
{
  "senderId": "string (uuid)",
  "targetGroup": "enum (ALL_STUDENTS, BTECH_ONLY, DEPT_SPECIFIC)",
  "notificationType": "enum (Event, Result, Placement)",
  "message": "string (max 250 chars)",
  "metadata": {
    "department": "string",
    "priority": "enum (HIGH, MEDIUM, LOW)"
  }
}# Notification System Architecture Design
