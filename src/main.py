
## libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
import fastparquet as fp
import os
import pandas as pd
import logging
import random

logging.basicConfig(level=logging.INFO, filename="logs.log", format="%(asctime)s - %(levelname)s - %(message)s")

main_url = 'https://lista.mercadolivre.com.br/iphone-13s-pro-max' ## website 
products_per_page = 50 ## products per page
filepath_products = 'data/products.parquet'  ## save data local 
seconds_wait = 2 ## seconds to not overcharge requests

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}


def write_append_parquet(filepath, df):
    if os.path.isfile(filepath) == True: ## check if parquet already exists
        fp.write(filepath, df,append = True) ## if, only append rows
    else:
        fp.write(filepath, df) ## if not exists, create parquet


def random_sleep(seconds): ## random wiat function to avoid 
    delay = random.random()*seconds
    time.sleep(delay)

def extract_products_urls(page_url): ## this function extract urls from main page and return a products urls list
    
    response = requests.get(page_url,headers=headers)
    html = response.text
        
    #BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')

    #Finding all products elements from page
    products = soup.find_all('li', class_='ui-search-layout__item shops__layout-item')
    urls = []

    for i in range(len(products)): ## getting href with the url
        product = products[i]
        url = product.find('a', class_='ui-search-item__group__element shops__items-group-details ui-search-link')['href']
        urls.append(url)
    return urls


def get_seller_name(url): ## this function get the seller name with a profile page url
    response = requests.get(url,headers=headers)
    html = response.text
        
    soup = BeautifulSoup(html, 'html.parser')

    seller_name = soup.find('h3', class_='store-info__name').text.strip() ## seller name
    return(seller_name)

def extract_info_from_product_url(product_url): ## this function get the informations about a product with a product page url
    
    response = requests.get(product_url,headers=headers)
    logging.info(f'{response} url: {product_url}')
    html = response.text
    
    soup = BeautifulSoup(html, 'html.parser')

    if response.status_code == 200: ## check if successed
        try:
            values = soup.find_all('div', class_ ="ui-pdp-container ui-pdp-container--pdp")[0] ## filttering common div
        except:
            logging.warning(f'Values Not Found! url: {product_url}')

        try:
            name = values.find('h1', class_='ui-pdp-title').text.strip() ## product name
        except:
            name = '' ## blank if not find
            logging.warning(f'Name Not Found! url: {product_url}')

        try:
            price = values.find('span', class_='andes-money-amount__fraction').text.strip() ## product price
        except:
            price = ''
            logging.warning(f'Price Not Found! url: {product_url}')

        try:
            currency = values.find('span', class_='andes-money-amount__currency-symbol').text.strip() # product currency
        except:
            currency = '' ## blank if not find
            logging.warning(f'Currency Not Found! url: {product_url}')
        
        seller = ''
        count = 0
        while seller == '' and count <= 3: ## if not find, try 3 times
            try:
                seller_url =  soup.find('a', class_ ='ui-pdp-media__action ui-box-component__action')['href'] ## seller url 
                seller = get_seller_name(seller_url) ## getting the seller name with a seller url
            except: 
                seller_url = '' ## blank if not find
                seller = ''
                time.sleep(1)
                logging.warning(f'Seller Not Found! url: {product_url}')
                response = requests.get(product_url,headers=headers)
                logging.info(f'{response} url: {product_url}')
                html = response.text
                count = count + 1 ## more one attempt
                soup = BeautifulSoup(html, 'html.parser')

        try:
            stock = values.find('span', class_='ui-pdp-buybox__quantity__available').text.strip()  
        except:
            try:
                stock = values.find('p', class_='ui-pdp-color--BLACK ui-pdp-size--MEDIUM ui-pdp-family--SEMIBOLD').text.strip()
                if stock == 'Último disponível!':
                    stock = '1'
                else:
                    pass
            except:
                stock = ''
                logging.warning(f'Stock Not Found! url: {product_url}')

        output =  {'name': name, 
                'price':price,
                'currency': currency, 
                'seller': seller,
                'seller_url': seller_url,
                'stock': stock,
                'product_url':product_url}
        
        try:
            output['stock'] = int(re.findall(r'\d+', output['stock'])[0]) 
        except:
            output['stock'] = None


        output['price'] = output['price'].replace('.','')
        
        df = pd.DataFrame({'name':[output['name']], ## creating a dataframe
                    'price':[output['price']],
                    'currency':[output['currency']],
                    'seller':[output['seller']],
                    'seller_url':[output['seller_url']],
                    'stock':[output['stock']],
                    'product_url':[output['product_url']]})
        
        write_append_parquet(filepath_products,df) ## saving products infos as a parquet

        logging.info(f'Saved: {output}')
    else: ## if response is not 2xx, saving blank products infos as a parquet
        
        output =  {'name': None,
                'price':None,
                'currency': None, 
                'seller': None,
                'seller_url': None,
                'stock': None,
                'product_url':product_url}
        
        df = pd.DataFrame({'name': [None],
                    'price':[None],
                    'currency':[None],
                    'seller':[None],
                    'seller_url':[None],
                    'stock':[None],
                    'product_url':[product_url]})
            
            
        write_append_parquet(filepath_products,df)

        logging.info(f'Saved: {output}')
    
    return output

def get_n_pages(url): ## this function 
    
    response = requests.get(url,headers=headers)
    html = response.text
        
    soup = BeautifulSoup(html, 'html.parser')

    n_pages =  int(soup.find_all('li', class_='andes-pagination__page-count')[0].text.strip().split(' ')[-1]) ## number of pages with products
    next_url = soup.find('a', class_='andes-pagination__link shops__pagination-link ui-search-link')['href'] ## next page url

    return([n_pages,next_url])

def web_scrap_meli(main_url):
    urls = extract_products_urls(main_url) ## extracting products urls
    n_pages = get_n_pages(main_url)[0] 
    next_page_url_start = get_n_pages(main_url)[1].split('51')[0] ## next page url start
    next_page_url_end = get_n_pages(main_url)[1].split('51')[1] ## next page url end
    logging.info(f'{n_pages} pages!')
    for i in range(n_pages):
        if i == 0:
            url_page = main_url
            logging.info('URL')
            logging.info(url_page)
        else:
            n = (i * products_per_page) + 1            
            url_page = f'{next_page_url_start}{n}{next_page_url_end}'
            logging.info('URL')
            logging.info(url_page)
        urls = extract_products_urls(url_page)
        start = 1
        total = len(urls)
        for j in urls:
            logging.info(f'page: {i+1}/{n_pages} -- {start}/{total}')
            random_sleep(seconds_wait)
            extract_info_from_product_url(j) ## extrating infos from a product
            start += 1


if __name__ == '__main__':
    web_scrap_meli(main_url) ## run the main function to web scrap infos
    logging.info('End.')
    print('End.')
    