AUTHOR = "Ben Nour"
SITENAME = "Ben Nour"
SITEURL = 'https://ben-nour.com/'
SITETITLE = "Ben Nour"

PATH = "content"
STATIC_PATHS = ["images", "folium", "misc", 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

PLUGINS = ["sitemap"]

TIMEZONE = "Australia/Sydney"

DEFAULT_LANG = "en"

# Articles
#ARTICLE_PATHS = ['blog',]
#ARTICLE_URL = 'blog/{slug}.html'
#ARTICLE_SAVE_AS = 'blog/{slug}.html'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (("blog", "https://ben-nour.com/category/blog.html"),)

# Social widget
SOCIAL = (
    ("github", "https://github.com/ben-n93"),
    ("twitter", "https://twitter.com/ben_n_93"),
    ("medium", "https://medium.com/@ben.nour_68691"),
)

# Theme.
THEME = "/Users/benjaminnour/opt/anaconda3/envs/pelcian/lib/python3.10/site-packages/pelican/themes/Flex"

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

DISQUS_SITENAME = "ben-nour"
