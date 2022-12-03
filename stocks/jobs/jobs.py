from django.conf import settings

PRICES = []

class Millioner:
    def __init__(self):
        self.group_url = 'https://finviz.com/groups.ashx?g=sector&v=140&o=name'
        # out of them we need to find winner and winner_url
        self.winner_url = ''
        self.settings_url = ''
        self.stock = ''
        self.prices = []

    def get_successful_group(self):
        # the group url is known
        from bs4 import BeautifulSoup
        import requests
        import pandas as pd

        pd.set_option('display.max_columns', None)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
        }
        # Try parsing
        try:
            # reset winner url and get a new one
            self.winner_url = ''

            response = requests.get(self.group_url, headers=headers).text
            soup = BeautifulSoup(response, 'html.parser')
            # table = soup.find('table', attrs={'class': 'table-light'})

            # list of names for columns
            columns = [col.text for col in soup.findAll('td', {'class': 'table-top cursor-pointer'})]
            columns.insert(1, "Name")

            all_rows_in_one_str = [row.text for row in soup.findAll('td', {'class': 'body-table'})]

            # I need to split list into chunks of 13 (columns), and each list will become a new row
            chunk_size = 13
            rows = [all_rows_in_one_str[i:i + chunk_size] for i in range(0, len(all_rows_in_one_str), chunk_size)]

            df = pd.DataFrame(columns=columns)
            for row in rows:
                # Add each row to the end of df
                df.loc[len(df)] = row
            # Drop column 'No.'
            df = df.drop(['No.'], axis=1)
            # I have a dataframe at this point

            # Parse links for every sector in the table
            links_for_sector = []
            for row in soup.findAll('td', {'class': 'body-table'}):
                try:
                    a = row.a
                    if a:
                        links_for_sector.append('https://finviz.com/' + a.get('href'))
                except:
                    # ignore every item except the one that contains tag <a>
                    continue
            # print(f"Links for sector: {links_for_sector}")

            # Append links to dataframe

            df['Url'] = links_for_sector

            # get rid of "%" in some columns
            df['Perf Week'] = df['Perf Week'].str.replace('%', '')
            df['Perf Month'] = df['Perf Month'].str.replace('%', '')
            df['Perf Quart'] = df['Perf Quart'].str.replace('%', '')

            df['Perf Week'] = pd.to_numeric(df['Perf Week'])
            df['Perf Month'] = pd.to_numeric(df['Perf Month'])
            df['Perf Quart'] = pd.to_numeric(df['Perf Quart'])

            df['Sum'] = df['Perf Week'] + df['Perf Month'] + df['Perf Quart']

            # sort df to show biggest 'Sum' first
            sorted = df.sort_values('Sum', ascending=False)

            # winner's url:

            self.winner_url = sorted['Url'].iloc[0]
            # print(f"Winner url: {self.winner_url}")
            # return self.winner_url

        # If parsing website change- catch the error to prevent program crash
        except Exception as e:
            return e

    def get_settings_to_url(self):
        self.settings_url = ''

        # get the sector
        url = self.winner_url
        start = url.find('f=')
        end = url.find('&v')
        sector = url[start+2:end]
        # I know the sector name now

        # Now I apply Beta- over 1.5, p/e- under 5, and get new_url
        # You can change the settings yourself by changing url
        new_url = f"https://finviz.com/screener.ashx?v=141&f=fa_pe_u5,{sector},ta_beta_o1.5&ft=4"
        self.settings_url = new_url


    def parse_stock_names(self):
        from bs4 import BeautifulSoup
        import requests
        import pandas as pd

        self.stock = ''

        pd.set_option('display.max_columns', None)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
        }
        # Try parsing
        try:
            response = requests.get(self.settings_url, headers=headers).text
            soup = BeautifulSoup(response, 'html.parser')

            # Get names from table
            names = [name.text for name in soup.findAll('a', {'class': 'screener-link-primary'})]
            self.stock = names
            # print(f"Stock: {self.stock}")
            
        except:
            print("I could not do final parsing of stock names provided")

    def get_historical_prices(self):
        import yfinance as yf
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        self.prices = []

        for ticker in self.stock:
            stock = yf.Ticker(ticker)
            today = datetime.today().strftime('%Y-%m-%d')
            # print(f"Today : {today}", type(today))
            year_ago = datetime.now() - relativedelta(years=1)
            year_ago = year_ago.strftime('%Y-%m-%d')
            # print(f"Year ago: {year_ago}", type(year_ago))
            df = stock.history(start=year_ago, end=today, interval='1d')

            item = {
                'name': ticker,
                'df': df
            }
            
            self.prices.append(item)
            

            print('successfully pulled info on single stock')
            
        global PRICES
        PRICES = self.prices
           
            

    def get_bullinger_bands(self):
        import pandas as pd
        import numpy as np
        import matplotlib
        
        import matplotlib.pyplot as plt

        import io, base64
        import datetime
        from termcolor import colored

        from django.core.files.images import ImageFile
        import urllib

        from website.models import Charts

        # for entry in Charts: delete entry
        charts = Charts.objects.all()
        for entry in charts:
            entry.delete()

        for item in self.prices:
            name = item['name']
            df = item['df']

            # set date to be index
            # df = df.set_index(pd.DatetimeIndex(df['Date'].values))

            # calculate simple moving average, standard deviation, upper band and lower band for "Bollinger Bands"
            # get a time period (20 days)
            period = 20
            # Calculate the simple moving average (SMA)
            df['SMA'] = df['Close'].rolling(window=period).mean()
            # get the standard deviation
            df['STD'] = df['Close'].rolling(window=period).std()
            # Calculate the Upper Bollinger Band
            df['Upper'] = df['SMA'] + 2 * df['STD']
            # Calculate the Lower Bollinger Band
            df['Lower'] = df['SMA'] - 2 * df['STD']

            # Create a list of columns to keep
            column_list = ['Close', 'SMA', 'Upper', 'Lower']

            # create new df
            new_df = df[period - 1:]

            # show the new data

            # Create a function to get buy and sell signals
            def get_signal(data):
                buy_signal = []
                sell_signal = []

                for i in range(len(data['Close'])):
                    if data['Close'][i] > data['Upper'][i]:  # Then you should sell
                        buy_signal.append(np.nan)
                        sell_signal.append(data['Close'][i])
                    elif data['Close'][i] < data['Lower'][i]:  # Then you should buy
                        buy_signal.append(data['Close'][i])
                        sell_signal.append(np.nan)
                    else:
                        buy_signal.append(np.nan)
                        sell_signal.append(np.nan)

                return (buy_signal, sell_signal)

            # Create two new columns
            new_df['Buy'] = get_signal(new_df)[0]
            new_df['Sell'] = get_signal(new_df)[1]

            # Plot all of the data

            fig = plt.figure(figsize=(12.2, 6.4))
            ax = fig.add_subplot(1, 1, 1)
            x_axis = new_df.index
            ax.fill_between(x_axis, new_df['Upper'], new_df['Lower'], color='grey')
            ax.plot(x_axis, new_df['Close'], color='gold', lw=3, label='Close Price', alpha=0.5)
            ax.plot(x_axis, new_df['SMA'], color='blue', lw=3, label='Simple Moving Average', alpha=0.5)
            ax.scatter(x_axis, new_df['Buy'], color='green', lw=3, label='Buy', marker='^', alpha=1)
            ax.scatter(x_axis, new_df['Sell'], color='red', lw=3, label='Sell', marker='v', alpha=1)

            ax.set_title(f'Bollinger bands for "{name}"')
            ax.set_xlabel('Date')
            ax.set_ylabel('USD Price ($)')

            plt.xticks(rotation=45)
            ax.legend()
            plt.grid(linestyle = '--', linewidth = 0.5)
            # plt.show()

            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            string = base64.b64encode(buf.read())
            uri = urllib.parse.quote(string)

            # make new entries in Charts

            stock_chart = Charts(img=uri, name=name)
            stock_chart.save()
            
            print('The code run successfully')
            

    def run_in_order(self):
        # filter 8000 stock to successful group
        self.get_successful_group()
        # apply Beta 1.5- to select stock that is moving together with market but is 50% more volotile
        self.get_settings_to_url()
        # get names of stock I will be interested in
        self.parse_stock_names()
        # get historical prices for stock
        self.get_historical_prices()
        # get charts
        self.get_bullinger_bands()


# df columns:
    # ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
    # I could base my analysis not on 'Close' price but on median of 'High' and 'Low' for the day
    # The predictability of this method is still not very scientific