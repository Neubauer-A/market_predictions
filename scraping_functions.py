import datetime
from lxml import etree
from os import system, listdir
from urllib.request import urlopen
from pandas import read_csv, concat
from pandas_datareader import data as pdr

# Download short data for one date (format: 'yyyymmdd')
def get_short_pcts(date):
  short = read_csv('http://regsho.finra.org/FNSQshvol'+date+'.txt', 
                  header=0, infer_datetime_format=True, delimiter='|',
                  parse_dates=['Date'], index_col=['Date'])
  short['pct'] = short['ShortVolume']/short['TotalVolume']
  return short[['Symbol', 'pct']]

def csv_from_yahoo(stock, date, current=True):
  if current:
    start = str(int(date)-1)
  else:
    start = date
  df = pdr.get_data_yahoo(stock, start=start, end=date)
  if current:
    df = df.drop(df.index[0])
  return df

def volatility_index(date):
  VI = csv_from_yahoo('^VIX', date)
  return VI['Close'].values[0]

def get_eps(stock):
  url = 'https://www.marketwatch.com/investing/stock/'+stock+ \
        '/financials/income/quarter'
  content = urlopen(url)
  htmlparser = etree.HTMLParser()
  tree = etree.parse(content, htmlparser)
  text_list = tree.xpath("//text()")
  try:
    index = text_list.index('EPS (Basic)')
  except:
    index = text_list.index(' EPS (Basic)')  
  eps = text_list[index+13]
  if '(' in eps:
    eps = eps[1:-1]
    return -float(eps)
  return float(eps)

def get_market_cap(stock):
  content = urlopen('https://finance.yahoo.com/quote/'+stock+'/key-statistics')
  htmlparser = etree.HTMLParser()
  tree = etree.parse(content, htmlparser)
  mc = tree.xpath('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/section/div[3]/div[1]/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[2]/text()')[0]
  if ',' in mc:  
    mc = ''.join([i for i in mc if i != ','])
    mc = float(mc)
  elif 'M' in mc:
    mc = mc[:-1]
    mc = float(mc) * 1000000
  elif 'B' in mc:
    mc = mc[:-1]
    mc = float(mc) * 1000000000
  elif 'T' in mc:
    mc = mc[:-1]
    mc = float(mc) * 1000000000000
  return mc

def get_insider_sales(stock, date):
  content = urlopen('https://finance.yahoo.com/quote/'+stock+'/insider-transactions')
  htmlparser = etree.HTMLParser()
  tree = etree.parse(content, htmlparser)
  text_list = tree.xpath("//text()")

  d = datetime.datetime.strptime(date, '%Y%m%d')
  d = d.strftime('%b %d, %Y')
  sales = 0.0

  for i in text_list:
    if "Sale at price" in i:
      if d == text_list[text_list.index(i)+3]:
        value = ''.join([x for x in text_list[text_list.index(i)+2] if x!=','])
        sales += float(value)
      else: 
        try:
          d2 = text_list[text_list.index(i)+3]
          d2 = datetime.datetime.strptime(d2, '%b %d, %Y')
          d2 = d2.strftime('%Y%m%d')
          if int(d2) < int(date):
            break
        except:
          continue
  return sales
