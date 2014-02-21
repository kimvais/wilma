#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 SSH Communication Security Corporation.
# All rights reserved.
# This software is protected by international copyright laws.
#
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
import smtplib
import settings


def send_email(message, rcpt, sender, subject, timestamp, user):
    msg = MIMEText(message, _charset="utf-8")
    msg['Subject'] = '[{}] {}'.format(user, subject)
    msg['From'] = formataddr((sender, 'wilma-mailer@77.fi'))
    msg['To'] = rcpt
    msg['Date'] = formatdate(int(timestamp.strftime('%s')))
    s = smtplib.SMTP(settings.SMTP)
    s.send_message(msg)
    s.quit()
