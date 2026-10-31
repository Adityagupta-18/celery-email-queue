from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def home(request):
    return render(request,'home.html')



def mail_sent(request):
    recipients = [  # Your actual Gmail
        'user1@example.com',
        'user2@example.com',
        'user3@example.com',
        'user4@example.com',
        'user5@example.com',
        'user6@example.com',
        'user7@example.com',
        'user8@example.com',
        'aditya.work018@gmail.com',
    ]

    count = 0

    for email in recipients:
        send_mail(
            subject='Welcome!',
            message='Welcome to our Celery Email Demo project!',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )
        count += 1

    return render(request, 'success.html', {'count': count})