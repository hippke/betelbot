import os
import requests
import numpy as np
from twython import Twython
from bs4 import BeautifulSoup
from astropy.stats import biweight_location


consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')


def tweet(text, image):
    print('Tweeting...')
    twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
    response = twitter.upload_media(media=open(image, 'rb'))
    twitter.update_status(status=text, media_ids=[response['media_id']])
    print("Done.")


def build_string(days_ago, mag):
    print('Building string...')
    data_last24hrs = np.where(days_ago<1)
    data_last1_6_days = np.where((days_ago<6) & (days_ago>1))
    n_obs_last24hrs = np.size(mag[data_last24hrs])
    n_obs_last1_6_days = np.size(mag[data_last1_6_days])
    mean_last24hrs = biweight_location(mag[data_last24hrs])
    mean_last1_6_days = biweight_location(mag[data_last1_6_days])
    stdev = np.std(mag[data_last24hrs]) / np.sqrt(n_obs_last24hrs) \
        + np.std(mag[data_last1_6_days]) / np.sqrt(n_obs_last1_6_days)
    diff = mean_last24hrs - mean_last1_6_days
    sigma = diff / stdev

    if n_obs_last24hrs < 3 or n_obs_last1_6_days < 3:
        print('Not enough observations. Abort.')
        return None
    else:

        if diff > 0:
            changeword = 'dimmer'
        else:
            changeword = 'brighter'

        mag_text = "My visual mag from last night was " + \
            str(format(mean_last24hrs, '.2f')) + \
            ' (robust mean of ' + \
            str(n_obs_last24hrs) + \
            ' observations). '

        change_text = 'That is ' + \
            format(abs(diff), '.2f') + \
            ' mag ' + \
            changeword + \
            ' than the robust mean of the 5 previous nights (n=' + \
            str(n_obs_last1_6_days) + \
            ', ' + \
            format(abs(sigma), '.1f') + \
            'σ). #Betelgeuse'

        text = mag_text + change_text
        print(text)
        return text



def get_mags_from_AAVSO(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    rows = soup.select('tbody tr')
    dates = []
    mags = []
    for row in rows:
        string = '' + row.text
        string = string.split('\n')
        try:
            date = float(string[3])
            mag = float(string[5])
            # Remove crap
            if mag < 3:
                dates.append(date)
                mags.append(mag)
        except:
            pass
    return np.array(dates), np.array(mags)
