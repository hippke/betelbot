import os
import requests
import numpy as np
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from wotan import flatten
from twython import Twython


consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')
plot_file = 'plot_long.png'
url_base = 'https://www.aavso.org/apps/webobs/results/?star=betelgeuse&num_results=200&obs_types=vis&page='


def tweet(text, image):
    print('Tweeting...')
    twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
    response = twitter.upload_media(media=open(image, 'rb'))
    twitter.update_status(status=text, media_ids=[response['media_id']])
    print("Done.")

def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    """
    flatten_lc, trend_lc = flatten(
        days_ago,
        mag,
        method='lowess',
        window_length=time_span/3,
        return_trend=True,
        )
    """
    #plt.scatter(days_ago, mag, s=5, color='blue', alpha=0.3)

    # Make daily bins
    min_plot = 0.0
    max_plot = 1.75
    x_days = 120

    nights = np.arange(0, max(days_ago), 1)
    daily_mags = []
    errors = []
    for night in nights:
        selector = np.where((days_ago<night+1) & (days_ago>night))
        n_obs = np.size(mag[selector])
        flux = np.mean(mag[selector])
        error = np.std(mag[selector]) / np.sqrt(n_obs)
        if error > 0.75:
            error = 0
        daily_mags.append(flux)
        errors.append(error)
        print(night, flux, error, n_obs, np.std(mag[selector]))
    plt.errorbar(nights+0.5, daily_mags, yerr=errors, fmt='.k')
    plt.xlabel('Days before today')
    plt.ylabel('Visual magnitude')
    mid = np.median(mag)
    plt.ylim(min_plot, max_plot)
    plt.xlim(0, x_days)
    #plt.plot(days_ago, trend_lc, color='red', linewidth=1)
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.text(x_days-2, max_plot-0.05, 'AAVSO visual (by-eye) daily bins')
    plt.savefig(plot_file, bbox_inches='tight', dpi=100)
    print('Plot made')


def build_string(days_ago, mag):
    print('Building string...')
    data_last24hrs = np.where(days_ago<1)
    data_last1_6_days = np.where((days_ago<6) & (days_ago>1))
    n_obs_last24hrs = np.size(mag[data_last24hrs])
    n_obs_last1_6_days = np.size(mag[data_last1_6_days])
    mean_last24hrs = np.median(mag[data_last24hrs])
    mean_last1_6_days = np.median(mag[data_last1_6_days])
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
            ' (med of ' + \
            str(n_obs_last24hrs) + \
            ' observations). '

        change_text = 'That is ' + \
            format(abs(diff), '.2f') + \
            ' mag ' + \
            changeword + \
            ' than the med of the 5 previous nights (n=' + \
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




pages = np.arange(1, 10, 1)
all_dates = np.array([])
all_mags = np.array([])
for page in pages:
    url = url_base + str(page)
    print(url)
    dates, mags = get_mags_from_AAVSO(url)
    all_dates = np.concatenate((all_dates, dates))
    all_mags = np.concatenate((all_mags, mags))

dates = all_dates
mags = all_mags
days_ago = np.max(dates) - dates
text = build_string(days_ago, mags)
if text is not None:
    make_plot(days_ago, dates, mags)
    #tweet(text, plot_file)
