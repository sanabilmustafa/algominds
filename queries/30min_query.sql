WITH market_sessions AS (
    SELECT 
        trading_day::date AS trading_day,
        unnest(ARRAY['09:30:00'::time, '15:30:00'::time]) AS session_start,
        unnest(ARRAY['15:30:00'::time, '15:30:00'::time]) AS session_end
    FROM (SELECT '{{DATE}}'::date AS trading_day) base
    WHERE EXTRACT(DOW FROM trading_day) IN (1,2,3,4)
    UNION ALL
    SELECT 
        trading_day::date AS trading_day,
        unnest(ARRAY['09:15:00'::time, '14:30:00'::time]) AS session_start,
        unnest(ARRAY['12:00:00'::time, '16:30:00'::time]) AS session_end
    FROM (SELECT '{{DATE}}'::date AS trading_day) base
    WHERE EXTRACT(DOW FROM trading_day) = 5
),
tick_data AS (
    SELECT
        md.symbol_code,
        md.ask_price,
        md.last_trade_price,
        md.timestamp,
        md.total_traded_volume,
        (date_trunc('minute', md.timestamp) - (extract(minute from md.timestamp)::int % 30) * interval '1 minute' + interval '30 minutes') AS interval_close_time,
        ROW_NUMBER() OVER (
            PARTITION BY (date_trunc('minute', md.timestamp) - (extract(minute from md.timestamp)::int % 30) * interval '1 minute' + interval '30 minutes')
            ORDER BY md.timestamp ASC
        ) AS rn_open,
        ROW_NUMBER() OVER (
            PARTITION BY (date_trunc('minute', md.timestamp) - (extract(minute from md.timestamp)::int % 30) * interval '1 minute' + interval '30 minutes')
            ORDER BY md.timestamp DESC
        ) AS rn_close,
        ROW_NUMBER() OVER (
            PARTITION BY date_trunc('day', md.timestamp) + interval '1 day'
            ORDER BY (CASE WHEN md.ask_price IS NOT NULL THEN md.timestamp ELSE NULL END) DESC NULLS LAST
        ) AS rn_last_non_null_ask_price
    FROM market_data md
    JOIN market_sessions ms ON md.timestamp::date = ms.trading_day
    WHERE md.timestamp::time >= ms.session_start
      AND md.timestamp::time <= ms.session_end + interval '30 minutes'
      AND md.symbol_code = '{{SYMBOL}}'
),
intervals AS (
    SELECT
        interval_close_time,
        MAX(total_traded_volume) AS interval_volume
    FROM tick_data
    GROUP BY interval_close_time
),
intervals_with_prev AS (
    SELECT
        interval_close_time,
        interval_volume,
        LAG(interval_volume, 1, 0) OVER (ORDER BY interval_close_time) AS prev_interval_volume
    FROM intervals
),
last_interval AS (
    SELECT MAX(interval_close_time) AS last_interval_close_time
    FROM intervals
),
market_close_ts AS (
    SELECT MAX(trading_day + session_end) AS market_close_timestamp
    FROM market_sessions
)
INSERT INTO ohlc_30min (symbol_code, candle_close_time, open_price, high_price, low_price, close_price, volume)
SELECT
    '{{SYMBOL}}' AS symbol_code,
    t1.interval_close_time AS candle_close_time,
    CASE
        WHEN t1.interval_close_time > (SELECT market_close_timestamp FROM market_close_ts) THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.rn_last_non_null_ask_price = 1)
        ELSE
            (SELECT last_trade_price FROM tick_data t2 
                WHERE t2.interval_close_time = t1.interval_close_time AND t2.rn_open = 1)
    END AS open_price,
    CASE
        WHEN t1.interval_close_time > (SELECT market_close_timestamp FROM market_close_ts) THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.rn_last_non_null_ask_price = 1)
        ELSE
            MAX(last_trade_price)
    END AS high_price,
    CASE
        WHEN t1.interval_close_time > (SELECT market_close_timestamp FROM market_close_ts) THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.rn_last_non_null_ask_price = 1)
        ELSE
            MIN(last_trade_price)
    END AS low_price,
    CASE 
        WHEN t1.interval_close_time = (SELECT last_interval_close_time FROM last_interval) THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.rn_last_non_null_ask_price = 1)
        WHEN t1.interval_close_time > (SELECT market_close_timestamp FROM market_close_ts) THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.rn_last_non_null_ask_price = 1)
        ELSE
            (SELECT last_trade_price FROM tick_data t2 WHERE t2.interval_close_time = t1.interval_close_time AND t2.rn_close = 1)
    END AS close_price,
    (iwp.interval_volume - iwp.prev_interval_volume) AS volume
FROM tick_data t1
JOIN intervals_with_prev iwp ON t1.interval_close_time = iwp.interval_close_time
GROUP BY t1.interval_close_time, iwp.interval_volume, iwp.prev_interval_volume
HAVING t1.interval_close_time >= (SELECT MIN(trading_day + session_start) FROM market_sessions)
   AND t1.interval_close_time <= (SELECT last_interval_close_time FROM last_interval)
ORDER BY t1.interval_close_time;
