import numpy as np
import datetime
from matplotlib import pyplot as plt
from wotan import flatten
from betellib import tweet, build_string, get_mags_from_AAVSO


def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    min_plot = 0.0
    max_plot = 1.75
    x_days = 120
    
    # Make daily bins
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
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    date_text = datetime.datetime.now().strftime("%d %b %Y")
    plt.text(x_days-2, max_plot-0.05, 'AAVSO visual (by-eye) daily bins. Update: '+date_text)
    plt.savefig(plot_file, bbox_inches='tight', dpi=300)
    print('Plot made, test120')


# Pull the last 10 pages from AAVSO and collate the dates and mags
plot_file = 'plot120d.png'
url_base = 'https://www.aavso.org/apps/webobs/results/?star=betelgeuse&num_results=200&obs_types=vis&page='
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
    tweet(text, plot_file)
