import numpy as np
from matplotlib import pyplot as plt
import datetime
from betellib import tweet


def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    min_plot = 1.75
    max_plot = 0
    
    # 30-day bins for the century scale
    bin_width = 30  # days
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
    # Convert days to digital years
    date = datetime.datetime.now()
    digi_year = (float(date.strftime("%j"))-1) / 366 + float(date.strftime("%Y"))
    days = nights+bin_width/2
    years_before = digi_year - (days / 365.2524)

    fig, ax = plt.subplots()
    plt.errorbar(years_before, bin_mags, yerr=errors, fmt='.k', alpha=0.5)
    plt.scatter(years_before[0], bin_mags[0], s=50, marker="o", color='red', alpha=0.5)

    # 3-day bins for the last 90 days
    bin_width = 3  # days
    nights = np.arange(0, 90, bin_width)
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
    # Convert days to digital years
    date = datetime.datetime.now()
    digi_year = (float(date.strftime("%j"))-1) / 366 + float(date.strftime("%Y"))
    days = nights+bin_width/2
    years_before = digi_year - (days / 365.2524)
    plt.plot(years_before, bin_mags, color='blue', alpha=0.5)
    plt.scatter(years_before[0], bin_mags[0], marker="x", color='blue', s=50)
    print(bin_mags[0])

    plt.xlabel('Year')
    plt.ylabel('Visual magnitude')
    mid = np.median(mag)
    plt.ylim(min_plot, max_plot)
    plt.xlim(1890, digi_year+5)
    date_text = datetime.datetime.now().strftime("%d %b %Y")
    plt.text(1893, 1.7, 'AAVSO visual (by-eye) 30-day bins. Update: '+date_text)
    plt.savefig(plot_file, bbox_inches='tight', dpi=300)
    print('Plot made')
    return str(round(bin_mags[0], 2))  # e.g., "1.61" mags


baseline_mag = 0.5
plot_file = "longest.png"
filename = 'aavso_vis.csv'
dates, mags = np.loadtxt(filename, unpack=True)
days_ago = np.max(dates) - dates
lumi = make_plot(days_ago, dates, mags)
text = "#Betelgeuse today at its dimmest in 125 years at " + lumi + " mag"
print(text)
tweet(text, plot_file)
