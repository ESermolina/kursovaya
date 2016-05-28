import datetime
import csv
from urllib.request import urlopen
from urllib.parse import quote_plus
import logging

def day_down(close):
    day = 0
    prev_close = None
    day_down = []
    for close_price in close:
        if prev_close != None: 
            if close_price < prev_close:
                day += 1
                prev_close = close_price
            else:
                if day > 0:
                    day_down.append(day)
                    day = 0
                prev_close = close_price
        else:
            prev_close = close_price
    return max(day_down)
    
def day_MACD(data, window_s, window_l):
    try:
        import numpy as np
        weights = np.exp(np.linspace(-1., 0., window_s))
        weights /= weights.sum()
        weightl = np.exp(np.linspace(-1., 0., window_l))
        weightl /= weightl.sum()
        sma_s = np.convolve(np.array(data['close']), weights)[:len(np.array(data['close']))]
        sma_l = np.convolve(np.array(data['close']), weightl)[:len(np.array(data['close']))]
        sma_s[:window_s] = sma_s[window_s]
        sma_l[:window_l] = sma_l[window_l]
        # weight = np.ones(window)
        # weight /= weight.sum()
        sma = sma_s - sma_l
        # sma = np.convolve(np.array(sma_s)-np.array(sma_l), weight)[:len(np.array(sma_s))]
        # sma[:window] = sma[window]
        # sma = sma[window - 1:-window]
        # # sma = list(map(lambda x: x.item(), sma))
    except ImportError: 
        logging.error('Библиотека Numpy не найдена') 
    #убираем данные самого длинного периода, они не нужны 
    dates = data['date'][window_l:] 
    data = { 
        'date': dates, 
        'sma': sma[window_l:],
        'table': {date: {'sma': sma[i]} for i, date in enumerate(dates)}, 
        'columns': ['sma_up', 'sma_down'] 
        } 
    return data 

def sma_signals(data, sma):
    result = {}
    pred_sma_i = None
    for date in sorted(sma['table'].keys()):
        sma_i = sma['table'][date]['sma']
        
        if pred_sma_i == None:
            pred_sma_i = sma_i
        if (pred_sma_i < 0) and (sma_i > 0):
            result[date] = {'signal': 'BUY'} 
        elif (pred_sma_i > 0) and (sma_i < 0):
            result[date] = {'signal': 'SELL'}  
        pred_sma_i = sma_i

    return { 
        'table': result, 
        'text_columns': ['signal'] 
    } 

def print_file(file_out, rezult):
    if file_out:
        with open(file_out, 'w') as f_out:
            f_out.write(str(rezult))
    print(rezult)

def print_file_signal(file_out, data, width=15):
    row_format = '{date!s:^{width}}' 
    if file_out:
        with open(file_out, 'w') as f_out:
            for date in sorted(data['table'].keys()): 
                f_out.write(row_format.format(date=date, **data['table'][date], width=width) + data['table'][date]['signal'] + '\n')
                print(row_format.format(date=date, **data['table'][date], width=width) + data['table'][date]['signal'])

def read_url(symbol, year):
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    url = "http://www.google.com/finance/historical?q={0}&startdate={1}&enddate={2}&output=csv"
    url = url.format(symbol.upper(), quote_plus(start.strftime('%b %d, %Y')), quote_plus(end.strftime('%b %d, %Y')))
    data = urlopen(url).readlines()
    
    info = { 
        'date': [], 
        'open': [], 
        'close': [], 
        'high': [], 
        'low': [], 
        'volume': [],       
        'table': {},  # Для хранения данных по строкам 
        #информация колонках
        'columns': ['open', 'close', 'high', 'low', 'volume'] 
    } 
    
    for line in data[1:]:  # Пропускаем первую строку с именами колонок
        row = line.decode().strip().split(',')
        date = datetime.datetime.strptime(row[0], '%d-%b-%y').date() 
        open_price = float(row[1]) 
        close_price = float(row[2]) 
        high_price = float(row[3]) 
        low_price = float(row[4]) 
        volume_price = float(row[5]) 
        info['date'].append(date) 
        info['open'].append(open_price) 
        info['close'].append(close_price) 
        info['high'].append(high_price) 
        info['low'].append(low_price) 
        info['volume'].append(volume_price) 
        info['table'][date] = { 
            'open': open_price, 
            'close': close_price, 
            'high': high_price, 
            'low': low_price, 
            'volume': volume_price, 
        } 
        
    return info

def read_file(file):
    info = { 
        'date': [], 
        'open': [], 
        'close': [], 
        'high': [], 
        'low': [], 
        'volume': [],       
        'table': {},  # Для хранения данных по строкам 
        #информация колонках
        'columns': ['open', 'close', 'high', 'low', 'volume'] 
    } 
    with open(file) as f:
        f.readline()
        csv_file = csv.reader(f, delimiter=',')
        close_prices = []
        for row in csv_file:
             #date = datetime.datetime.strptime(row[0], '%d-%b-%y').date()
            date = row[0] 
            open_price = float(row[1]) 
            close_price = float(row[4]) 
            high_price = float(row[2]) 
            low_price = float(row[3]) 
            volume_price = float(row[5]) 
            info['date'].append(date) 
            info['open'].append(open_price) 
            info['close'].append(close_price) 
            info['high'].append(high_price) 
            info['low'].append(low_price) 
            info['volume'].append(volume_price) 
            info['table'][date] = { 
             'open': open_price, 
             'close': close_price, 
             'high': high_price, 
             'low': low_price, 
             'volume': volume_price, 
             }
    return info            
    
def process_data(data, file_out, indicator, window_s, window_l):
    if indicator is None:
        day = day_down(data["close"])
        print_file(file_out, day)
    if indicator == "MACD":
        sma = day_MACD(data, window_s, window_l)
        signals = sma_signals(data, sma)
        print_file_signal(file_out, signals)


def process_network(symbol,  year, file_out, indicator, window_s, window_l):
    data = read_url(symbol, year)
    process_data(data, file_out, indicator, window_s, window_l)

def process_file(file, file_out, indicator, window_s, window_l):
    data = read_file(file)
    process_data(data, file_out, indicator, window_s, window_l)