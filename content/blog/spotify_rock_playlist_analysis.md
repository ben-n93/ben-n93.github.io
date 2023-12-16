Title: Using Spotify's Web API to analyse my Favourite Rock playlist
Date: 2023-11-11
Description: Using Python and Spotify's WebAPI to learn interesting facts about my Favourite Rock playlist. The pandas library is used
to clean and analyse the data.
Tags: data-analysis, data-visualisation, Python, pandas

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TFP90633KX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-TFP90633KX');
</script>

Since 2015 I've been adding my most-liked rock songs to the aptly named playlist *Favourite Rock*.


I thought it'd be fun to use content metadata from Spotify's [Web API](https://developer.spotify.com/documentation/web-api) to learn more about my taste in rock music, such as favourite music era and how often I've added to the playlist over the years.


```python
import os

import requests
import pandas as pd
```

## Getting the data


```python
# Getting the API access token.
url = "https://accounts.spotify.com/api/token"

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "client_credentials",
    "client_id": os.environ['SPOTIFY_CLIENT_ID'],
    "client_secret": os.environ['SPOTIFY_CLIENT_SECRET']
}

response = requests.post(url, headers=headers, data=data)
token = response.json()['access_token']
```

The **[Get Playlist Items](https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks)** endpoint returns a maximum of 50 items (tracks/songs). 

However in the API call you can specify the index of the first item to return, a parameter which you can take advantage of to make multiple API calls to capture all songs on the playlist:


```python
# Getting all the songs in my Favourite Rock playlist.
headers = {
    "Authorization": f"Bearer {token}"
}

tracks = []
for number in range(0, 520, 50):
    response = requests.get(f"https://api.spotify.com/v1/playlists/{os.environ['PLAYLIST_ID']}/tracks?limit=50&offset={number}", headers=headers)
    data = response.json()
    tracks = tracks + (data['items'])

# Double check that my list contains all the playlist songs.
data['total'] == len(tracks) 
```




    True



## Transforming the data
Not all of the metadata returned from the API is relevant, as you can infer from a look at the following JSON keys (for example, 'video_thumbnail'), or structured in a way that can be passed to a pandas DataFrame immediately. 


```python
tracks[0].keys()
```




    dict_keys(['added_at', 'added_by', 'is_local', 'primary_color', 'track', 'video_thumbnail'])



The artist name is nested with the 'artists' key.


```python
tracks[0]['track']['artists']
```




    [{'external_urls': {'spotify': 'https://open.spotify.com/artist/6bUJpbekaIlq2fT5FMV2mQ'},
      'href': 'https://api.spotify.com/v1/artists/6bUJpbekaIlq2fT5FMV2mQ',
      'id': '6bUJpbekaIlq2fT5FMV2mQ',
      'name': 'Wavves',
      'type': 'artist',
      'uri': 'spotify:artist:6bUJpbekaIlq2fT5FMV2mQ'}]




```python
# Creating a list of track dictionaries.
new_tracks = []
for track in tracks:
    new_track = track['track']
    new_track['added_at'] = track['added_at']
    new_track['release_date'] = track['track']['album']['release_date']
    new_track['artist_name'] = track['track']['artists'][0]['name']
    new_tracks.append(new_track)
```


```python
df = pd.DataFrame(new_tracks)
# Keeping only relevant columns.
df = df[['artist_name', 'name', 'duration_ms', 'release_date', 'added_at']]
df= df.rename(columns={'name':'track_name'})
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>artist_name</th>
      <th>track_name</th>
      <th>duration_ms</th>
      <th>release_date</th>
      <th>added_at</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Wavves</td>
      <td>Way Too Much</td>
      <td>153640</td>
      <td>2015-07-21</td>
      <td>2015-11-01T13:20:26Z</td>
    </tr>
    <tr>
      <th>1</th>
      <td>The Rubens</td>
      <td>Hoops</td>
      <td>158973</td>
      <td>2015-08-07</td>
      <td>2015-11-01T13:17:48Z</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Lurch &amp; Chief</td>
      <td>Keep It Together</td>
      <td>236280</td>
      <td>2014-10-17</td>
      <td>2015-11-01T13:23:21Z</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Violent Soho</td>
      <td>Covered in Chrome</td>
      <td>212546</td>
      <td>2013-09-06</td>
      <td>2015-11-03T07:05:03Z</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Foo Fighters</td>
      <td>Everlong</td>
      <td>250546</td>
      <td>1997-05-20</td>
      <td>2015-11-01T13:17:59Z</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>515</th>
      <td>Ainslie Wills</td>
      <td>Drive</td>
      <td>301910</td>
      <td>2015-09-14</td>
      <td>2023-11-05T12:28:19Z</td>
    </tr>
    <tr>
      <th>516</th>
      <td>Sonic Youth</td>
      <td>Sunday</td>
      <td>292306</td>
      <td>1998-01-01</td>
      <td>2023-11-05T12:31:29Z</td>
    </tr>
    <tr>
      <th>517</th>
      <td>Brand New</td>
      <td>The Quiet Things That No One Ever Knows</td>
      <td>241640</td>
      <td>2003</td>
      <td>2023-11-05T12:36:23Z</td>
    </tr>
    <tr>
      <th>518</th>
      <td>Chastity Belt</td>
      <td>Lydia</td>
      <td>239826</td>
      <td>2015-03-23</td>
      <td>2023-11-05T12:40:02Z</td>
    </tr>
    <tr>
      <th>519</th>
      <td>The Velvet Underground</td>
      <td>Oh! Sweet Nuthin'</td>
      <td>444778</td>
      <td>1970</td>
      <td>2023-11-07T08:31:32Z</td>
    </tr>
  </tbody>
</table>
<p>520 rows × 5 columns</p>
</div>



## Data analysis

Now that we have a pandas DataFrame I can start doing some data analysis.

### Which artist appears the most frequently?
I was curious to see which artist has the most songs featured on the playlist.

Unsuprisingly it was my favourite band - Nirvana!


```python
most_popular_artists = df['artist_name'].value_counts()
most_popular_artists.head(1)
```




    artist_name
    Nirvana    15
    Name: count, dtype: int64



### What is the shortest and longest song in the playlist?


```python
# Creating a more readable song length column.
df['song_length'] = round(df['duration_ms'] / 60000, 2)
```


```python
max_length_index = df['song_length'].idxmax()
max_song = df.loc[max_length_index]
print(f"Song: {max_song.iloc[1]}, Artist: {max_song.iloc[0]}, Song length: {max_song.iloc[5]}")
```

    Song: Beach Life-In-Death, Artist: Car Seat Headrest, Song length: 13.31


13 minutes!


```python
min_length_index = df['song_length'].idxmin()
min_song = df.loc[min_length_index]
print(f"Song: {min_song.iloc[1]}, Artist: {min_song.iloc[0]}, Song length: {min_song.iloc[5]}")
```

    Song: We See U, Artist: Speed, Song length: 1.06


### How many songs have I added to the playlist over the years?
I was curious to see if I added a similar number of songs per year since creating the playlist.


```python
df['year_added'] = df['added_at'].str[:4] # Creating a year_added column.
songs_per_years = df['year_added'].value_counts().sort_index()
songs_per_years.plot()
```




    <Axes: xlabel='year_added'>


<img src="{static}/images/output_20_1.png">
    


### What era of rock music is most represented?
Perhaps unsuprisingly given my age (30 at time of writing), the 2010s were the most popular decade when looking at the number of songs added to the playlist by decade released.


```python
df['release_date_decade'] = df['release_date'].str[:3] + "0s"
rock_era_song_count = df['release_date_decade'].value_counts().sort_index()
rock_era_song_count.plot(kind="bar", rot=0)
```




    <Axes: xlabel='release_date_decade'>



    
<img src="{static}/images/output_22_1.png">

    


### Looking at each era individually, which artist had the most songs featured in my playlist?


```python
era_artists = df.groupby(['release_date_decade', 'artist_name']).size().reset_index(name='song_count')
max_count_id = era_artists.groupby('release_date_decade')['song_count'].idxmax()
top_artists_per_era = era_artists.loc[max_count_id]
top_artists_per_era
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>release_date_decade</th>
      <th>artist_name</th>
      <th>song_count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1960s</td>
      <td>The Beatles</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1970s</td>
      <td>David Bowie</td>
      <td>2</td>
    </tr>
    <tr>
      <th>15</th>
      <td>1980s</td>
      <td>Descendents</td>
      <td>5</td>
    </tr>
    <tr>
      <th>44</th>
      <td>1990s</td>
      <td>Nirvana</td>
      <td>10</td>
    </tr>
    <tr>
      <th>87</th>
      <td>2000s</td>
      <td>NOFX</td>
      <td>8</td>
    </tr>
    <tr>
      <th>283</th>
      <td>2010s</td>
      <td>Violent Soho</td>
      <td>8</td>
    </tr>
    <tr>
      <th>294</th>
      <td>2020s</td>
      <td>Amyl and The Sniffers</td>
      <td>6</td>
    </tr>
  </tbody>
</table>
</div>



## Conclusion

Some interesting insights came out of this analysis, my favourites of which include:

- The longest song on my playlist is over 13 minutes long and the shortest is just over a minute long.

- The 2010s are my favourite era of rock music, going off of the number of songs from each decade of rock music.

- I added the most songs to the playlist in 2016 but since 2020 I've been adding more and more songs every year. 

Thanks for reading!

You can find this Jupyter Notebook in this [Github repo](https://github.com/ben-n93/spotify_rock_playlist_analysis).
