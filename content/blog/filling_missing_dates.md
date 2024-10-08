Title: Data cleaning with SQL: filling missing dates
Date: 2024-09-19
Description: Data cleaning with SQL to fill missing dates/data clean in a dataset in Snowflake data warehouse. Two solutions (both using a recursive CTE) is presented.
Tags: SQL, Snowflake, data-cleaning

Filling in missing dates is a common data cleaning task that can be a bit of a curly problem when
taking into account different groups of data within a dataset.

To demonstrate this (and the solutions) I'll be using a table called `page_traffic`:

|DT|PAGE_NAME|PAGE_VIEWS|
|--|---------|----------|
|2024-09-01|Homepage|10|
|2024-09-02|Homepage|15|
|2024-09-05|Homepage|13|
|2024-09-02|International news|2|
|2024-09-08|International news|9|

What we want is a row for each missing date in this dataset:

|DATES_DT|PAGE_NAME|PAGE_VIEWS|
|--------|---------|--|
|2024-09-01|Homepage|10|
|2024-09-02|Homepage|15|
|2024-09-03|Homepage||
|2024-09-04|Homepage||
|2024-09-05|Homepage|13|
|2024-09-06|Homepage||
|2024-09-07|Homepage||
|2024-09-08|Homepage||
|2024-09-01|International news||
|2024-09-02|International news|2|
|2024-09-03|International news||
|2024-09-04|International news||
|2024-09-05|International news||
|2024-09-06|International news||
|2024-09-07|International news||
|2024-09-08|International news|9|

Note that this solution was developed using Snowflake but it should work for all RDBMs with some syntax adjustments.

Here's the code for creating the table and inserting the values:

```SQL
CREATE OR REPLACE TABLE PAGE_TRAFFIC(
	DT DATE,
	PAGE_NAME VARCHAR(100),
	PAGE_VIEWS NUMBER(38,0)
);

INSERT INTO PAGE_TRAFFIC (DT, PAGE_NAME, PAGE_VIEWS) VALUES('2024-09-01', 'Homepage', 10);
INSERT INTO PAGE_TRAFFIC (DT, PAGE_NAME, PAGE_VIEWS) VALUES('2024-09-02', 'Homepage', 15);
INSERT INTO PAGE_TRAFFIC (DT, PAGE_NAME, PAGE_VIEWS) VALUES('2024-09-05', 'Homepage', 13);
INSERT INTO PAGE_TRAFFIC (DT, PAGE_NAME, PAGE_VIEWS) VALUES('2024-09-02', 'International news', 2);
INSERT INTO PAGE_TRAFFIC (DT, PAGE_NAME, PAGE_VIEWS) VALUES('2024-09-08', 'International news', 9);
```

If you don't want to read the explanation you can jump straight to the [solutions](#codesolutions). 

## Generating the dates 

First let's use a recursive CTE to create the date range we're after:

```SQL
WITH RECURSIVE DATES AS 
(
SELECT DATE('2024-09-01') AS dt 
UNION ALL
SELECT DATEADD(DAY, 1, dt) AS dt 
FROM DATES 
WHERE dt < '2024-09-08'
)
SELECT * 
FROM DATES
;
```

|DT|
|--|
|2024-09-01|
|2024-09-02|
|2024-09-03|
|2024-09-04|
|2024-09-05|
|2024-09-06|
|2024-09-07|
|2024-09-08|

## Let's fill some gaps!

Let's focus just on the _Homepage_ rows for now.

Using a `RIGHT JOIN` we'll return every row from `DATES` and also return `PAGE_VIEWS` from `page_traffic` where they exist:

``` SQL
WITH RECURSIVE DATES AS 
(
SELECT DATE('2024-09-01') AS dt 
UNION ALL
SELECT DATEADD(DAY, 1, dt) AS dt 
FROM DATES 
WHERE DT < '2024-09-08'
)
SELECT 
DATES.DT
, PAGE_VIEWS -- NULL is returned if there is no match in DATES.
FROM page_traffic AS pt 
	RIGHT JOIN DATES -- All rows from this CTE will be returned, even if there is no match in page_traffic.
	ON pt.dt = dates.dt 
	AND page_name = 'Homepage'
;
```

Our missing dates have been added to the dataset:

|DT|PAGE_VIEWS|
|--|----------|
|2024-09-01|10|
|2024-09-02|15|
|2024-09-03||
|2024-09-04||
|2024-09-05|13|
|2024-09-06||
|2024-09-07||
|2024-09-08||

### Including additional columns

However we also want to include the `page_name` column.

