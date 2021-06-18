
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

import requests
from dateutil import parser
from datetime import datetime
import pandas as pd

import configparser
config = configparser.ConfigParser()
config.read('main.ini')
apikey = config.get('default', 'apikey')
sonarrurl = config.get('default', 'sonarrurl')
daysToAllow = int(config.get('default', 'daysToAllow'))

def main():
    now = pd.Timestamp.utcnow()
    queueresponse = requests.get(sonarrurl + '/api/queue?apikey=' + apikey).json()
    logger.info('Total number of requests in the queue: ' + str(len(queueresponse)))

    for queue in range(0, len(queueresponse) -1):
        logger.debug ('queue: ' + str(queue))
        logger.debug (queueresponse[queue]['series']['title'] + ' ' + str(queueresponse[queue]['id']) + str(queueresponse[queue]['episode']['title']) + ' ' + str(queueresponse[queue]['episode']['id'])+ ' ' + str(queueresponse[queue]['episode']['seasonNumber']) + ' ' + str(queueresponse[queue]['episode']['episodeNumber']))
        episodeId = queueresponse[queue]['episode']['id']
        response = requests.get(sonarrurl + '/api/history/?apikey=' + apikey + '&sortkey=date&sortdir=des&episodeId=' + str(episodeId)).json()
        logger.debug (response['records'][0]['date'])
        parsed_date = pd.to_datetime(response ['records'][0]['date'])
        subtracted = (now - parsed_date)
        logger.debug ('subtracted: ' + str(subtracted.days ))

        if (subtracted.days > daysToAllow):
            blresponse = requests.delete(sonarrurl + '/api/queue/' +  str(queueresponse[queue]['id']) + '?apikey=' + apikey + '&blacklist=true')
            logger.debug (blresponse.url)
            logger.debug (blresponse.status_code)
            logger.debug (blresponse.text)

if __name__ == '__main__':
    main()
