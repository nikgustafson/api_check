import requests
import logging
from requests import codes

logger = logging.getLogger(__name__)


def check_env(input):
     logger.info(__name__)
 #"Environment":"prod","Version":"1.0.73.889","Branch":"default","Commit":"ed55689508097909378cc244f5d020a3312d112d","CommitDate":"2018-03-21T22:18:13+00:00","BuildDate":"2018-03-21T16:05:51+00:00 
     d = requests.get('https://'+input+'.ordercloud.io/env')
     logger.debug(d.status_code)
     logger.debug(d.url)
     logger.debug(d.json())
     assert d.status_code is codes.ok
     return(d)




#logger = logging.getLogger(__name__).getChild()