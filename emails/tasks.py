import smtplib

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_welcome_emails(self, start_index=0, sent_count=0):

    recipients = [
        'user1@example.com',
        'user2@example.com',
        'user3@example.com',
        'user4@example.com',
        'user5@example.com',
        'user6@example.com',
        'user7@example.com',
        'user8@example.com',
        'user9@example.com',
    ]

    count = sent_count

    for index in range(start_index, len(recipients)):
        try:
            # Delibrately did first wrong to generate a exaception and initiate retry

            # if index == 0 and self.request.retries == 0:
            #     raise smtplib.SMTPServerDisconnected(
            #         "Simulated temporary SMTP failure"
            #     )
            
            send_mail(
                subject='Welcome!',
                message='Welcome to our Celery Email Demo project!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipients[index]],
                fail_silently=False
            )

            count += 1

        except (smtplib.SMTPException, OSError) as exc:
            raise self.retry(
                args=(index, count),
                exc=exc
            )

    return count