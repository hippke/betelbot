import numpy as np
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from wotan import flatten
#from twython import Twython
#from auth import consumer_key, consumer_secret, access_token, access_token_secret
import requests
import pandas as pd


def tweet(text, image):
    print('Tweeting...')
    twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
    response = twitter.upload_media(media=open(image, 'rb'))
    twitter.update_status(status=text, media_ids=[response['media_id']])
    print("Done.")


def make_plot(days_ago, mag):
    print('Making plot...')
    time_span = np.max(date) - np.min(date)
    flatten_lc, trend_lc = flatten(
        days_ago,
        mag,
        method='lowess',
        window_length=time_span/3,
        return_trend=True,
        )
    plt.scatter(-days_ago, mag, s=5, color='blue', alpha=0.5)
    plt.xlabel('Days before today')
    plt.ylabel('Visual magnitude')
    plt.plot(-days_ago, trend_lc, color='red', linewidth=1)
    plt.gca().invert_yaxis()
    plt.savefig(plot_file, bbox_inches='tight')
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
        elif diff < 0:
            changeword = 'brighter'
        else:
            changeword = 'constant'

        mag_text = "My visual mag from last night was " + \
            str(format(mean_last24hrs, '.2f')) + \
            ' (avg of ' + \
            str(n_obs_last24hrs) + \
            ' observations). '

        change_text = 'It is ' + \
            format(diff, '.2f') + \
            ' mag ' + \
            changeword + \
            ' than the avg of the 5 previous nights (avg of ' + \
            str(n_obs_last1_6_days) + \
            ' observations). '

        sig_text = 'The significance of this change is ' + \
            format(sigma, '.1f') + \
            ' sigma.'

        text = mag_text + change_text + sig_text
        print(text)
        return text


class HTMLTableParser:
           
    def parse_url(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        return [(table['id'],self.parse_html_table(table))\
                for table in soup.find_all('table')]  

    def parse_html_table(self, table):
        n_columns = 0
        n_rows=0
        column_names = []

        # Find number of rows and columns
        # we also find the column titles if we can
        for row in table.find_all('tr'):
            
            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows+=1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)
                    
            # Handle column names if we find them
            th_tags = row.find_all('th') 
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 else range(0,n_columns)
        df = pd.DataFrame(columns = columns,
                          index= range(0,n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1
                
        # Convert to float if possible
        for col in df:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass
        
        return df

plot_file = 'plot.png'
filename = 'betelflux.csv'
url = 'https://www.aavso.org/apps/webobs/results/?star=betelgeuse&num_results=200&obs_types=vis'

hp = HTMLTableParser()
table = hp.parse_url(url)[0][1]
table.head()
avg=table['Avg'].values
print(avg)

date, mag = np.loadtxt(filename, unpack=True)
days_ago = np.max(date) - date
text = build_string(days_ago, mag)
if text is not None:
    make_plot(days_ago, mag)
    tweet(text, plot_file)

