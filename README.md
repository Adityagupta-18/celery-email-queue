# Celery Email Queue

A Django-based project demonstrating asynchronous email processing using **Celery and Redis**. It explores background task execution, task status tracking, automatic retries, and periodic task scheduling with Celery Beat.

The project was built to understand how background job processing works in real-world Django applications.

## Features

- **Asynchronous Email Sending:** Queue email tasks from Django without making users wait for the entire operation.
- **Redis Message Broker:** Uses Redis to queue tasks before they are consumed by Celery workers.
- **Celery Worker:** Executes background email tasks independently of Django's request-response cycle.
- **Result Backend:** Stores task execution states and returned results in Redis.
- **Task Status Tracking:** Retrieve task status using a unique task ID.
- **Live Status Updates:** JavaScript polling automatically updates the task status on the success page.
- **Failure Handling:** Handles selected SMTP and network-related exceptions.
- **Automatic Retries:** Retries failed tasks up to three times with a configurable delay.
- **Celery Beat:** Demonstrates periodic task scheduling, including recurring email tasks.
- **Gmail SMTP Integration:** Uses Gmail SMTP for email processing.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Django | Web framework |
| Celery | Background task processing |
| Redis | Message broker and result backend |
| JavaScript | Live task status polling |
| HTML | Application templates |
| Gmail SMTP | Email service |
| Docker | Running Redis locally |

## Architecture

The project uses Redis for two separate purposes: task messaging and task result storage.

```text
                 User / Browser
                       |
                       v
                 Django Application
                       |
                 .delay() method
                       |
                       v
                 Redis (DB 0)
                  Task Broker
                       |
                       v
                 Celery Worker
                       |
                       v
                  Gmail SMTP
                       |
                       v
                 Email Processing


              Task Execution Status
                       |
                       v
                 Redis (DB 1)
                 Result Backend
                       |
                       v
              Django Status Endpoint
                       |
                       v
                JavaScript Polling
                       |
                       v
               Updated Browser UI


                 Celery Beat
                       |
             Scheduled Task Messages
                       |
                       v
                  Redis (DB 0)
```

### Component Responsibilities

- **Django:** Handles user requests and queues background tasks.
- **Redis DB 0:** Acts as the Celery message broker.
- **Celery Worker:** Retrieves and executes queued tasks.
- **Redis DB 1:** Stores task states and results.
- **Celery Beat:** Schedules periodic tasks and sends them to the broker.
- **JavaScript:** Periodically requests task status from Django and updates the interface.

## Project Structure

```text
celery-email-queue/
│
├── config/
│   ├── __init__.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── emails/
│   ├── migrations/
│   ├── templates/
│   ├── tasks.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── templates/
│   ├── home.html
│   └── success.html
│
├── manage.py
├── .env
├── .gitignore
└── requirements file
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Adityagupta-18/celery-email-queue.git

cd celery-email-queue
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key

EMAIL_HOST_USER=your-gmail-address@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
```

**Gmail configuration:**

- Use a Gmail App Password instead of your normal Gmail password.
- Configure the Gmail account appropriately for App Password access.
- Never commit your `.env` file or expose your credentials.

### 5. Start Redis

Redis is used as the broker and result backend.

This project uses a Redis Docker container for local development.

Make sure the Redis container is running and port `6379` is accessible from your development environment.

Verify the Redis connection:

```bash
docker ps
```

Test Redis:

```bash
docker exec -it <redis-container-name> redis-cli ping
```

Expected response:

```text
PONG
```

### 6. Run database migrations

```bash
python manage.py migrate
```

### 7. Start the Django development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Running Celery

Celery runs independently of the Django development server.

Open a separate terminal, activate the virtual environment, and execute:

```bash
celery -A config worker --loglevel=info --concurrency=1
```

The worker listens for tasks from Redis and executes them in the background.

### Concurrency

The worker is configured with concurrency `1`, meaning it has one task execution slot.

## Task Processing Workflow

When a user clicks the **Send Emails** button:

1. Django receives the POST request.
2. Django calls `.delay()` to queue the email task.
3. Redis stores the task message.
4. Django immediately returns the success page.
5. The Celery worker retrieves and executes the task.
6. The result backend stores the task's execution status and result.

Example:

```python
task = send_welcome_emails.delay()
```

The task ID can be retrieved using:

```python
task.id
```

## Task Status Tracking

Every queued task receives a unique task ID.

The project uses Celery's `AsyncResult` to retrieve information about task execution.

