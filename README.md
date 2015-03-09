# wilmailer

This tool can log on to StarSoft Wilma parents'/guardians' Web interface programmatically and send the wilma messages as e-mail.

Tested and developed against version ~~2.15c~~ 2.18d used by City of Espoo. 



## Installation

### Requirements
Requires on Python3.x (tested with 3.2.3 and 3.4.0a4). See `requirements.txt`
for 3rd party module requirements.

### Step-by-step instructions
1. git clone
1. `pip install -r requirements.txt`
2. edit `settings.py`, see `settings.py.sample`
3. add something like this to your crontab: `*/15 * * * *    /srv/wilma/wilma.py &>/tmp/wilma.log`

