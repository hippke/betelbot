#import os
#import requests
import numpy as np
import datetime
#from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from wotan import flatten
from betellib import tweet, build_string, get_mags_from_AAVSO
#from datetime import datetime



def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    min_plot = 0
    max_plot = 1.4
    x_days = 2000
    
    # Make daily bins
    bin_width = 10
    nights = np.arange(0, max(days_ago), bin_width)
    bin_mags = []
    errors = []
    for night in nights:
        selector = np.where((days_ago<night+bin_width) & (days_ago>night))
        n_obs = np.size(mag[selector])
        flux = np.mean(mag[selector])
        error = np.std(mag[selector]) / np.sqrt(n_obs)
        if error > 0.2:
            error = 0
        bin_mags.append(flux)
        errors.append(error)
        print(night, flux, error, n_obs, np.std(mag[selector]))

    bin_mags = np.array(bin_mags)
    flux = 1 / (10**(0.4 * (bin_mags - baseline_mag)))
    print(flux)

    date = datetime.datetime.now()
    digi_year = (float(date.strftime("%j"))-1) / 366 + float(date.strftime("%Y"))
    days = nights+bin_width/2
    years = days / 365.2524
    years_before = digi_year - years
    #years_before = years_before[::-1]
    print(years_before)

    fig, ax = plt.subplots()
    plt.errorbar(years_before, flux, yerr=errors, fmt='.k')
    plt.xlabel('Year')
    plt.ylabel('Normalized flux')
    mid = np.median(mag)
    plt.ylim(min_plot, max_plot)
    plt.xlim(2015, digi_year+0.25)
    #plt.gca().invert_yaxis()
    #plt.gca().invert_xaxis()
    date_text = datetime.datetime.now().strftime("%d %b %Y")
    plt.text(2015.1, 0.03, 'AAVSO visual (by-eye) 10-day bins. Update: '+date_text)
    plt.savefig(plot_file, bbox_inches='tight', dpi=300)
    print('Plot made')
    #last_percentage = 
    #return flux[:-1]


# Pull the last 10 pages from AAVSO and collate the dates and mags
plot_file = 'plot5y.png'
url_base = 'https://www.aavso.org/apps/webobs/results/?star=betelgeuse&num_results=200&obs_types=vis&page='
baseline_mag = 0.5
pages = np.arange(1, 25, 1)
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

data_last24hrs = np.where(days_ago<1)
mean_last24hrs = np.median(mags[data_last24hrs])
flux = 1 / (10**(0.4 * (mean_last24hrs - baseline_mag)))
percentage = str(int(round(flux * 100, 0)))
text = "#Betelgeuse is now at " + percentage + r"% of its usual brightness!"
print(text)

if text is not None:
    make_plot(days_ago, dates, mags)
    tweet(text, plot_file)
