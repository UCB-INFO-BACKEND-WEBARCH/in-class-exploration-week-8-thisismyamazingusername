"""
Notification Service API - Starter (Synchronous)

This version sends notifications SYNCHRONOUSLY.
Each request blocks for 3 seconds while "sending" the notification.

YOUR TASK: Convert this to use rq for background processing!
"""

import os

from flask import Flask, jsonify, request
import time
import uuid
from datetime import datetime
from redis import Redis
from tasks import send_notification
from rq.job import Job

app = Flask(__name__)

# In-memory store for notifications
notifications = {}

# Connect to Redis
redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

def send_notification_sync(notification_id, email, message):
    """
    Send a notification (SLOW - blocks for 3 seconds!)

    In production, this would call an email service like Mailgun.
    We simulate the slow API with time.sleep().
    """
    print(f"[Sending] Notification {notification_id} to {email}...")

    # This is the problem - blocking for 3 seconds!
    time.sleep(3)

    sent_at = datetime.utcnow().isoformat() + "Z"
    print(f"[Sent] Notification {notification_id} at {sent_at}")

    return {
        "notification_id": notification_id,
        "email": email,
        "status": "sent",
        "sent_at": sent_at
    }


@app.route('/')
def index():
    return jsonify({
        "service": "Notification Service (Synchronous - SLOW!)",
        "endpoints": {
            "POST /notifications": "Send a notification (takes 3 seconds!)",
            "GET /notifications": "List all notifications",
            "GET /notifications/<id>": "Get a notification"
        }
    })


@app.route('/notifications', methods=['POST'])
def create_notification():
    """
    Send a notification.

    WARNING: This blocks for 3 seconds!
    The user has to wait while we "send" the notification.

    TODO: Convert this to use rq for background processing!

    Modify `app.py` to use rq with the `.delay()` pattern:

    | Step | Code Pattern |
    |------|--------------|
    | Import Redis | `from redis import Redis` |
    | Import task | `from tasks import send_notification` |
    | Connect to Redis | `redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))` |
    | Queue task with .delay() | `job = send_notification.delay(id, email, message)` |
    | Return job ID | Return `{"job_id": job.id}` with status `202` |

    **Key insight**: The `@job` decorator adds a `.delay()` method to your function:
    - `send_notification(id, email, msg)` → runs **NOW** (blocks for 3 seconds!)
    - `send_notification.delay(id, email, msg)` → queues to run **LATER** (returns instantly!)

    """
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400

    # Create notification record
    notification_id = str(uuid.uuid4())
    email = data['email']
    message = data.get('message', 'You have a new notification!')

    # THIS IS THE PROBLEM: We block here for 3 seconds!
    job = send_notification.delay(notification_id, email, message)

    # The user can't do anything while we wait.
    # result = send_notification_sync(notification_id, email, message)

    notification = {
        "id": notification_id,
        "email": email,
        "message": message,
        "status": "queued",
        "sent_at": None
    }
    notifications[notification_id] = notification

    return jsonify({"job_id": job.id}), 202


@app.route('/notifications', methods=['GET'])
def list_notifications():
    """List all notifications."""
    return jsonify({
        "notifications": list(notifications.values())
    })


@app.route('/notifications/<notification_id>', methods=['GET'])
def get_notification(notification_id):
    """Get a single notification."""
    notification = notifications.get(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify(notification)



# Add `GET /jobs/<job_id>` to check job status:
# | Step | Code Pattern |
# |------|--------------|
# | Import Job | `from rq.job import Job` |
# | Fetch job | `job = Job.fetch(job_id, connection=redis_conn)` |
# | Get status | `job.get_status()` returns "queued", "started", "finished", "failed" |
# | Get result | `job.result` (available when finished) |

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get the status of a background job."""

    try:
        # Fetch the job from Redis
        job = Job.fetch(job_id, connection=redis_conn)
        # Get status
        status = job.get_status()
        # Get result
        result = job.result if status == 'finished' else None
        return jsonify({
            "job_id": job_id,
            "status": status,
            "result": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5858, debug=True)
