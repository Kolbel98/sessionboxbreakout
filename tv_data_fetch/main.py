from tvDatafeed import TvDatafeed, Interval
import os

username = os.getenv('TV_USERNAME')
password = os.getenv('TV_PASSWORD')

tv = TvDatafeed(username, password)


data = tv.get_hist(
    symbol="FDAX1!",
    exchange="EUREX",
    interval=Interval.in_1_minute,
    n_bars=10000
)

print(type(data))
print(data.dtypes)
print(data.tail())