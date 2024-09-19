Title: Creating custom colour palettes in Tableau from the command-line
Date: 2024-04-30
Description: A command-line app to make it easier and quicker to add and edit custom colour palettes in Tableau.
Tags: Python, Tableau, data-visualisation, command-line

If you're anything like me most of the time Tableau's in-built colour palettes are more than suitable for the visualisation you're creating.
That said, I also quite like to create my own custom colour palettes for use in Tableau.

Unfortunately in order to create custom colour palettes in Tableau you have 
to find your `Preferences.tsp` file and then edit the XML:

```xml
<?xml version='1.0' encoding='utf-8'?>
<workbook>

<preferences>

<color-palette name="Forest" type="ordered-sequential">
<color>#132a13</color>
<color>#4f772d</color>
<color>#90a955</color>
</color-palette></preferences>
</workbook>
```

While this might be fine as a one-off, it gets unyieldy if you're constantly 
having to edit the XML to add or remove colours/palettes.

So I decided to create a command-line app to make it easier and quicker
to manage your custom colour palettes in Tableau.

Introducing `tab-pal`:

<p align="center">
    <a href="https://github.com/ben-n93/tab-pal">
        <img src="https://github.com/ben-n93/tab-pal/assets/84557025/d26de9c5-434e-4299-a35d-e97cb46ae57d" alt="tab-pal-demo">
    </a>
</p>

`tab-pal` will automatically search for your Preferences.tsp file and prompt you for the path to it.

Alternatively, and what is recommended, is to create an enviromental variable called `TAB_PAL_FILE`, which `tab-pal` will search for on launch. This will ensure you don't need to keep supplying the file path every time you launch `tab-pal`.

You can install via `pip` (although I recommend `pipx` so you use it regardless of which virtual environment is or isn't activated).

Here is the [Github repository](https://github.com/ben-n93/tab-pal).