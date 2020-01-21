import numpy as np
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from wotan import flatten
from twython import Twython
import requests


def tweet(text, image):
    print('Tweeting...')
    twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
    response = twitter.upload_media(media=open(image, 'rb'))
    twitter.update_status(status=text, media_ids=[response['media_id']])
    print("Done.")


def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    flatten_lc, trend_lc = flatten(
        days_ago,
        mag,
        method='lowess',
        window_length=time_span/5,
        return_trend=True,
        )
    plt.scatter(days_ago, mag, s=5, color='blue', alpha=0.5)
    plt.xlabel('Days before today')
    plt.ylabel('Visual magnitude')
    plt.plot(days_ago, trend_lc, color='red', linewidth=1)
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.savefig(plot_file, bbox_inches='tight', dpi=300)
    print('Done.')


def build_string(days_ago, mag):
    print('Building string...')
    data_last24hrs = np.where(days_ago<1)
    data_last1_6_days = np.where((days_ago<6) & (days_ago>1))
    n_obs_last24hrs = np.size(mag[data_last24hrs])
    n_obs_last1_6_days = np.size(mag[data_last1_6_days])
    mean_last24hrs = np.mean(mag[data_last24hrs])
    mean_last1_6_days = np.mean(mag[data_last1_6_days])
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
            ' (avg of ' + \
            str(n_obs_last24hrs) + \
            ' observations). '
        change_text = 'That is ' + \
            format(abs(diff), '.2f') + \
            ' mag ' + \
            changeword + \
            ' than the avg of the 5 previous nights (n=' + \
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
            dates.append(date)
            mags.append(mag)
        except:
            pass
    return np.array(dates), np.array(mags)
    

consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')
plot_file = 'plot.png'
url = 'https://www.aavso.org/apps/webobs/results/?star=betelgeuse&num_results=200&obs_types=vis'

dates, mags = get_mags_from_AAVSO(url)
days_ago = np.max(dates) - dates
text = build_string(days_ago, mags)
if text is not None:
    make_plot(days_ago, dates, mags)
    #tweet(text, plot_file)