The status endpoint is:

```text
/task-status/<task_id>/
```

Example JSON response:

```json
{
    "task_id": "003b0ca7-99b0-414d-a448-d2bd2554566f",
    "state": "SUCCESS",
    "result": 9
}
```

### Supported Task States

| State | Description |
|---|---|
| PENDING | Task is waiting or its state is not known to the backend |
| STARTED | Task execution has started |
| RETRY | Task has been scheduled for another attempt |
| SUCCESS | Task completed successfully |
| FAILURE | Task failed after an unrecovered error |
| REVOKED | Task was revoked |

The project enables started-state tracking through:

```python
CELERY_TASK_TRACK_STARTED = True
```

### JavaScript Polling

The success page uses JavaScript `fetch()` to request the task status every two seconds.

The page automatically updates when the task moves between states and stops polling when it reaches `SUCCESS` or `FAILURE`.

## Failure Handling and Automatic Retries

Background tasks can fail because of temporary SMTP errors, network interruptions, or unavailable external services.

The project implements Celery's retry mechanism.

Example configuration:

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
```

The task uses:

```python
self.retry(exc=exc)
```

### Retry Behaviour

- Maximum retries: 3
- Initial execution: 1
- Maximum total executions: 4
- Default retry delay: 10 seconds

The task also preserves its progress when retrying, allowing it to resume from the failed recipient instead of restarting the entire email batch.

The project tests both outcomes:

- A temporary failure followed by a successful retry.
- Repeated failures that eventually result in the `FAILURE` state.

**Note:** SMTP acceptance does not guarantee final inbox delivery. Production email systems also need careful handling of duplicate messages and permanent errors.

## Celery Beat — Periodic Task Scheduling

Celery Beat is used to schedule tasks that should execute automatically at specific times or recurring intervals.

Unlike manually triggered tasks, periodic tasks do not require a user to click a button.

### Running Celery Beat

Open another terminal and execute:

```bash
celery -A config beat --loglevel=info
```

Celery Beat checks the configured schedule and sends due tasks to Redis. The Celery worker then executes them.

### Example: Schedule a Task Every Minute

Add the following to `config/settings.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-test-emails-every-minute': {
        'task': 'emails.tasks.send_welcome_emails',
        'schedule': crontab(minute='*'),
    },
}
```

### Example: Schedule a Task Every Day at 9 AM

```python
CELERY_BEAT_SCHEDULE = {
    'send-daily-emails': {
        'task': 'emails.tasks.send_welcome_emails',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

The project uses:

```python
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_ENABLE_UTC = True
```

Therefore, the example schedule runs at 9:00 AM Indian Standard Time.

**Note:** These are optional scheduling examples. No periodic schedule is enabled by default in the current project. Before enabling one, configure an appropriate recurring email task and recipient list.

Only one Celery Beat scheduler instance should manage a given schedule in this setup.

## Running All Services Together

For local development, the following processes run separately:

| Terminal | Command | Responsibility |
|---|---|---|
| Redis | Docker container | Broker and result backend |
| Terminal 1 | `python manage.py runserver` | Django application |
| Terminal 2 | `celery -A config worker --loglevel=info --concurrency=1` | Background task execution |
| Terminal 3 | `celery -A config beat --loglevel=info` | Periodic task scheduling (only when enabled) |

Celery Beat can remain stopped when no periodic tasks are configured.

## Important Notes

- The current recipient list uses `example.com` placeholder addresses. Replace them with actual recipient addresses to test real email delivery.
- The result backend stores task information separately from the broker.
- Task results are subject to Celery's result-expiration configuration.
- The local Beat scheduler generates a `celerybeat-schedule` file to maintain scheduling state. This runtime file should not be committed to Git.
- The project is an educational implementation and is not yet hardened for production use. Production deployments should include authenticated task-status access, secure secret management, monitoring, idempotency, and appropriate error handling.

## Learning Outcomes

Through this project, I implemented and explored:

- Asynchronous task processing with Django and Celery.
- Redis as a message broker and result backend.
- Celery worker configuration and concurrency.
- Task IDs, states, and result retrieval.
- JavaScript polling for live task status updates.
- Task failure handling and automatic retries.
- Periodic task scheduling using Celery Beat.
- Integration of external SMTP services with background tasks.

---

**Project:** Celery Email Queue  
**Repository:** [Adityagupta-18/celery-email-queue](https://github.com/Adityagupta-18/celery-email-queue)