Including the `page_name` column in our `SELECT` statement won't work with our current query because the `DATES` dataset only
has a match with rows in `page_traffic` that have the same date:

```SQL 
WITH RECURSIVE DATES AS  ... -- Truncuating this to make these code blocks more readable.
SELECT 
DATES.dt
, page_name
, page_views
FROM page_traffic AS pt 
	RIGHT JOIN DATES
	ON pt.dt = dates.dt 
	AND page_name = 'Homepage'
;
```

|DT|PAGE_NAME|PAGE_VIEWS|
|--|---------|----------|
|2024-09-01|Homepage|10|
|2024-09-02|Homepage|15|
|2024-09-03|||
|2024-09-04|||
|2024-09-05|Homepage|13|
|2024-09-06|||
|2024-09-07|||
|2024-09-08|||

To solve this problem we could harcode the value, use `COALESCE()` or a window function:

``` SQL
WITH RECURSIVE DATES AS  ...
SELECT 
DATES.dt
, 'Homepage' AS page_name
, COALESCE(page_name, 'Homepage') AS page_name_v2
, FIRST_VALUE(PAGE_NAME) IGNORE NULLS OVER (ORDER BY DATES.DT) AS page_name_v3
, PAGE_VIEWS
FROM page_traffic AS pt 
	RIGHT JOIN DATES
	ON pt.dt = dates.dt 
	AND page_name = 'Homepage'
;
```

However these solutions won't work considering that our dataset includes more than one unique value in the `page_name` column.

Remember, up until now I've just been focused on the _Homepage_ rows.

One solution would be to use `COALESCE` with a `SELECT` query for each unique group in `page_traffic` and use a `UNION ALL` to create a complete dataset...

```SQL
WITH RECURSIVE DATES AS ...
SELECT 
DATES.dt
, COALESCE(page_name, 'Homepage') AS page_name
, page_views
FROM page_traffic AS pt 
	RIGHT JOIN DATES
	ON pt.DT = dates.DT 
	AND page_name = 'Homepage'
UNION ALL 
SELECT 
DATES.DT
, COALESCE(page_name, 'International news') AS page_name
, page_views
FROM page_traffic AS pt 
	RIGHT JOIN DATES
	ON pt.dt = dates.dt 
	AND page_name = 'International news'
;
```

... however this is a cumbersome solution, particularly when there is a more elegant, dynamic solutions.
<a id="codesolutions"></a>
### Solution 1 

We want to ensure that every date/row from `DATES` is paired wth as many unique values as there are in our `page_traffic` table.

Once we've done this, we can deduplicate the data so that `page_views` data is only returned when it exists.

We can accomplish this by using a `CROSS JOIN` which will join each row in our `DATES` data with each row in our `page_views` table (resulting in what is known as a Cartesian product).

Let's examine what that looks like:

``` SQL
WITH RECURSIVE DATES AS ...
SELECT 
pt.*
, dates.dt as dates_dt -- Note I've renamed it this to make it a bit easier to understand.
FROM page_traffic AS pt 
	CROSS JOIN DATES 
ORDER BY page_name, pt.dt, dates.dt
;
```

|DT|PAGE_NAME|PAGE_VIEWS|DATES_DT|
|--|---------|----------|--|
|2024-09-01|Homepage|10|2024-09-01|
|2024-09-01|Homepage|10|2024-09-02|
|2024-09-01|Homepage|10|2024-09-03|
|2024-09-01|Homepage|10|2024-09-04|
|2024-09-01|Homepage|10|2024-09-05|
|2024-09-01|Homepage|10|2024-09-06|
|2024-09-01|Homepage|10|2024-09-07|
|2024-09-01|Homepage|10|2024-09-08|
|2024-09-02|Homepage|15|2024-09-01|
|2024-09-02|Homepage|15|2024-09-02|
|2024-09-02|Homepage|15|2024-09-03|
|2024-09-02|Homepage|15|2024-09-04|
|2024-09-02|Homepage|15|2024-09-05|
|2024-09-02|Homepage|15|2024-09-06|
|2024-09-02|Homepage|15|2024-09-07|
|2024-09-02|Homepage|15|2024-09-08|
|2024-09-05|Homepage|13|2024-09-01|
|2024-09-05|Homepage|13|2024-09-02|
|2024-09-05|Homepage|13|2024-09-03|
|2024-09-05|Homepage|13|2024-09-04|
|2024-09-05|Homepage|13|2024-09-05|
|2024-09-05|Homepage|13|2024-09-06|
|2024-09-05|Homepage|13|2024-09-07|
|2024-09-05|Homepage|13|2024-09-08|
|2024-09-02|International news|2|2024-09-01|
|2024-09-02|International news|2|2024-09-02|
|2024-09-02|International news|2|2024-09-03|
|2024-09-02|International news|2|2024-09-04|
|2024-09-02|International news|2|2024-09-05|
|2024-09-02|International news|2|2024-09-06|
|2024-09-02|International news|2|2024-09-07|
|2024-09-02|International news|2|2024-09-08|
|2024-09-08|International news|9|2024-09-01|
|2024-09-08|International news|9|2024-09-02|
|2024-09-08|International news|9|2024-09-03|
|2024-09-08|International news|9|2024-09-04|
|2024-09-08|International news|9|2024-09-05|
|2024-09-08|International news|9|2024-09-06|
|2024-09-08|International news|9|2024-09-07|
|2024-09-08|International news|9|2024-09-08|

