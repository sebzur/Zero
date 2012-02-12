from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

import datetime
from django.db.models import get_model


def send_notification(instance, created):
    if hasattr(instance, 'get_subscribers'):
        subject = "ZERO has has saved instance! Action date: %s" % datetime.datetime.now().strftime("%d %b %Y")
        ct = get_model('contenttypes','contenttype').objects.get_for_model(instance)    
        tpl = "zero/notify/%s.html" % ct.model
        site = get_model('sites', 'Site').objects.get_current()
        body = render_to_string(tpl, {'instance': instance, 'created': created, 'site': site})
        email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, instance.get_subscribers())
        # email.content_subtype = "html"
        # email.attach_file(bkp_path)

        #if not settings.DEBUG:
        email.send()
