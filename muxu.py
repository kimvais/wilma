#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2014 Kimmo Parviainen-Jalanko
#
# Licensed under MIT License, see LICENSE for details.
#
import json

import logging
import os

import bs4
from dateutil.parser import parse
import requests
import re
from mail import send_email
import settings

logger = logging.getLogger(__name__)


def fetch(credentials):
    session = requests.Session()
    baseurl = 'https://oma.muksunkirja.fi/'
    logger.debug(session.get('{0:s}perusmuxu/login'.format(baseurl)))
    credentials.update(dict(next='/perusmuxu/', submit='Login'))
    login = session.post('{0:s}perusmuxu/login/'.format(baseurl), credentials)
    logger.debug(login)
    soup = bs4.BeautifulSoup(login.text)
    # This is a hack, but this way we don't have to parse JavaScript
    kid_id = int(soup.find('div', attrs={'class': 'caption'}).attrs['id'].rsplit('_', 1)[1])
    kid_data = json.loads(session.get('{1}json/kid/{0:d}'.format(kid_id, baseurl)).text)
    logger.debug(kid_data)
    dep_id = kid_data['department']['id']
    logger.debug(dep_id)

    # Load the news feed
    feed_data = json.loads(
        session.get('{1}json/daycarefeed/{0}/?filter=all&idx=0'.format(dep_id, baseurl)).text)
    user = 'muksu'  # XXX
    for entry in feed_data['entries']:
        raw_html_message = entry['message']
        sender = entry['user']['name']
        # XXX: Process.
        filename = os.path.join(settings.DATAPATH,
                                '{0}_{1}.json'.format(user, entry['id']))
        try:
            with open(filename):
                continue  # No need to overwrite
        except (OSError, IOError):
            with open(filename, 'w') as f:
                entry_as_json = json.dumps(entry)
                logger.info("Writing entry: {}".format(entry_as_json))
                f.write(entry_as_json)
                send_mail = True  # XXX
                parsed_message = bs4.BeautifulSoup(raw_html_message).text
                logger.debug(parsed_message)
                timestamp = parse(entry['time'])
                try:
                    subject, message = parsed_message.split('\n', 1)
                except ValueError:
                    # Just a single line message.
                    message = parsed_message
                    subject = parsed_message[:re.search(r'[.!?]', parsed_message).end()]  # Split by punctuation

                body = '** {} - {} **\n\n{}'.format(
                        user,
                        timestamp.isoformat(),
                        message)
                if send_mail:
                    rcpt = settings.RECIPIENT
                    send_email(body, rcpt, sender, subject, parse(entry['time']),
                               user)
                else:
                    logger.info("Not sending e-mail")

    # XXX: Fetch messages too

    logger.debug(session.get('{0:s}perusmuxu/logout/'.format(baseurl)))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    fetch(settings.MUXU_CREDS)