If you find this confusing, just remember that every date in our date range (1st of September to 8th of September) has been joined to every row in our `page_traffic` table. Doing this means we can dynamically pair every date with as many unique values as there are in the `page_traffic` table.

For example, our 1st of September row in our `page_traffic` table has been duplicated 8 times, for every row in our `DATES` CTE.

If we were to ignore the `page_views` column our solution would be complete. We can just use the `DISTICT` keyword to only return unique rows:

``` SQL
WITH RECURSIVE DATES AS ...
SELECT 
DISTINCT 
DATES.dt
, PT.page_name 
FROM page_traffic AS pt 
	CROSS JOIN DATES 
ORDER BY page_name, dt 
;
```

|DT|PAGE_NAME|
|--|---------|
|2024-09-01|Homepage|
|2024-09-02|Homepage|
|2024-09-03|Homepage|
|2024-09-04|Homepage|
|2024-09-05|Homepage|
|2024-09-06|Homepage|
|2024-09-07|Homepage|
|2024-09-08|Homepage|
|2024-09-01|International news|
|2024-09-02|International news|
|2024-09-03|International news|
|2024-09-04|International news|
|2024-09-05|International news|
|2024-09-06|International news|
|2024-09-07|International news|
|2024-09-08|International news|

However of course we'll want to include `page_views` and this is where it gets a little trickier.

Let's use `2024-09-01` for the Homepage as an example:

``` SQL
WITH RECURSIVE DATES AS ...
SELECT 
dates.dt AS dates_dt
, pt.*
FROM page_traffic AS pt 
	CROSS JOIN DATES 
WHERE dates.dt = '2024-09-01'
AND page_name = 'Homepage'
ORDER BY page_name, pt.dt, dates.dt
;
```

|DATES_DT|DT|PAGE_NAME|PAGE_VIEWS|
|--------|--|---------|----------|
|2024-09-01|2024-09-01|Homepage|10|
|2024-09-01|2024-09-02|Homepage|15|
|2024-09-01|2024-09-05|Homepage|13|

We want to exclude the `page_views` for the `2024-09-02` and `2024-09-05` rows (as these are simply the product of joining `2024-08-01` to every row in `page_traffic`) and so let's use a `CASE` statement to do to do this:

```SQL
WITH RECURSIVE DATES ...
SELECT 
DISTINCT 
dates.dt AS dates_dt
, pt.page_name 
, CASE WHEN DATES.dt = PT.dt THEN page_views END AS pv
FROM page_traffic AS pt 
	CROSS JOIN DATES 
WHERE dates.dt = '2024-09-01'
AND page_name = 'Homepage'
;
```

|DATES_DT|PAGE_NAME|PAGE_VIEWS|
|--------|---------|----------|
|2024-09-01|Homepage|10|
|2024-09-01|Homepage||

Great! If page views exist for a date (as determined by our `CASE` statement) that's what will be returned.

Next we'll want to only include the date with a non-NULL `page_view` and we can accomplish this by using the `RANK()` window function:

```SQL
WITH RECURSIVE DATES ...
SELECT 
DISTINCT 
dates.dt AS dates_dt
, pt.page_name 
, CASE WHEN DATES.dt = PT.dt THEN page_views END AS pv -- Be sure to rename this column.
, RANK() OVER (PARTITION BY dates_dt, page_name ORDER BY pv) AS pv_ranking 
FROM page_traffic AS pt 
	CROSS JOIN DATES 
WHERE dates.dt = '2024-09-01'
AND page_name = 'Homepage'
;
```

|DATES_DT|PAGE_NAME|PV|PV_RANKING|
|--------|---------|--|-------|
|2024-09-01|Homepage|10|1|
|2024-09-01|Homepage||2|

As you can see, rows with a non-NULL value will always be ranked 1 and we just need to filter out rows without this rank.

