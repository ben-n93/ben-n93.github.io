Title: Using SQL to calculate how often and how many days a store's inventory is out of stock 
Date: 2024-07-02
Description: Using SQL in the PostgreSQL database to calculate how often and how many days a store's inventory is out of stock.
Tags: SQL, Postgres

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TFP90633KX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-TFP90633KX');
</script>

Recently a Reddit user posted in [r/SQL](https://www.reddit.com/r/SQL/) wanting to know how to calculate 
how often and how many days an item was out of stock.

I enjoyed coming up with a solution and so I've decided to write about it in more detail.

Note that I'll be using Postgres.

## The data

First, the dataset we'll be operating on:

|item|inventory_check_dt|inventory_level|
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

Each record in the dataset is when an inventory check is conducted.

Here's the DDL:

```SQL
CREATE TABLE stock (
    item VARCHAR(50),
    transactioninventory_check_dt_date DATE,
    inventory_level INT
);

INSERT INTO stock (item, inventory_check_dt, inventory_level) VALUES
('Bicycle', '2024-01-10', 10),
('Bicycle', '2024-01-15', 5),
('Bicycle', '2024-01-16', 0),
('Bicycle', '2024-01-20', 0),
('Bicycle', '2024-01-23', 0),
('Bicycle', '2024-01-25', 0),
('Bicycle', '2024-01-28', 20),
('Bicycle', '2024-01-29', 12),
('Bicycle', '2024-01-31', 0)
;
```

## The problem

We want to find out how often our store was out of stock of bicycles and for how may days.

### Calculating how many times bicycles were sold out

It's simple enough to verify when an item goes out of stock. There's 0 inventory on hand
and when the last inventory check was conducted there was stock.

Verifying this nicely demonstrates the power of both `CASE` statements and window functions and how they can be combined
to analyse and transform data. In this case we use them to verify both the aformentioned criteria. 

Specifically by utilising the `LAG()` window function we can look to see how much inventory there was on the previous inventory check date:

```SQL
SELECT
item
, inventory_check_dt
, inventory_level
, CASE 
	WHEN inventory_level != 0 THEN 'IN STOCK'
    WHEN inventory_level = 0 AND LAG(inventory_level, 1) OVER (PARTITION BY ITEM ORDER BY inventory_check_dt) != 0 
		THEN 'OUT_OF_STOCK' 
  END AS stock_status
FROM stock
;
```

|item|inventory_check_dt|inventory_level|stock_status|
|----|----------------|---------------|------------|
|Bicycle|2024-01-10|10|IN STOCK|
|Bicycle|2024-01-15|5|IN STOCK|
|Bicycle|2024-01-16|0|OUT_OF_STOCK|
|Bicycle|2024-01-20|0||
|Bicycle|2024-01-23|0||
|Bicycle|2024-01-25|0||
|Bicycle|2024-01-28|20|IN STOCK|
|Bicycle|2024-01-29|12|IN STOCK|
|Bicycle|2024-01-31|0|OUT_OF_STOCK|

Perfect! We can see that twice bicycles have gone out of stock.

### Calculating how long bicycles were sold out

Next let's calculate how long bicycles were sold out for.

All we need to do is calculate the difference in days between when an item was flagged as having gone out of stock and when it 
next came into stock (or more accurately, when an inventory check was recorded that revealed there was stock).

Again we'll use a `CASE` statement but this time with the `LEAD()` window function to return the next transcation date.

We'll filter out rows with `NULL` for the `stock_status` column so that what will be returned, if it exists, is the next date in which an inventory count is conducted that reveals bicycles are back in stock.

I've also wrapped `COALESCE()` around `LEAD()` so if there is no next row (meaning bicycles are still out of stock) what's returned is the current date:

```SQL
WITH stock_status AS 
(
SELECT
*
, CASE 
	WHEN inventory_level != 0 THEN 'IN STOCK'
    WHEN inventory_level = 0 AND LAG(inventory_level, 1) OVER (PARTITION BY item ORDER BY inventory_check_dt) != 0 
    	THEN 'OUT_OF_STOCK' 
  END AS stock_status
FROM stock
)
SELECT
item
, inventory_check_dt
, stock_status
, CASE 
	WHEN stock_status = 'OUT_OF_STOCK' 
		THEN COALESCE(LEAD(inventory_check_dt, 1) OVER (PARTITION BY ITEM ORDER BY inventory_check_dt), CURRENT_DATE)
		- inventory_check_dt 
  END AS days_out_of_stock
FROM stock_status
WHERE stock_status IS NOT NULL
;
```
|item|inventory_check_dt|stock_status|days_out_of_stock|
|----|------------------|------------|-----------------|
|Bicycle|2024-01-10|IN STOCK||
|Bicycle|2024-01-15|IN STOCK||
|Bicycle|2024-01-16|OUT_OF_STOCK|12|
|Bicycle|2024-01-28|IN STOCK||
|Bicycle|2024-01-29|IN STOCK||
|Bicycle|2024-01-31|OUT_OF_STOCK|246|

Perfect!

We have our answer.

The Redditor who I helped asked for a single row per item which broke out how many
times the item was out of stock and for how long (in a comma-seperated string) so let's do that:

```SQL
WITH stock_status AS 
(
SELECT
*
, CASE 
	WHEN inventory_level != 0 THEN 'IN STOCK'
    WHEN inventory_level = 0 AND LAG(inventory_level, 1) OVER (PARTITION BY item ORDER BY inventory_check_dt) != 0 
    	THEN 'OUT_OF_STOCK' 
  END AS stock_status
FROM stock
), time_calculation AS 
(
SELECT
item
, stock_status
, COALESCE(LEAD(inventory_check_dt, 1) OVER (PARTITION BY ITEM ORDER BY inventory_check_dt), CURRENT_DATE) 
- inventory_check_dt AS days_out_of_stock
FROM stock_status
WHERE stock_status IS NOT NULL 
)
SELECT 
item 
, COUNT(stock_status) AS times_out_of_stock
, STRING_AGG(days_out_of_stock::VARCHAR, ',') AS days_out_of_stock
FROM time_calculation 
WHERE stock_status = 'OUT_OF_STOCK'
GROUP BY item 
;
```

Our final __result set__:

|item|times_out_of_stock|days_out_of_stock|
|----|------------------|-----------------|
|Bicycle|2|12,153|

