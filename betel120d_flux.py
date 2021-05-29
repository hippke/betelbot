import numpy as np
import datetime
from matplotlib import pyplot as plt
from betellib import tweet, build_string, get_mags_from_AAVSO
from astropy.stats import biweight_location


def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    min_plot = 0
    max_plot = +1.5
    x_days = 300
    
    # Make bins
    bin_width = 1
    nights = np.arange(0, max(days_ago), bin_width)
    bin_mags = []
    errors = []
    for night in nights:
        selector = np.where((days_ago<night+bin_width) & (days_ago>night))
        n_obs = np.size(mag[selector])
        flux = biweight_location(mag[selector])
        error = np.std(mag[selector]) / np.sqrt(n_obs)
        if error > 0.2:
            error = 0
        if error == 0:# and flux < 0.2:
            flux = np.nan
        bin_mags.append(flux)
        errors.append(error)
        print(night, flux, error, n_obs, np.std(mag[selector]))

    # Convert magnitudes to fluxes
    bin_mags = np.array(bin_mags)
    flux = 1 / (10**(0.4 * (bin_mags - baseline_mag)))
    latest_flux = flux[0]
    if np.isnan(latest_flux):
        latest_flux = flux[1]

    plt.errorbar(nights+0.5, flux, yerr=errors, fmt='.k')
    plt.xlabel('Days before today')
    plt.ylabel('Normalized flux (0.5 mag baseline)')
    plt.ylim(min_plot, max_plot)
    plt.xlim(x_days, 0)
    date_text = datetime.datetime.now().strftime("%d %b %Y")
    try:
        lumi = str(int((round(latest_flux*100, 0))))
        text = "#Betelgeuse at " + lumi + r"% of its usual brightness @betelbot "
    except:
        text = "No new #Betelgeuse brightness tonight @betelbot"
        lumi = 0
    plt.text(x_days-2, 0.19, "Update: " + date_text)
    plt.text(x_days-2, 0.12, text)
    plt.text(x_days-2, 0.05, "AAVSO visual (by-eye) daily bins")
    plt.savefig(plot_file, bbox_inches='tight', dpi=300)
    print('Plot made')
    return lumi


# Pull the last 10 pages from AAVSO and collate the dates and mags
plot_file = 'plot120d_flux.png'
url_base = 'https://www.aavso.org/apps/webobs/results/?star=betelgeuse&num_results=200&obs_types=vis&page='
baseline_mag = 0.5
pages = np.arange(1, 20, 1)
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

lumi = make_plot(days_ago, dates, mags)
if lumi == 0:
    text = "No new #Betelgeuse brightness tonight"
else:
    text = "Now at " + lumi + r"% of my usual brightness! #Betelgeuse"
    tweet(text, plot_file)
print(text)