What about dates on which there are no page views? `NULL` values will recieve the same rank but our `DISTINCT` keyword will take care of them (returning only 1 row).

And that's our first solution!

If you're using Snowflake or any other RDBMS where the `QUALIFY` clause is supported we can filter to rows ranked 1 without having to using an inline-view or additional CTE:

``` SQL
-- RDBMS with QUALIFY:
WITH RECURSIVE DATES AS 
(
SELECT DATE('2024-09-01') AS dt 
UNION ALL
SELECT DATEADD(DAY, 1, dt) AS dt 
FROM DATES 
WHERE dt < '2024-09-08'
)
SELECT 
DISTINCT 
dates.dt AS dates_dt
, pt.page_name
, CASE WHEN DATES.dt = PT.dt THEN page_views END AS pv
FROM page_traffic AS pt 
	CROSS JOIN DATES 
QUALIFY RANK() OVER (PARTITION BY dates_dt, page_name ORDER BY pv) = 1 
ORDER BY page_name, dates_dt
;

-- If QUALIFY is not supported:
WITH RECURSIVE DATES AS 
(
SELECT DATE('2024-09-01') AS dt 
UNION ALL
SELECT DATEADD(DAY, 1, DT) AS pt 
FROM DATES 
WHERE dt < '2024-09-08'
), 
final_dataset AS 
(
SELECT  
dates.dt AS dates_dt
, pt.page_name
, CASE WHEN DATES.DT = PT.DT THEN page_views END AS pv
, RANK() OVER (PARTITION BY dates_dt, page_name ORDER BY pv) AS pv_rank
FROM page_traffic AS pt 
	CROSS JOIN DATES 
)
SELECT 
DISTINCT 
dates_dt
, page_name
, pv
FROM final_dataset
WHERE pv_rank = 1 
ORDER BY page_name, dates_dt
;
```

|DATES_DT|PAGE_NAME|PV|
|--------|---------|--|
|2024-09-01|Homepage|10|
|2024-09-02|Homepage|15|
|2024-09-03|Homepage||
|2024-09-04|Homepage||
|2024-09-05|Homepage|13|
|2024-09-06|Homepage||
|2024-09-07|Homepage||
|2024-09-08|Homepage||
|2024-09-01|International news||
|2024-09-02|International news|2|
|2024-09-03|International news||
|2024-09-04|International news||
|2024-09-05|International news||
|2024-09-06|International news||
|2024-09-07|International news||
|2024-09-08|International news|9|

### Solution 2

Solution 2 involves the same approach, in that we're using a `CROSS JOIN` to make sure there is a row for every date in our range for every unique page name.
However we'll also use a `LEFT JOIN` to take out the manual work of evaluating whether a page view exists for a date.

By using an in-line view of distinct page names we can join every date in our range with all possible page names:

```SQL
WITH RECURSIVE DATES AS 
(
SELECT DATE('2024-09-01') AS dt 
UNION ALL
SELECT DATEADD(DAY, 1, dt) AS dt 
FROM DATES 
WHERE dt < '2024-09-08'
)
SELECT 
DISTINCT 
dates.dt AS dt
, pn.page_name
FROM DATES
	CROSS JOIN (SELECT DISTINCT page_name FROM page_traffic) AS pn
;
```

|dates_dt|page_name|
|--------|---------|
|2024-09-01|Homepage|
|2024-09-01|International news|
|2024-09-02|Homepage|
|2024-09-02|International news|
|2024-09-03|Homepage|
|2024-09-03|International news|
|2024-09-04|Homepage|
|2024-09-04|International news|
|2024-09-05|Homepage|
|2024-09-05|International news|
|2024-09-06|Homepage|
|2024-09-06|International news|
|2024-09-07|Homepage|
|2024-09-07|International news|
|2024-09-08|Homepage|
|2024-09-08|International news|

Next, let's `LEFT JOIN` to `page_traffic`. If a page view exists that's what
will be returned, otherwise `NULL` will be returned:

```SQL
WITH RECURSIVE DATES AS 
(
SELECT DATE('2024-09-01') AS dt 
UNION ALL
SELECT DATEADD(DAY, 1, dt) AS dt 
FROM DATES 
WHERE dt < '2024-09-08'
)
SELECT
dates.dt AS dates_dt
, pn.page_name
, pt.page_views as pv
FROM dates as dates
    CROSS JOIN (SELECT DISTINCT page_name FROM page_traffic) AS pn 
	LEFT join page_traffic as pt 
	ON pt.dt = dates.dt
	AND pt.page_name = pn.page_name
ORDER BY page_name, dates_dt
;
```

And that's it! 