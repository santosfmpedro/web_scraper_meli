# Web Scraper Mercado Livre
Scraper to collect information about products on the cell phone offers page of Mercado Livre.


Repository description:
-----------
- data: 
    - Where products.parquet file is, with products informations collected.
- src:
    - web_scraper_meli.py: file with the main code
    - aux_parquet.py: module created to help save parquet files
- requirements.txt: libraries necessary
- .gitignore
- README.md
- notebook.ipynb: Python notebook to check if all is working

Firsts Steps
-----------

clone this repository
```bash
git clone https://github.com/santosfmpedro/web_scraper_meli.git
```

change de directory 
```bash
cd web_scraper_meli
```

installing dependences 

```bash
pip install -r requirements.txt
```

Running the scrapper script

```bash
python3 src/web_scraper_meli.py
```

