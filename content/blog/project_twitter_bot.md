Title: How I created a Twitter bot that posts about science fiction books
Date: 2023-03-31
Description: How I used Python/Github to create an automated Twitter bot to post about science fiction books from Project Gutenberg's collection of public domain works.
Tags: twitter-bot, data-engineering, SQL

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TFP90633KX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-TFP90633KX');
</script>

<style>
img {
  border: 1px solid #BFBFBF;
}
</style>

As an avid reader I thought it would be cool to combine my love of literature and
data to create a [Twitter bot](https://twitter.com/Gutenberg_SciFi) that 
posts about sci-fi books :

<p align="center">
    <a href="https://pypi.python.org">
        <img src="https://ben-nour.com/images/pg_twitter_bot.webp" alt="Twitter-bot" style="width: 60%; height: auto"/>
    </a>
</p>

Specifically I wanted to recommend science fiction books that you could read 
free of charge, something made possible thanks to 
[Project Gutenberg](https://www.gutenberg.org/), a volunteer-run organisation 
that hosts a collection of public domain works.

## Data source/collection

PG very helpfully offers a [CSV feed](https://www.gutenberg.org/cache/epub/feeds/),
which I used to download sci-fi books from their catalog and upload to a SQLite database:

``` py
import csv
import io
import sqlite3

import requests

SQL = """
INSERT INTO books_catalog (book_id, title, authors)
VALUES (?, ?, ?)
"""

response = requests.get(URL, stream=True, timeout=240)
content = response.content.decode("utf-8")
csv_file = io.StringIO(content)
csv_reader = csv.reader(csv_file)
sf_books = [
    row for row in csv_reader if row[1] == "Text" and "Science Fiction" in row[8]
]
processed_sf_books = []
for book in sf_books:
    processed_book = []
    for index, field in enumerate(book):
        if index in (0, 3, 5):
            field = field.replace("\n", " ")
            field = field.replace("\r", "")
            processed_book.append(field)
    processed_sf_books.append(processed_book)

with sqlite3.connect(database) as conn:
    cursor = conn.cursor()
    cursor.executemany(SQL, processed_sf_books)
    conn.commit()

```

Here's a snippet of the catalog:

|   Text#  |   Type  |   Issued      |   Title             |   Language  |   Authors                           |   Subjects                                                                                                                                                                     |   LoCC  |   Bookshelves                         |
|----------|---------|---------------|---------------------|-------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|---------------------------------------|
|   64     |   Text  |   1993-05-01  |   The Gods of Mars  |   en        |   Burroughs, Edgar Rice, 1875-1950  |   Science fiction; Mars (Planet) -- Fiction; Life on other planets -- Fiction; Carter, John (Fictitious character) -- Fiction; Dejah Thoris (Fictitious character) -- Fiction  |   PS    |   Science Fiction                     |
|   155    |   Text  |   2006-01-12  |   The Moonstone     |   en        |   Collins, Wilkie, 1824-1889        |   England -- Fiction; Country homes -- Fiction; Police -- England -- Fiction; Jewelry theft -- Fiction; East Indians -- England -- Fiction; Mystery fiction                    |   PR    |   Detective Fiction; Mystery Fiction  |
|          |         |               |                     |             |                                     |                                                                                                                                                                                |         |                                       |

### Cleaning the data

The Authors field metadata is in the "surname-first" format (used in academic and scientific writing), which is unfortunately
not as readable for the intended end user of this bot:

For example:

|   Text#  |   Title          |   Authors                                                              |
|----------|------------------|------------------------------------------------------------------------|
|   28767  |   The Defenders  |   Dick, Philip K., 1928-1982; Emshwiller, Ed, 1925-1990 [Illustrator]  |
|          |                  |                                                                        |

In order to clean this data, I created a `clean_authors()` function that takes advantage of regex:

``` python
def clean_authors(authors):
    """Clean the authors string into a more
    readable string."""
    authors = [re.sub("[0-9]{4}-[0-9]{4}", "", author) for author in authors.split(";")]
    cleaned_authors = []
    for author in authors:
        author = author.split(",")
        stripped_authors = [creator.strip() for creator in author if creator != (" ")]
        if "[Illustrator]" in stripped_authors:
            del stripped_authors[stripped_authors.index("[Illustrator]")]
            stripped_authors.reverse()
            stripped_authors.append("[Illustrator]")
        else:
            stripped_authors.reverse()
        stripped_authors = " ".join(stripped_authors)
        cleaned_authors.append(stripped_authors)
    cleaned_authors = " and ".join(cleaned_authors)
    return cleaned_authors
```

Using our *The Defenders* example from before, here is the cleaned data:

<p align="center">
    <a href="https://pypi.python.org">
        <img src="https://ben-nour.com/images/twitter_cleaned_data_example.webp" alt="Twitter-bot" style="width: 60%; height: auto"/>
    </a>
</p>

## Choosing a book to post about

I won't go into great detail but I utilised SQL to a great extent throughout the script, including
an anti-join to get a list of books that had not yet been posted about:

```SQL
SELECT 
BC.*
FROM books_catalog bc 
	LEFT JOIN books_posted bp 
	ON bc.BOOK_ID = bp.BOOK_ID
	OR BC.TITLE = BP.TITLE 
WHERE BP.BOOK_ID IS NULL
```

### Automation

In order to make my Twitter bot automatically post a random book recommendation twice a day (at 7am and 7pm UTC time), I utilized Github Actions to create a customized workflow. This allowed me to automate the process of selecting and posting a book recommendation without the need for manual intervention:

``` yaml
name: Post book tweet

on: 
  schedule: 
  - cron: "0 7 * * *"
  - cron: "0 19 * * *"

permissions: write-all

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Install Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Checkout repository content
      uses: actions/checkout@master
    - name: Install requirements.txt
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Set enviromental secrets and execute twitter_bot.py
      env:
          PG_TWITTER_ACCESS_TOKEN: ${{ secrets.PG_TWITTER_ACCESS_TOKEN }}
          PG_TWITTER_ACCESS_TOKEN_SECRET: ${{ secrets.PG_TWITTER_ACCESS_TOKEN_SECRET }}
          PG_TWITTER_BEARER_TOKEN: ${{ secrets.PG_TWITTER_BEARER_TOKEN }}
          PG_TWITTER_CONSUMER_KEY: ${{ secrets.PG_TWITTER_CONSUMER_KEY }}
          PG_TWITTER_CONSUMER_SECRET: ${{ secrets.PG_TWITTER_CONSUMER_SECRET }}
      run: |
          python src/twitter_bot.py
    - name: update repo
      run: |
        git config user.email ${{ secrets.EMAIL }}
        git config user.name "Ben"
        git config user.username ben-n93
        git config user.password ${{ secrets.PERSONAL_ACCESS_TOKEN}}
        git add --all
        git commit -m "update"
        git push
```

In order to ensure that my Twitter bot could post about any new sci-fi books added to the PG catalog, I also used GitHub Actions to automate the extraction of the catalog data on the first day of every month (I won't include the YAML file here but you can view it in my repo).

You can view the full source code on [Github](https://github.com/ben-n93/project_guntenberg_sf_twitterbot).