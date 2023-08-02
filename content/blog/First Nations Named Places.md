Title: Officially named places of First Nations origin in NSW, Australia
Date: 2023-08-01
Description: How I used Python to create an interactive map that shows places in NSW, Australia that have a name of First Nations origin.
Tags: geospatial-data, pandas, Python

<style>
    /* CSS code. */
    .iframe-container {
        position: relative;
        padding-bottom: 66.66%; /* 3:2 aspect ratio (100 * 2/3) */
        height: 0;
        overflow: hidden;
    }

    .iframe-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
</style>

Recently I was curious about the origin of my street name and my search online
led me to the [NSW Geographical Names Board](https://www.gnb.nsw.gov.au/),
a government body responsible for the management and administration of
geographic and place names within the state of New South Wales, Australia.

So not quite what I was looking for but I still found this to be a fascinating
data set, which is helpfully available as a [CSV file](https://proposals.gnb.nsw.gov.au/public/geonames/search) with all record information from the Geographical Name Register that the Board maintains.

The data set includes an ABORIGINAL NAME field and so I thought it would be
interesting to visualise how many places in NSW are of First
Nations origin vs not.

## How I did it

I used the ever fantastic [Folium](https://python-visualization.github.io/folium/) package
to visualise this data.

But before I could use Folium I needed a GeoJSON file
so what I did was write a Python script to take this CSV file and turn it in
to a GeoJSON file. You can find the script, which is executed daily (so the data is fresh and of use to anyone else out there), and GeoJSON
file in this [repo](https://github.com/ben-n93/NSW_Geographical_Name_Register_GeoJSON/tree/main).

## Data accuracy

I want to flag that I can't verify as to how accurate this data is.

The aforementioned ABORIGINAL NAME field is blank for many rows/places that, according to the MEANING or ORIGIN fields, are of First Nations origin.
I contacted the Board and they told me that the ABORIGINAL NAME field was *"...a recent edition to the Geographical Names Register (it was only added 2 years ago)."*. 

So what I've done is also included any places that, according to the MEANING or ORIGIN field, are of First Nations origin. 

Again, I can't speak to the accuracy of these fields - you can see my doubt when presented with descriptions like this:

<img src="{static}/images/tilcha_creek.jpg" alt="Screenshot of metadata about a geographical location (Tilcha Creek) with NSW, Australia that is of First Nations origin.">

However I've included these places anyway.

I've also only included places that have been officially 'assigned' by the Board.

You can read more about the different place designations [here](https://www.gnb.nsw.gov.au/__data/assets/pdf_file/0011/59627/Glossary_of_Designation_Values.pdf).

## Visualising the data

Originally I wanted to plot all the named places on a map however the Folium map created was so large
that it crashed my browser. I want to note that this is because of the large number
of places that are *not* of First Nations origin.

Creating a Folium map with places of First Nations origin was of no issue, size-wise:

<div class="iframe-container">
<iframe src="https://ben-nour.com/NSW_geographical_places.html" height="500" width="750"></iframe>
</div>


While I couldn't use Folium to show the vast number of named places that are not of
First Nations origin you can see it in this column chart:

<img src="{static}/images/nsw_geographical_places.png" alt="Screenshot of a column chart showing the number of places in NSW, Australia that
are of First Nations origin vs not." width="500" height="311.87">

If you want to see the Jupyter Notebook I used for this you can check it out
in this Github [repo](https://github.com/ben-n93/First_Nations_places_NSW).