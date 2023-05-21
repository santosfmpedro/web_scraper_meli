# Web Scraper Mercado Livre
Scraper to collect information about products on the cell phone offers page of Mercado Livre.

Repository description:
-----------
- data: 
    - Where products.parquet file is, with products informations collected.
- src:
    - main.py: file with the main code
- requirements.txt: necessary libraries 
- .gitignore
- README.md
- notebook.ipynb: Python notebook to check if all is working
- logs.log: logs from script 

Running the code
-----------

Clone this repository
```bash
git clone https://github.com/santosfmpedro/web_scraper_meli.git
```

Install libraries required
```bash
pip install -r requirements.txt
```

Run the web scraper script using the notebook.ipynb file.

The web scraper code takes approximately 16 minutes to run completely.

You can see the parquet file collected with notebook.ipynb.
