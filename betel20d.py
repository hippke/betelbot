import numpy as np
import datetime
from matplotlib import pyplot as plt
from wotan import flatten
from betellib import tweet, build_string, get_mags_from_AAVSO


def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    flatten_lc, trend_lc = flatten(
        days_ago,
        mag,
        method='lowess',
        window_length=time_span/3,
        return_trend=True,
        )
    plt.scatter(days_ago, mag, s=5, color='blue', alpha=0.5)
    plt.xlabel('Days before today')
    plt.ylabel('Visual magnitude')
    mid = np.median(mag)
    plt.ylim(mid-1, mid+1)
    plt.xlim(0, 20)
    plt.plot(days_ago, trend_lc, color='red', linewidth=1)
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    date_text = datetime.datetime.now().strftime("%d %b %Y")
    plt.text(19.5, mid+1-0.05, 'AAVSO visual (by-eye) observations. Update: '+date_text)
    plt.savefig(plot_file, bbox_inches='tight', dpi=300)
    print('Done.')


# Pull the last 10 pages from AAVSO and collate the dates and mags
plot_file = 'plot20d.png'
url_base = 'https://www.aavso.org/apps/webobs/results/?star=betelgeuse&num_results=200&obs_types=vis&page='
pages = np.arange(1, 4, 1)
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
