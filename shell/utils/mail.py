from django.core.mail import send_mail


def mail(subject, message):
    def to(recipient_list):
        send_mail(
            subject,
            message,
            'hello+support@mountainbikers.club',
            recipient_list,
            fail_silently=False,
        )

    return to
