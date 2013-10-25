import bs4
import requests

def main(conf, user):
    session = requests.Session()
    frontpage = bs4.BeautifulSoup(session.get(conf.BASEURL).text)
    session_id = frontpage.find('input', attrs=dict(name='SESSIONID')).attrs['value']
    logindata = dict(SESSIONID=session_id,
            Login=conf.USERS[user]['username'],
            Password=conf.USERS[user]['password'])
    _ = session.post(conf.BASEURL + '/login', logindata)
    messages_html = session.get(conf.BASEURL + '/messages').text
    messages = bs4.BeautifulSoup(messages_html)
    for message_link in messages.find_all('a', attrs={'class':'fitt'}):
        message_id = message_link.attrs['href'].rsplit('/',1)[-1]
        msg_page_html = session.get(conf.BASEURL +
                '/messages/{0}'.format(message_id)).text
        msg = bs4.BeautifulSoup(msg_page_html).find('div',
                attrs={'class':'columns-left-inner'})
        message = '\n\n'.join(x.text for x in msg.find_all('p'))
        sender, recipient, timestamp = (x.text for x in msg.find_all('td'))
        sender = sender.replace('\xa0', ' ')

        try:
            with open('data/{0}_{1}.txt'.format(user, message_id)) as f:
                pass
        except IOError:
            with open('data/{0}_{1}.txt'.format(user, message_id), 'w') as f:
                f.write(sender + '\n')
                f.write(recipient + '\n')
                f.write(timestamp + '\n')
                f.write(message + '\n')

    # Log out
    session.post(conf.BASEURL + '/logout', dict(loginbtn="Kirjaudu ulos"))

if __name__ == "__main__":
    import settings
    main(settings, 'Elias')

