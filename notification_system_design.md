# Campus Notifications Microservice Architecture Design

---

## Stage 1: REST API Design & Contracts

### 1. Core Endpoints & API Data Structures

```json
{
  "apiDesign": {
    "sendNotification": {
      "endpoint": "POST /api/v1/notifications",
      "requestExample": {
        "senderId": "550e8400-e29b-41d4-a716-446655440000",
        "targetGroup": "ALL_STUDENTS",
        "notificationType": "Result",
        "message": "Mid-sem results are published.",
        "metadata": {
          "department": "CSE",
          "priority": "HIGH"
        }
      },
      "fieldDescription": {
        "senderId": "UUID of the sender (admin/faculty)",
        "targetGroup": "ALL_STUDENTS | BTECH_ONLY | DEPT_SPECIFIC",
        "notificationType": "Event | Result | Placement",
        "message": "Notification text (max 250 characters)",
        "metadata": {
          "department": "Department name (e.g., CSE, ECE)",
          "priority": "HIGH | MEDIUM | LOW"
        }
      },
      "successResponseExample": {
        "status": "success",
        "notificationId": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "dispatchedAt": "2026-06-05T10:45:00Z"
      }
    },
    "fetchUnreadNotifications": {
      "endpoint": "GET /api/v1/students/{studentId}/notifications/unread",
      "responseExample": {
        "studentId": "23BQ1A4908",
        "unreadCount": 1,
        "notifications": [
          {
            "notificationId": "cf2885a6-45ac-4ba8-b548-6e9e9d4c52c8",
            "type": "Result",
            "message": "Mid-sem results published.",
            "timestamp": "2026-06-05T08:00:00Z"
          }
        ]
      }
    },
    "markAsRead": {
      "endpoint": "PATCH /api/v1/students/{studentId}/notifications/{notificationId}/read",
      "responseExample": {
        "status": "updated",
        "notificationId": "cf2885a6-45ac-4ba8-b548-6e9e9d4c52c8",
        "isRead": true
      }
    }
  }
}
```
---

## Stage 2: Persistent Storage Strategy

### 1. Database Schema Design

```sql
CREATE TYPE notification_enum AS ENUM ('Event', 'Result', 'Placement');

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL,
    notification_type notification_enum NOT NULL,
    message VARCHAR(250) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_notification_states (
    student_id VARCHAR(50) NOT NULL,
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, notification_id)
);
CREATE INDEX idx_student_unread_lookup 
ON student_notification_states (student_id, is_read, updated_at DESC);
```