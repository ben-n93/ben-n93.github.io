Title: Splitting a delimited string column into rows using Snowflake
Date: 2023-07-20
Description: Using a SQL LATERAL JOIN in Snowflake to split a delimited string column into rows.
Tags: SQL, Snowflake

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TFP90633KX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-TFP90633KX');
</script>

Do you have a column in your Snowflake table that contains delimited strings that you want to split into individual rows?

For example, let’s say we have a table called `countries_official_languages`, which has two columns: `country` and `official_languages`.

The data might look something like this:

<p align="center">
    <a href="">
        <img src="https://ben-nour.com/images/snowflake-1.webp" alt="A table in Snowflake data warehouse." style="width: 60%; height: auto"/>
    </a>
</p>

However we want each unique language to be on its own row:

<p align="center">
    <a href="">
        <img src="https://ben-nour.com/images/snowflake-2.webp" alt="A table in Snowflake data warehouse." style="width: 60%; height: auto"/>
    </a>
</p>

You can do this in Snowlake by taking advantage of the `SPLIT_TO_TABLE` function and `LATERAL` keyword.

## SPLIT_TO_TABLE

Snowflake offers the handy `SPLIT_TO_TABLE` function, which *“splits a string (based on a specified delimiter) and flattens the results into rows.”*

Here’s an example of it in use:

Output:

```
+-------+
| VALUE |
|-------|
| Arabic|
| Berber|
+-------+
```

However, as the Snowflake documentation points out, *“table functions are used in the FROM clause of a SQL statement”.*

We need to execute the `SPLIT_TO_TABLE` for each row in our `countries_official_languages` table. Plus, we need the country column included also so we know which languages belong to which countries.

How do we do this? Using a `LATERAL` join.

### LATERAL JOIN

A lateral join is different from a regular join like `INNER JOIN` OR `LEFT JOIN` in that it *“allows an inline view to reference columns from a table expression that precedes that inline view.”*

That inline view can be a subquery, table function or an inline view (a view defined within the statement, and valid only for the duration of the statement).

If you're confused what’s important to understand is what happens when you use `LATERAL`:

```
for each row in left_hand_table LHT:
    execute right_hand_subquery RHS using the values from 
                                    the current row in the LHT
```

As you might have guessed, we can take advantage of the `LATERAL` keyword in order to execute the `SPLIT_TO_TABLE` function for each row in our `countries_official_languages` table:

``` SQL 
SELECT country, TRIM(VALUE) AS language
FROM countries_official_languages, -- Don't forgot the comma!
LATERAL SPLIT_TO_TABLE(official_languages, ',')
```

Let’s examine this in more detail. Let’s take the first row in our table as an example of what happens when we execute the above query:

```
|country|official_languages|
|-------|------------------|
|Algeria|Arabic, Berber    |
```

1) This row is passed to the right-hand inline view, which is in this case is a table function — `SPLIT_TO_TABLE`.

2) The table function returns two rows, for Arabic and Berber, in a column called `VALUE`.

3) In our `SELECT` statement we select the country column and the `VALUE` column. I’ve wrapped the `TRIM` function around the `VALUE` column to remove any whitespace.

4) This final result set is appended to what will be the final output once every row from the table has been processed.

And here is our final output:

<p align="center">
    <a href="">
        <img src="https://ben-nour.com/images/snowflake-2.webp" alt="A table in Snowflake data warehouse." style="width: 60%; height: auto"/>
    </a>
</p>

And that's it!

