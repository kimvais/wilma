import logging
import bs4
import requests

logger = logging.getLogger(__name__)

def main(conf, user):
    session = requests.Session()
    req = session.get(conf.BASEURL)
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    frontpage = bs4.BeautifulSoup(req.text)
    session_id = frontpage.find('input', attrs=dict(name='SESSIONID')).attrs['value']
    logger.debug("session id: {0}".format(session_id))
    logindata = dict(SESSIONID=session_id,
            Login=conf.USERS[user]['username'],
            Password=conf.USERS[user]['password'])
    req = session.post(conf.BASEURL + '/login', logindata)
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    req = session.get(conf.BASEURL + '/messages')
    logger.info('{0} - {1}'.format(req.url, req.status_code))
    messages = bs4.BeautifulSoup(req.text)
    for message_link in messages.find_all('a', attrs={'class':'fitt'}):
        message_id = message_link.attrs['href'].rsplit('/',1)[-1]
        req = session.get(conf.BASEURL +
                '/messages/{0}'.format(message_id))
        logger.info('{0} - {1}'.format(req.url, req.status_code))
        msg = bs4.BeautifulSoup(req.text).find('div',
                attrs={'class':'columns-left-inner'})
        message = '\n\n'.join(x.text for x in msg.find_all('p'))
        try:
            sender, recipient, timestamp = (x.text for x in msg.find_all('td')[:3])
        except ValueError:
            logger.warning(msg.find_all('td'))

        try:
            with open('data/{0}_{1}.txt'.format(user, message_id)) as f:
                pass
        except IOError:
            with open('data/{0}_{1}.txt'.format(user, message_id), 'w') as f:
                f.write(sender.encode('utf-8') + '\n')
                f.write(recipient.encode('utf-8')+ '\n')
                f.write(timestamp + '\n')
                f.write(message.encode('utf-8') + '\n')

    # Log out
    session.post(conf.BASEURL + '/logout', dict(loginbtn="Kirjaudu ulos"))

if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    import settings
    logger.debug("Calling main")
    main(settings, 'Elias')

