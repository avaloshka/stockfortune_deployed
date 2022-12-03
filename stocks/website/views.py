from django.shortcuts import render, redirect
# from .forms import EnterStockForm
# from jobs pull variable PRICES (it has name and df for a filtered stock). This will be displayed at Strategy
from jobs.jobs import PRICES
from django.contrib import messages

def home(request):
	page_title = 'HOME'
	return render(request, 'home.html', {'page_title': page_title})

def introduction(request):
	page_title = 'INTRODUCTION'
	return render(request, 'introduction.html', {'page_title': page_title})

def members(request):
	page_title = 'MEMBERS AREA'
	return render(request, 'members.html', {'page_title': page_title})

def join(request):
	page_title = 'JOIN'
	return render(request, 'join.html', {'page_title': page_title})

def strategy(request):
	import pandas as pd
	page_title = 'Strategy'
	global PRICES

	# pass stock names to the page
	names = [stock['name'] for stock in PRICES]
	stock_names = ', '.join(names)
		
	return render(request, 'strategy.html', {'page_title': page_title, 'names': stock_names})

def magic(request):
	page_title = "Magic"
	return render(request, 'magic.html', {'page_title': page_title})

def lesson1(request):
	return render(request, 'lesson1.html', {})

def charts(request):
	from .models import Charts
	page_title = 'Stock selected by bot last midnight'
	all = Charts.objects.all()

	return render(request, 'charts.html', {'page_title': page_title, 'all': all})

def your_stock(request):
	page_title = 'Your stock'

	if request.method == 'POST':
		# get the posted form
		
		ticker = str(request.POST['name'])
		
		try:
			import numpy as np
			import matplotlib.pyplot as plt
			import time
			import datetime
			import pandas as pd
			from termcolor import colored
			import io, base64
			import urllib

			time_now = datetime.datetime.now()

		
			# specify time 'from' for df
			period1 = int(time.mktime(datetime.datetime(2020, 12, 31, 23, 59).timetuple()))
			# specify time 'to' for df (it will be time now in this case)
			period2 = int(time.mktime(datetime.datetime.now().timetuple()))
			# set interval that the df will show
			interval = '1d'

			query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'

			df = pd.read_csv(query_string)
			print(colored(f'{ticker}', 'blue'))
			print(df)

			plt.style.use('fivethirtyeight')

			# set date to be index
			df = df.set_index(pd.DatetimeIndex(df['Date'].values))

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

			ax.set_title(f'Bollinger band for {ticker}')
			ax.set_xlabel('Date')
			ax.set_ylabel('USD Price ($)')
			plt.xticks(rotation=20)
			ax.legend()

			plt.grid(linestyle = '--', linewidth = 1)
			# plt.show()

			buf = io.BytesIO()
			fig.savefig(buf, format='png')
			buf.seek(0)
			string = base64.b64encode(buf.read())
			uri = urllib.parse.quote(string)

			# make new entries in Charts

			# stock_chart = Charts(img=uri, name=name)
			# stock_chart.save()

			return render(request, 'your_stock.html', {'page_title': page_title, 'ticker': ticker, 'uri': uri})


		except:
			messages.success(request, ("Could not find name. Check abriviation..."))
			return redirect('your_stock')


	return render(request, 'your_stock.html', {'page_title': page_title})

def protecting_your_trade(request):
	page_title = 'Protecting your trade'

	return render(request, 'protecting_your_trade.html', {'page_title': page_title})

def buy_half_price(request):
	page_title = 'Buy for half the price'

	return render(request, 'buy_half_price.html', {'page_title': page_title})

def conclusion(request):
	page_title = 'Conclusion'

	return render(request, 'conclusion.html', {'page_title': page_title})