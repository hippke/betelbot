import datetime
import os
import glob
import PIL
import numpy as np
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from astropy.stats import biweight_location


from transitleastsquares import cleaned_array
from betellib import build_string, get_mags_from_AAVSO, tweet

from sklearn import gaussian_process
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel


def make_plot(days_ago, dates, mag):
    print('Making plot...')
    time_span = np.max(dates) - np.min(dates)
    min_plot = 0.0
    max_plot = 2
    x_days = -120
    
    # Make daily bins
    nights = np.arange(0, 120, 1)
    daily_mags = []
    errors = []
    for night in nights:
        selector = np.where((days_ago<night+1) & (days_ago>night))
        n_obs = np.size(mag[selector])
        flux = biweight_location(mag[selector])
        error = np.std(mag[selector]) / np.sqrt(n_obs)
        if error > 0.75:
            error = 0
        daily_mags.append(flux)
        errors.append(error)
        print(night, flux, error, n_obs, np.std(mag[selector]))
    nights_all = nights.copy()
    daily_mags_all = daily_mags.copy()
    errors_all = errors.copy()

    lookback = np.arange(1, 20, 1)

    for missing_days in lookback:
        nights = nights_all.copy()[missing_days:]
        daily_mags = daily_mags_all.copy()[missing_days:]
        errors = errors_all.copy()[missing_days:]
        plt.errorbar(-(nights+0.5), daily_mags, yerr=errors, fmt='.k', alpha=0.5)
        plt.xlabel('Days from today')
        plt.ylabel('Visual magnitude')
        mid = biweight_location(mag)
        plt.ylim(min_plot, max_plot)
        plt.xlim(x_days, 120)
        plt.gca().invert_yaxis()
        date_text = datetime.datetime.now().strftime("%d %b %Y")
        plt.text(-x_days-2, min_plot+0.1, 'AAVSO visual (by-eye) daily bins', ha='right')
        plt.text(-x_days-2, min_plot+0.2, 'Gaussian process regression, Matern 3/2 kernel', ha='right')
        plt.text(-x_days-2, min_plot+0.3, '@betelbot update ' + date_text, ha='right')
        use_days = 30-missing_days
        X = np.array(nights+0.5)
        X = X[:use_days]
        y = np.array(daily_mags)
        y = y[:use_days]
        X, y = cleaned_array(X, y)
        length_scale = 1
        kernel = ConstantKernel() + Matern(length_scale=length_scale, nu=3/2) + WhiteKernel(noise_level=1)
        X = X.reshape(-1, 1)
        gp = gaussian_process.GaussianProcessRegressor(kernel=kernel)
        gp.fit(X, y)
        GaussianProcessRegressor(alpha=1e-10, copy_X_train=True,
        kernel=1**2 + Matern(length_scale=length_scale, nu=1.5) + WhiteKernel(noise_level=1),
        n_restarts_optimizer=0, normalize_y=False,
        optimizer='fmin_l_bfgs_b', random_state=None)
        x_pred = np.linspace(30, -120, 250).reshape(-1,1)
        y_pred, sigma = gp.predict(x_pred, return_std=True)
        plt.plot(-x_pred, y_pred, linestyle='dashed', color='blue')
        plt.fill_between(-x_pred.ravel(), y_pred+sigma, y_pred-sigma, alpha=0.5)
        idx = 20 - missing_days
        if idx < 10:
            filename = "0" + str(idx) +'.png'
        else:
            filename = str(idx) +'.png'
        
        plt.savefig(filename, bbox_inches='tight', dpi=100)
        print('Plot made', filename)
        plt.clf()


# Clear old crap
files = glob.glob('*.png')
for file in files:
    os.remove(file)

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
make_plot(days_ago, dates, mags)

# Make animation
frames = []
files = glob.glob('*.png')
files.sort()
for file in files:
    print('Appending file', file)
    new_frame = PIL.Image.open(file, mode='r')
    frames.append(new_frame)

# Make last frame last longer
for i in range(5):
    frames.append(new_frame)
    
# Save gif
frames[0].save(
    'betel_video.gif',
    format='GIF',
    append_images=frames,
    save_all=True,
    duration=500,
    loop=0)  # forever

for file in files:
    os.remove(file)

tweet("Updated #Betelgeuse forecast", 'betel_video.gif')
