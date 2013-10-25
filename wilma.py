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
    print messages

    # Log out
    session.post(conf.BASEURL + '/logout', dict(loginbtn="Kirjaudu ulos"))

if __name__ == "__main__":
    import settings
    main(settings, 'Elias')

