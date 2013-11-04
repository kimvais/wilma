#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2013 Kimmo Parviainen-Jalanko
#
# Licensed under MIT License, see LICENSE for details.
#

from email.mime.text import MIMEText
from email.utils import formatdate, formataddr
import logging
import smtplib
import bs4
from dateutil.parser import parse
import requests
import sys

logger = logging.getLogger(__name__)


def send_email(message, rcpt, sender, subject, timestamp, user):
    msg = MIMEText(message, _charset="utf-8")
    msg['Subject'] = '[{}] {}'.format(user, subject)
    msg['From'] = formataddr((sender, 'wilma-mailer@77.fi'))
    msg['To'] = rcpt
    msg['Date'] = formatdate(int(timestamp.strftime('%s')))
    s = smtplib.SMTP(settings.SMTP)
    s.send_message(msg)
    s.quit()


def fetch(conf, user, send_mail=True):
    session = requests.Session()
    req = session.get(conf.BASEURL)
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    frontpage = bs4.BeautifulSoup(req.text)
    session_id = frontpage.find('input', attrs=dict(name='SESSIONID')).attrs[
        'value']
    logger.debug("session id: {0}".format(session_id))
    logindata = dict(SESSIONID=session_id,
                     Login=conf.USERS[user]['username'],
                     Password=conf.USERS[user]['password'])
    req = session.post(conf.BASEURL + '/login', logindata)
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    req = session.get(conf.BASEURL + '/messages')
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    messages = bs4.BeautifulSoup(req.text)
    for message_link in messages.find_all('a', attrs={'class': 'fitt'}):
        message_id = message_link.attrs['href'].rsplit('/', 1)[-1]

        try:
            with open('data/{0}_{1}.txt'.format(user, message_id)):
                pass
        except (OSError):
            with open('data/{0}_{1}.txt'.format(user, message_id), 'wb') as f:
                req = session.get(conf.BASEURL +
                                  '/messages/{0}'.format(message_id))
                logger.info('{0} - {1}'.format(req.url, req.status_code))
                soup = bs4.BeautifulSoup(req.text)
                msg = soup.find('div', attrs={'class': 'columns-left-inner'})
                subject = soup.find('h1', attrs={'class': 'safeflow'}).text
                try:
                    sender, recipient, timestamp = (x.text for x in
                                                    msg.find_all('td')[:3])
                except ValueError:
                    logger.warning(msg.find_all('td'))
                else:
                    timestamp = parse(
                        timestamp.replace(' klo ', ' at '))
                    message_body = '\n\n'.join(x.text for x in msg.find_all('p'))
                    message = '** {} - {} **\n\n{}'.format(
                        user,
                        timestamp.isoformat(),
                        message_body)
                    f.write(subject.encode('utf-8') + b'\n')
                    f.write(sender.encode('utf-8') + b'\n')
                    f.write(recipient.encode('utf-8') + b'\n')
                    f.write(timestamp.isoformat().encode('utf-8') + b'\n')
                    f.write(message.encode('utf-8') + b'\n')

                    # Mail
                    if send_mail:
                        rcpt = conf.RECIPIENT
                        send_email(message, rcpt, sender, subject, timestamp,
                                   user)
                    else:
                        logger.info("Not sending e-mail")


    # Log out
    session.post(conf.BASEURL + '/logout', dict(loginbtn="Kirjaudu ulos"))


if __name__ == "__main__":
    import settings
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    for user in settings.USERS.keys():
        send_mail = len(sys.argv) < 2
        fetch(settings, user, send_mail)

