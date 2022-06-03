import pandas as pd
from requests import get
from bs4 import BeautifulSoup
from datetime import datetime
from time import time
from time import sleep
from random import randint
from IPython.core.display import clear_output
import urllib
import re


def make_url(base_url , *res, **params):
    url = base_url
    for r in res:
        url = '{}/{}'.format(url, r)
    if params:
        url = '{}?{}'.format(url, urllib.parse.urlencode(params))
    return url


# Redeclaring the lists to store data in
names = []
urls = []
years = []
imdb_ratings = []
metascores = []
votes = []
certificates = []
runtimes = []
genres = []
descriptions = []
directors = []
stars = []
revenues = []


# Preparing the monitoring of the loop
start_time = time()
requests = 0

url_base=make_url('https://www.imdb.com/search/title/',
               title_type='feature',
               user_rating='7.5,',
               num_votes='10000,',
               release_date='2000-01-01,',
               genres='horror',
               countries='!in',
               sort='num_votes,desc')

headers = {"Accept-Language": "en-US, en;q=0.5"}

for i in range(1):
    url_current=url_base+'&start='+str(1+i*50)

    # Make a get request
    response = get(url_current, headers = headers)

    # Pause the loop
    sleep(randint(3,5))

    # Monitor the requests
    requests += 1
    elapsed_time = time() - start_time
    print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
    clear_output(wait = True)

    # Throw a warning for non-200 status codes
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests, response.status_code))

    # Break the loop if the number of requests is greater than expected
    if requests > 72:
        warn('Number of requests was greater than expected.')
        break

    # Parse the content of the request with BeautifulSoup
    page_html = BeautifulSoup(response.text, 'html.parser')

    # Select all the 50 movie containers from a single page
    mv_containers = page_html.find_all('div', class_ = 'lister-item mode-advanced')

    # For every movie of these 50
    for container in mv_containers:
        # If the movie has a Metascore, then:
        if container.find('div', class_ = 'ratings-metascore') is not None:

            # Scrape the name
            name = container.h3.a.text
            names.append(name)
            
            # Scrape the link
            url='https://www.imdb.com'+container.h3.a['href']
            urls.append(url)

            # Scrape the year
            year = container.h3.find('span', class_ = 'lister-item-year').text
            years.append(re.search('(\d{4})', year).group(1))

            # Scrape the IMDB rating
            imdb = float(container.strong.text)
            imdb_ratings.append(imdb)

            # Scrape the Metascore
            m_score = container.find('span', class_ = 'metascore').text
            metascores.append(int(m_score))

            # Scrape the number of votes
            vote = container.find('span', attrs = {'name':'nv'})['data-value']
            votes.append(int(vote))
            
            # Scrape the certificate
            try: 
                certificate = container.p.find('span', class_ = 'certificate').text
            except: 
                certificate = 'None'
            certificates.append(certificate)
            
            # Scrape the Runtime
            runtime = container.p.find('span', class_ = 'runtime').text
            runtimes.append(runtime)
            
            # Scrape the Genre
            genre = container.p.find('span', class_ = 'genre').text.replace('\n','')
            genres.append(genre)
            
            # Scrape the description
            description = container.find_all('p', class_ = 'text-muted')[-1].text.replace('\n','')
            descriptions.append(description)
            
            # Scrape the People
            value_split = container.find_all('p', class_ = '')[-1].text.replace('\n','').split("|")
            try: 
                director = re.search('(?<=Director:)(.*)', value_split[0]).group(1)
            except: 
                director = 'None'
                
            try: 
                star = re.search('(?<=Stars:)(.*)', value_split[1]).group(1)
            except: 
                star = 'None'
            
            directors.append(director)
            stars.append(star)
            
            # Scrape the Revenue
            revenue = container.find_all('span', attrs = {'name':'nv'})[-1]['data-value']
            revenues.append(revenue)


output_df = pd.DataFrame({'movie': names,
                        'url': urls,
                        'year': years,
                        'imdb': imdb_ratings,
                        'metascore': metascores,
                        'votes': votes,              
                        'certificate': certificates,
                        'runtime': runtimes,
                        'genres': genres,
                        'description': descriptions,
                        'director': directors,
                        'stars': stars,
                        'revenue': revenues                     
})

print(output_df.shape)

now = datetime.now() # current date and time
date_time = now.strftime("%m%d%Y_%H%M%S")
genre='horror'
csv_name='data_files/output/extract'+'_'+genre+'_'+date_time+'.csv'

output_df.to_csv(csv_name, index=False)