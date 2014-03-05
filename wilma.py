#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2013 Kimmo Parviainen-Jalanko
#
# Licensed under MIT License, see LICENSE for details.
#

import logging
import os
import sys

import bs4
from dateutil.parser import parse
import requests
from mail import send_email


logger = logging.getLogger(__name__)


def fetch(conf, send_mail=True):
    credentials = settings.WILMA_CREDENTIALS
    session = requests.Session()
    baseurl = credentials['url']
    req = session.get(baseurl)
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    frontpage = bs4.BeautifulSoup(req.text)
    session_id = frontpage.find('input', attrs=dict(name='SESSIONID')).attrs[
        'value']
    logger.debug("session id: {0}".format(session_id))
    logindata = dict(SESSIONID=session_id,
                     Login=credentials['username'],
                     Password=credentials['password'])
    req = session.post(baseurl + '/login', logindata)
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    role_selection_page = bs4.BeautifulSoup(req.text)
    logger.debug(role_selection_page.find('div', attrs={'class': 'sidebar-related'}).find_all('a'))
    pupils = dict((a.text, a.attrs['href']) for a in role_selection_page.find('div', attrs={'class': 'sidebar-related'}).find_all('a') if a.attrs['href'].startswith('/!'))
    for name, pupil_link in pupils.items():
        req = session.get('{}{}/messages'.format(baseurl, pupil_link))
        logger.info('{0} - {1}'.format(req.url, req.status_code))
        messages = bs4.BeautifulSoup(req.text)
        for message_link in messages.find_all('a', attrs={'class': 'fitt'}):
            message_id = message_link.attrs['href'].rsplit('/', 1)[-1]

            filename = os.path.join(settings.DATAPATH,
                                    '{0}_{1}.txt'.format(name, message_id))
            try:
                with open(filename):
                    pass
            except (OSError, IOError):
                with open(filename, 'wb') as f:
                    req = session.get('{}{}/messages/{}'.format(baseurl, pupil_link, message_id))
                    logger.info('{0} - {1}'.format(req.url, req.status_code))
                    if req.status_code > 399:
                        logger.error("{} failed with {}".format(req.url, req.status_code))
                        logger.debug(req.text)
                        continue
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
                        message_body = '\n\n'.join(
                            x.text for x in msg.find_all('p'))
                        message = '** {} - {} **\n\n{}'.format(
                            name,
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
                                       name)
                        else:
                            logger.info("Not sending e-mail")


    # Log out
    session.post(baseurl + '/logout', dict(loginbtn="Kirjaudu ulos"))


if __name__ == "__main__":
    import settings

    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    send_mail = len(sys.argv) < 2
    fetch(settings, send_mail)

