Title: Reducing the size of GeoJSON files with geojson-shave
Date: 2024-03-30
Description: A command-line tool (written in Python) for reducing the file size of GeoJSON files.
Tags: geospatial data, Python, regex

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TFP90633KX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-TFP90633KX');
</script>

<p align="center">
    <a href="https://pypi.python.org">
        <img src="https://ben-nour.com/images/geojson-shave.png" alt="GeoJSON-shave" style="width: 60%; height: auto"/>
    </a>
</p>

Giant GeoJSON files can be a nightmare, crashing your IDE,
GIS software or browser (and potentially causing you to tear your hair out in frustration!).

I use GeoJSON files [quite often](https://ben-nour.com/where-are-australias-existingproposed-oil-and-gas-pipelines-located.html) so I decided to create a command-line tool that reduces the size of GeoJSON files.

<br>

<p align="center">
    <a href="https://pypi.python.org">
        <img src="https://ben-nour.com/images/demo.gif" alt="GeoJSON-shave-demo" style="width: 60%; height: auto"/>
    </a>
</p>

You can view the project homepage [here](https://github.com/ben-n93/geojson-shave).

You can install the tool using pip:

```
$ pip install geojson-shave
```

## Usage

`geojson-shave` reduces the size of GeoJSON files by truncating latitude/longitude coordinates to the specified decimal places,
eliminating unnecessary whitespace and (optionally) replacing the properties key's value with null/empty dictionary.

Simply pass the file path of your GeoJSON file and it will truncuate the coordinates to 5 decimal places, outputing to the current working directory:

```sh
$ geojson-shave roads.geoson
```

Alterntatively you can specify the number of decimal points you want the coordiantes truncuated to:

```sh
$ geojson-shave roads.geojson -d 3
```

You can also specify if you only want certain Geometry object types in the file to be processed:

```sh
$ geojson-shave roads.geojson -g LineString Polygon
```

Note that the -g option doesn't apply to objects nested within Geometry Collection.

And to reduce the file size even further you can nullify the property value of Feature objects:

```sh
$ geojson-shave roads.geojson -p
```

Output to a directory other than the current working directory:
```sh
$ geojson-shave roads.geojson -o ../data/output.geojson
```

## How I did it

To fully understand how the command-line tool works you can read the [source code](https://github.com/ben-n93/geojson-shave/)
but to truncuate coordinates I used a recursive function with regex:

```python
def _create_coordinates(coordinates, precision):
    """Create truncuated coordinates."""
    new_coordinates = []
    for item in coordinates:
        if isinstance(item, list):
            new_coordinates.append(_create_coordinates(item, precision))
        else:
            item = re.search(rf"[\-]?[0-9]+\.[0-9]{{0,{precision}}}", str(item)).group()
            new_coordinates.append(float(item))
    return new_coordinates
```

Because there are different types of GeoJSON Geometry objects with
varying levels of nested coordinates, recursion was critical to traversing these
hierarchial data structures.

For example, you can see the difference between a Point and Polygon objects' coordinates:

```json
{
         "type": "Point",
         "coordinates": [100.0, 0.0]
     },
{
         "type": "Polygon",
         "coordinates": [
             [
                 [100.0, 0.0],
                 [101.0, 0.0],
                 [101.0, 1.0],
                 [100.0, 1.0],
                 [100.0, 0.0]
             ],
             [
                 [100.8, 0.8],
                 [100.8, 0.2],
                 [100.2, 0.2],
                 [100.2, 0.8],
                 [100.8, 0.8]
             ]
         ]
     }
```

I used regex to truncuate the longitude/latitude values because it's so effective and easy!
