WITH market_sessions AS (
    SELECT 
        trading_day::date AS trading_day,
        unnest(ARRAY['09:30:00'::time, '15:30:00'::time]) AS session_start,
        unnest(ARRAY['15:30:00'::time, '15:30:00'::time]) AS session_end
    FROM (SELECT '{{DATE}}'::date AS trading_day) base
    WHERE EXTRACT(DOW FROM trading_day) IN (1,2,3,4) -- Mon-Thu
    UNION ALL
    SELECT 
        trading_day::date AS trading_day,
        unnest(ARRAY['09:15:00'::time, '14:30:00'::time]) AS session_start,
        unnest(ARRAY['12:00:00'::time, '16:30:00'::time]) AS session_end
    FROM (SELECT '{{DATE}}'::date AS trading_day) base
    WHERE EXTRACT(DOW FROM trading_day) = 5 -- Friday
),
tick_data AS (
    SELECT
        md.symbol_code,
        md.ask_price,
        md.last_trade_price,
        md.total_traded_volume,
        md.timestamp,
        (date_trunc('minute', md.timestamp) - (extract(minute from md.timestamp)::int % 30) * interval '1 minute' + interval '30 minutes') AS interval_close_time,
        ROW_NUMBER() OVER (
            PARTITION BY md.symbol_code, (date_trunc('minute', md.timestamp) - (extract(minute from md.timestamp)::int % 30) * interval '1 minute' + interval '30 minutes')
            ORDER BY md.timestamp ASC
        ) AS rn_open,
        ROW_NUMBER() OVER (
            PARTITION BY md.symbol_code, (date_trunc('minute', md.timestamp) - (extract(minute from md.timestamp)::int % 30) * interval '1 minute' + interval '30 minutes')
            ORDER BY md.timestamp DESC
        ) AS rn_close,
        ROW_NUMBER() OVER (
            PARTITION BY md.symbol_code, date_trunc('day', md.timestamp) + interval '1 day'
            ORDER BY (CASE WHEN md.ask_price IS NOT NULL THEN md.timestamp ELSE NULL END) DESC NULLS LAST
        ) AS rn_last_non_null_ask_price
    FROM market_data md
    JOIN market_sessions ms ON md.timestamp::date = ms.trading_day
    WHERE md.timestamp::time >= ms.session_start
      AND md.timestamp::time <= ms.session_end + interval '30 minutes'
),
volume_calc AS (
    SELECT
        symbol_code,
        interval_close_time,
        MAX(total_traded_volume) - COALESCE(LAG(MAX(total_traded_volume)) OVER (PARTITION BY symbol_code ORDER BY interval_close_time), 0) AS volume
    FROM tick_data
    GROUP BY symbol_code, interval_close_time
),
intervals AS (
    SELECT
        symbol_code,
        interval_close_time,
        MIN(timestamp) AS min_ts,
        MAX(timestamp) AS max_ts
    FROM tick_data
    GROUP BY symbol_code, interval_close_time
),
last_interval AS (
    SELECT symbol_code, MAX(interval_close_time) AS last_interval_close_time
    FROM intervals
    GROUP BY symbol_code
),
market_close_ts AS (
    SELECT symbol_code, MAX(trading_day + session_end) AS market_close_timestamp
    FROM market_sessions
    CROSS JOIN (SELECT DISTINCT symbol_code FROM tick_data) s
    GROUP BY symbol_code
)
INSERT INTO ohlc_30min (symbol_code, candle_close_time, open_price, high_price, low_price, close_price, volume)
SELECT
    t1.symbol_code,
    t1.interval_close_time AS candle_close_time,
    CASE
        WHEN t1.interval_close_time > mct.market_close_timestamp THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.symbol_code = t1.symbol_code AND t3.rn_last_non_null_ask_price = 1)
        ELSE
            (SELECT last_trade_price FROM tick_data t2 WHERE t2.symbol_code = t1.symbol_code AND t2.interval_close_time = t1.interval_close_time AND t2.rn_open = 1)
    END AS open_price,
    CASE
        WHEN t1.interval_close_time > mct.market_close_timestamp THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.symbol_code = t1.symbol_code AND t3.rn_last_non_null_ask_price = 1)
        ELSE
            MAX(t1.last_trade_price)
    END AS high_price,
    CASE
        WHEN t1.interval_close_time > mct.market_close_timestamp THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.symbol_code = t1.symbol_code AND t3.rn_last_non_null_ask_price = 1)
        ELSE
            MIN(t1.last_trade_price)
    END AS low_price,
    CASE 
        WHEN t1.interval_close_time = li.last_interval_close_time THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.symbol_code = t1.symbol_code AND t3.rn_last_non_null_ask_price = 1)
        WHEN t1.interval_close_time > mct.market_close_timestamp THEN
            (SELECT ask_price FROM tick_data t3 WHERE t3.symbol_code = t1.symbol_code AND t3.rn_last_non_null_ask_price = 1)
        ELSE
            (SELECT last_trade_price FROM tick_data t2 WHERE t2.symbol_code = t1.symbol_code AND t2.interval_close_time = t1.interval_close_time AND t2.rn_close = 1)
    END AS close_price,
    vc.volume
FROM tick_data t1
JOIN volume_calc vc ON t1.symbol_code = vc.symbol_code AND t1.interval_close_time = vc.interval_close_time
JOIN last_interval li ON t1.symbol_code = li.symbol_code
JOIN market_close_ts mct ON t1.symbol_code = mct.symbol_code
GROUP BY t1.symbol_code, t1.interval_close_time, li.last_interval_close_time, mct.market_close_timestamp, vc.volume
HAVING t1.interval_close_time >= (SELECT MIN(trading_day + session_start) FROM market_sessions)
   AND t1.interval_close_time <= li.last_interval_close_time
ORDER BY t1.symbol_code, t1.interval_close_time;
