# This Project involves: 
#1. Fetching data from world bank APIs- country API and Indicator API, used requests library: 
#2. Data Matching that is string matching needed to get more number of data rows: defined string conversion function, and
#   string match using fuzzywuzzy library (soundex or regex could also be used)
#3. DataFrame formation using Pandas
#4. Data Claeaning : dropping of duplicates, deletion of extra rows, pivot of dataFrame to get in desired shape.
#5. Data Analysis and Graphs formation 

# first import necessary Libraries:
import requests
import json
import pandas as pd
import numpy as np

# importing fuzzywuzzy for string matching
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process



Url = 'given'

def datafetchingapi(url):       # function has beeen defined to fetch data from given url.
  county_dat = []
  for pageno in range(1,8):
    payload = {'page': pageno}
    data =requests.get(country_url, payload).json()
    county_dat = county_dat + data[1]
  return county_dat
    
#to get the necessary columns of id and name:    
county_dat_id= []
county_dat_name = []
for i in county_dat:
    county_dat_id.append( i['id'])
    county_dat_name.append(i['name'])
    
# Converting list into Dataframe :
coty_df = pd.DataFrame({'id':county_dat_id, 'name':county_dat_name})
coty_df.head()


####
countrylist = 'create list of names of countries of world.'

# since original data also contains name of diff regions, continent, world, and different spelling of names.
#therefore string matching is needed to get maximum no of names.for this regex, fuzzywuzzy and soundex can be used
# to get more accurate and more number of correct country name.
## checking the country through FuzzyWuzzy
coty_df['isCountry'] = 0
coty_df['isCountry_fuzzy'] = 0
        
for i in range(len(coty_df)):
    #print(coty_df.loc[i,'name'])   # this gives 
    match = process.extract(coty_df.loc[i,'name'], countrylist)   #using fuzzywuzzy library here
    if match[0][1]>=90:
        print(i,'present')
        coty_df.loc[i,'isCountry_fuzzy']=1
        
        
        
# Function for string onversion to lower case to be used below, this will increase number of matches:
def modify_name(name):
    alphabets = 'abcdefghijklmnopqrstuvwxyz'
    tmp = []
    for alphabet in name:
        lc = alphabet.lower()
        if lc in alphabets:
            tmp.append(lc)
    mod_name = ''.join(tmp)
    return mod_name

  
# checking country through simple string comparisons - lower, special characters replace-- rep is used 
# bcoz rep means republic which should be used along with country name.
coty_df['isCountry_own'] = 0

for i in range(len(coty_df)):
    #print(coty_df.loc[i,'name'])   # this gives 
    if modify_name(coty_df.loc[i,'name']) in mod_countrylist or 'Rep' in coty_df.loc[i,'name']:
        print(i,'present')
        coty_df.loc[i,'isCountry_own']=1
        
        
        
  # noe fecthing more data using Indicator API:
  
datframe = pd.DataFrame()
county_id_df = coty_df['id']
for i in county_id_df:
    #print(i)
    #i = 'ABW'
    print("Fetching the data of the country : {}".format(i))
    url= 'http://api.worldbank.org/v2/country/'+ i + '/indicator/NY.GDP.MKTP.CD?format=json'
    response = requests.get(url)
    #response.json()[1]
    
    country_data = response.json()[1]
    #if country_data != None or country_data['countryiso3code']!='':
    if country_data != None :
        #print(country_data[0].keys())
        daf = pd.DataFrame(country_data)
        print(daf[['countryiso3code', 'date', 'value']])
        #if daf[daf.countryiso3code=='']:
            #print()
        
        
        #gdpdata=daf[['date', 'value','countryiso3code']]
        datframe = datframe.append(daf[['country','countryiso3code','date', 'value']], ignore_index= True)
        #if i== 'ABW':
        #break
    else:
        print('No data for the country {}'.format(i))
        


# adding 1 to region where there is no countryiso3code. These belongs to regions and not countries. 
datframe['region'] = 0

for i in range(len(datframe)):
    if datframe.loc[i, 'countryiso3code']== '':
        datframe.loc[i, 'region'] = 1

#saving datframe as csv file:        
datframe.to_csv('datframe.csv', sep='~')

# opening csv file:
df_worldbank = pd.read_csv("datframe.csv", sep = '~')
df_worldbank.head()   

del df_worldbank['Unnamed: 0']

# to get only countries data:
df1 = df_worldbank[df_worldbank.region==0].reset_index(drop=True)

# Pivot dataframe to get desired shape:
df_country = df1.pivot(index='countryiso3code',columns='date',values='value')
df_country.head()

#output of above code is given below:
# date	1969	1970	1971	1972	1973	1974	1975	1976	1977	1978	...	2009	2010	2011	2012	2013	2014	2015	2016	2017	2018
# countryiso3code																					
# AFG	1.408889e+09	1.748887e+09	1.831109e+09	1.595555e+09	1.733333e+09	2.155555e+09	2.366667e+09	2.555556e+09	2.953333e+09	3.300000e+09	...	1.243909e+10	1.585657e+10	1.780428e+10	2.000162e+10	2.056105e+10	2.048487e+10	1.990711e+10	1.936264e+10	2.019176e+10	1.936297e+10
# AGO	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN	...	7.030716e+10	8.379950e+10	1.117897e+11	1.280529e+11	1.367099e+11	1.457122e+11	1.161936e+11	1.011239e+11	1.221238e+11	1.057510e+11
# ALB	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN	...	1.204421e+10	1.192695e+10	1.289087e+10	1.231978e+10	1.277628e+10	1.322825e+10	1.138693e+10	1.186135e+10	1.302506e+10	1.505888e+10
# AND	NaN	7.861921e+07	8.940982e+07	1.134082e+08	1.508201e+08	1.865587e+08	2.201272e+08	2.272810e+08	2.540202e+08	3.080089e+08	...	3.660531e+09	3.355695e+09	3.442063e+09	3.164615e+09	3.281585e+09	3.350736e+09	2.811489e+09	2.877312e+09	3.013387e+09	3.236544e+09
# ARE	NaN	NaN	NaN	NaN	NaN	NaN	1.472067e+10	1.921302e+10	2.487178e+10	2.377583e+10	...	2.535474e+11	2.897873e+11	3.506660e+11	3.745906e+11	3.901076e+11	4.031371e+11	3.581351e+11	3.570451e+11	3.825751e+11	4.141789e+11


# taking yearwise gdp data for India, China, USA and Japan:
gdp_yearwise = df_country.loc[['IND','CHN','USA', 'JPN'], [2010,2011,2012,2013,2014,2015,2016,2017,2018]]
gdp_yearwise.plot(kind= 'bar')   # drawing bar graph.







        
