
### Task 1: Create `tasks.py` (10 min)
# Create a new file `tasks.py` with a background task function using the `@job` decorator:

from datetime import datetime
import time

from rq.decorators import job
from redis import Redis
import os

redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))


# **Key insight**: The `@job` decorator works just like Flask's `@app.route`:
# - `@app.route('/path')` → function handles HTTP requests **NOW**
# - `@job('queue_name')` → function handles queue jobs **LATER**

# | `send_notification` | `notification_id`, `email`, `message` | Sleep 3 seconds, return result dict |


@job('notifications', connection=redis_conn)
def send_notification(notification_id, email, message):
    # The function should:
    # - Print a message when starting
    print(f"[TASK] Sending Notification {notification_id} to {email}...")
    # - Sleep for 3 seconds (simulating slow email API)
    time.sleep(3)
    # - Print a message when done
    print(f"[TASK] Sent Notification {notification_id} to {email}")
    # - Return a dict with `notification_id`, `email`, `status`, `sent_at`
    return {
        "notification_id": notification_id,
        "email": email,
        "status": "sent",
        "sent_at": datetime.utcnow().isoformat() + "Z"
    }

    
