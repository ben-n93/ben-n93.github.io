Title: Introducing Archer API
Date: 2023-04-22
Category: Blog
Tags: API, data-engineering

Introducing [Archer API](https://www.archerapi.com/), a REST API based on one of my favourite shows, the
adult animated spy comedy [Archer](https://www.imdb.com/title/tt1486217/).

Archer API provides JSON data about Archer's episodes, charactes and 
quotes.

For example, to get a random quote you can access the 
[archerapi.com/api/quotes/random](https://www.archerapi.com/api/quotes/random) endpoint:

```
{
    "character": "Sterling Malory Archer",
    "episode": "Mole Hunt",
    "id": 10,
    "quote": "Just the tip!"
}
```

## Data source/collection

I pulled the data for this API from two sources:

- [IMDb](https://www.imdb.com/), for episode metadata (episode name, season, airdate, etc)
- [Archer Fandom](https://archer.fandom.com/wiki/Archer_Wiki), for everything else (character names, jobs, voice actor, etc)

For both sources I used Python to get the data. I used the fantastic [cinemagoer](https://pypi.org/project/cinemagoer/)
to access IMDb data and the [requests](https://requests.readthedocs.io/en/latest/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) packages for scraping/parsing Archer Fandom.

I then insert this data into a [SQLite](https://www.sqlite.org/index.html) database. I chose SQLite primarily because
Python has inbuilt support for it with their `sqlite` module and it can be embedded directly in an application.

## Data transformation

Using [Dbeaver](https://dbeaver.io/), I connected to the SQLite database and did all of my
data transformation and cleaning directly in the database. 

As Archer Fandom is maintained 
by fans there was some inconsistency with the spelling of actor names, the use of 
Roman numerals vs integers for multiple-part episodes (*Heart of Archness: Part II* vs *Heart of Archness: Part 2*)
and so on.

## Building and hosting the API

I built the API using [Flask](https://flask.palletsprojects.com/en/2.3.x/). This was my first time 
using this framework and I was really impressed with the documentation and 
how simple it was to get it up and running. 

I hosted the Flask application using [Heroku](https://www.heroku.com/). Again, this was my first time
using Heroku and I'll definitely be using it again with future projects.

For the front-end of my website I used a [Boostrap](https://getbootstrap.com/) template, the HTML of which I modified 
to add some custom styling and other stuff, like a Google Analytics tag.

You can read the full source code for this project in my [Github repo](https://github.com/ben-n93/archer_api).









