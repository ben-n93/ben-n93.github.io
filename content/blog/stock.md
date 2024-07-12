Title: Using SQL to calculate how often and how many days an item is out of stock
Date: 2024-07-02
Description: Using SQL in the PostgreSQL database to calculate how often and how many days a store's inventory is out of stock.
Tags: SQL, PostgreSQL

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TFP90633KX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-TFP90633KX');
</script>

Recently a Reddit user posted in r/SQL wanting to know how to calculate 
how often and how many days an item was out of stock.

I enjoyed coming up with a solution and so I've decided to explore my answer
in more detail on this website.

Note that I'll be using PostgreSQL.

## The data

First, the dataset we'll be operating on:

|item|transaction_date|inventory_level|
|----|----------------|---------------|
|Bicycle|2024-01-01|0|
|Bicycle|2024-01-05|0|
|Bicycle|2024-01-10|10|
|Bicycle|2024-01-15|5|
|Bicycle|2024-01-16|0|
|Bicycle|2024-01-20|0|
|Bicycle|2024-01-23|0|
|Bicycle|2024-01-25|0|
|Bicycle|2024-01-28|20|
|Bicycle|2024-01-29|12|
|Bicycle|2024-01-31|0|

The original poster explained that a record is created in the database
(1st Jan 2024) before inventory is recieved for an item.

The other records in the dataset are when a count of inventory is conducted.

It's worth noting that each row in our dataset is when an inventory check 
was made so it is possible that bicycles could have come in and out of stock
between inventory checks. However that's a data entry problem, not ours. We can only
work with the data we've been given!

