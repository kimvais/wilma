#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2014 Kimmo Parviainen-Jalanko
#
# Licensed under MIT License, see LICENSE for details.
#
import json

import logging
from pprint import pformat

import bs4
from dateutil.parser import parse
import requests
import settings

logger = logging.getLogger(__name__)


def fetch(credentials):
    session = requests.Session()
    logger.debug(session.get('https://oma.muksunkirja.fi/perusmuxu/login'))
    credentials.update(dict(next='/perusmuxu/', submit='Login'))
    login = session.post('https://oma.muksunkirja.fi/perusmuxu/login/', credentials)
    logger.debug(login)
    soup = bs4.BeautifulSoup(login.text)
    # This is a hack, but this way we don't have to parse JavaScript
    kid_id = int(soup.find('div', attrs={'class': 'caption'}).attrs['id'].rsplit('_', 1)[1])
    kid_data = json.loads(session.get('https://oma.muksunkirja.fi/json/kid/{0:d}'.format(kid_id)).text)
    logger.debug(kid_data)
    dep_id = kid_data['department']['id']
    logger.debug(dep_id)

    # Load the news feed
    feed_data = json.loads(
        session.get('https://oma.muksunkirja.fi/json/daycarefeed/{0}/?filter=all&idx=0'.format(dep_id)).text)
    logger.info(pformat(feed_data['entries']))
    for entry in feed_data['entries']:
        msg_id = entry['id']
        timestamp = parse(entry['time'])
        message = entry['message']
        sender = entry['user']['name']
        # XXX: Process.

    # XXX: Fetch messages too

    logger.debug(session.get('https://oma.muksunkirja.fi/perusmuxu/logout/'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    fetch(settings.MUXU_CREDS)

