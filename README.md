# Web Scraper Mercado Livre
Scraper to collect information about products on the cell phone offers page of Mercado Livre.


Firsts Steps
-----------

installing dependences 

```bash
pip install -r requirements.txt
```


Repository description:
- data: 
    - Where products.parquet file is, with products informations collected.
- src:
    - web_scraper_meli.py: file with the main code
    - aux_parquet.py: module created to help save parquet files
- requirements.txt: libraries necessary
- .gitignore
- README.md
- notebook.ipynb: Python notebook to check if all is working