If you want to follow along in Postgres you can find the code to create the 
table and insert the data [here](https://gist.github.com/ben-n93/9c59e49f231ad131dfa0300f30d85332).

## The challenge

We want to find out how often our store was out of stock of bicycles and for how may days.

### Counting from the right start date

We only want to start counting from when inventory is first recieved, NOT when
the item is first entered into the system or when an inventory count is conducted before stock has ever 
been recieved.

We can do this by using a correlated subquery:

```SQL
SELECT A.*
FROM STOCK AS A 
WHERE A.TRANSACTION_DATE >= 
	(
	SELECT MIN(B.TRANSACTION_DATE)
	FROM STOCK AS B
	WHERE B.ITEM = A.ITEM 
	AND B.INVENTORY_LEVEL != 0
	)
```

__Result set__:

|item|transaction_date|inventory_level|
|----|----------------|---------------|
|Bicycle|2024-01-10|10|
|Bicycle|2024-01-15|5|
|Bicycle|2024-01-16|0|
|Bicycle|2024-01-20|0|
|Bicycle|2024-01-23|0|
|Bicycle|2024-01-25|0|
|Bicycle|2024-01-28|20|
|Bicycle|2024-01-29|12|
|Bicycle|2024-01-31|0|

### Calculating how many times bicycles were sold out
Next, let's identify when the bicycle goes out of stock.

How do we do this?

It's simple enough to assert by verifying how much inventory is on hand:

```SQL
CASE WHEN INVENTORY_LEVEL = 0 THEN 'OUT OF STOCK' ELSE 'IN STOCK' END
```

However we want to calculate how often an item goes out of stock so to do this
what we'll want to do is identify when an item goes out of stock after having
previously had stock.

In other words, we want to capture every instance in which on the last
inventory count day there was stock and on the current counting day there was
no stock.

We can achieve this using the `LAG()` window function to see how much inventory there was on the previous day:

```SQL
SELECT
A.*
, CASE 
	WHEN A.INVENTORY_LEVEL = 0 -- No stock!
	and LAG(INVENTORY_LEVEL, 1) OVER (PARTITION BY ITEM ORDER BY TRANSACTION_DATE) != 0 -- The previous day there WAS stock.
	THEN 'OUT_OF_STOCK' 
	WHEN A.INVENTORY_LEVEL != 0 THEN 'IN STOCK'
END AS STOCK_STATUS
FROM STOCK AS A 
WHERE A.TRANSACTION_DATE >= 
	(
	SELECT MIN(B.TRANSACTION_DATE)
	FROM STOCK AS B
	WHERE B.ITEM = A.ITEM 
	AND B.INVENTORY_LEVEL != 0
	)
```

The __Result set__:

|item|transaction_date|inventory_level|stock_status|
|----|----------------|---------------|------------|
|Bicycle|2024-01-10|10|IN STOCK|
|Bicycle|2024-01-15|5|IN STOCK|
|Bicycle|2024-01-16|0|OUT_OF_STOCK|
|Bicycle|2024-01-20|0|[NULL]|
|Bicycle|2024-01-23|0|[NULL]|
|Bicycle|2024-01-25|0|[NULL]|
|Bicycle|2024-01-28|20|IN STOCK|
|Bicycle|2024-01-29|12|IN STOCK|
|Bicycle|2024-01-31|0|OUT_OF_STOCK|

Perfect! We can see that twice bicycles have gone out of stock.

### Calculating how long bicycles were sold out

Next, let's calculate how long bicycles were sold out for.

All we need to do is calculate the difference in days between when an item 
was flagged as having gone out of stock and when it 
next came into stock.

This is simple enough using the `LEAD()` window function, which we can use 
to return the next transcation date.

```SQL
SELECT 
*
, COALESCE(LAG(TRANSACTION_DATE,1) OVER (PARTITION BY ITEM ORDER BY TRANSACTION_DATE DESC), CURRENT_DATE)
- TRANSACTION_DATE AS DAYS_OUT_OF_STOCK
FROM 
(
	SELECT
	A.*
	, CASE 
		WHEN A.INVENTORY_LEVEL = 0 
		AND LAG(INVENTORY_LEVEL, 1) OVER (PARTITION BY ITEM ORDER BY TRANSACTION_DATE) != 0 
		THEN 'OUT_OF_STOCK' 
		WHEN A.INVENTORY_LEVEL != 0 THEN 'IN STOCK'
	END AS STOCK_STATUS
	FROM STOCK AS A 
	WHERE 
	A.TRANSACTION_DATE >= 
		(
		SELECT MIN(B.TRANSACTION_DATE)
		FROM STOCK AS B
		WHERE B.ITEM = A.ITEM 
		AND B.INVENTORY_LEVEL != 0
		)
) C
WHERE STOCK_STATUS IS NOT NULL
ORDER BY 2
```

__Result set__:

|item|transaction_date|inventory_level|stock_status|days_out_of_stock|
|----|----------------|---------------|------------|-----------------|
|Bicycle|2024-01-10|10|IN STOCK|5|
|Bicycle|2024-01-15|5|IN STOCK|1|
|Bicycle|2024-01-16|0|OUT_OF_STOCK|12|
|Bicycle|2024-01-28|20|IN STOCK|1|
|Bicycle|2024-01-29|12|IN STOCK|2|
|Bicycle|2024-01-31|0|OUT_OF_STOCK|153|

Perfect!

We have our answer.

The Redditor who I helped asked for a single row per item which broke out how many
times the item was out of stock and for how long (in a comma-seperated string) so let's do that:

```SQL
SELECT   
ITEM
, COUNT(STOCK_STATUS) AS TIMES_OUT_OF_STOCK
, STRING_AGG(DAYS_OUT_OF_STOCK::VARCHAR, ',') AS DAYS_OUT_OF_STOCK
FROM 
	(
	SELECT 
	*
	, COALESCE(LAG(TRANSACTION_DATE,1) OVER (PARTITION BY ITEM ORDER BY TRANSACTION_DATE DESC), CURRENT_DATE)
	- TRANSACTION_DATE AS DAYS_OUT_OF_STOCK
	FROM 
	(
		SELECT
		A.*
		, CASE 
			WHEN A.INVENTORY_LEVEL = 0 
			AND LAG(INVENTORY_LEVEL, 1) OVER (PARTITION BY ITEM ORDER BY TRANSACTION_DATE) != 0 
			THEN 'OUT_OF_STOCK' 
			WHEN A.INVENTORY_LEVEL != 0 THEN 'IN STOCK'
		END AS STOCK_STATUS
		FROM STOCK AS A 
		WHERE 
		A.TRANSACTION_DATE >= 
			(
			SELECT MIN(B.TRANSACTION_DATE)
			FROM STOCK AS B
			WHERE B.ITEM = A.ITEM 
			AND B.INVENTORY_LEVEL != 0
			)
	) C
	WHERE STOCK_STATUS IS NOT NULL
	ORDER BY 2
	) AS D
WHERE STOCK_STATUS = 'OUT_OF_STOCK'
GROUP BY 1
```

Our final __result set__:

|item|times_out_of_stock|days_out_of_stock|
|----|------------------|-----------------|
|Bicycle|2|13,153|

You can find all the code used in this blog post [here](https://gist.github.com/ben-n93/ffbd565c816b510c51f6b24320bdd5b1).

You can also test the code out [here](https://sqlfiddle.com/postgresql/online-compiler?id=b426842e-6e3c-4d50-81a5-f3afcd04a183).



