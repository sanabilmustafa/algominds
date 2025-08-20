- [algominds](#algominds)

- [Project Structure] (#-project-structure)

algominds-app-compilation/
│
├── config.py # Configuration settings (DB, secret keys, etc.)
├── requirements.txt # Python dependencies
│
├── static/ # Global static assets (CSS, JS, etc.)
│
├── templates/ # Global HTML templates (e.g. layout.html)
│
├── modules/ # Modular apps
│ ├── strategy/
│ │ ├── init.py
│ │ ├── strategy.py # Flask Blueprint for strategy config UI
│ │ ├── models.py
│ │ └── templates/
│ │ └── strategy.html
│ │
│ ├── strategy_engine/
│ │ ├── init.py # Blueprint definition
│ │ ├── indicators.py
│ │ ├── position_manager.py
│ │ ├── strategy_runner.py # Runs the strategy engine (processes live market data, sends orders, manages positions via WebSocket feeds)
│ │ ├── tkt_conventional.py
│ │ └── utils.py
│ │
│ ├── datafeed/ # Stateless | Handles raw PSX feed, parses and emits
│ │ ├── init.py # Blueprint definition
│ │ ├── feed_manager.py # ZeroMQ connection to receive live data, parses and broadcasts
│ │ ├── state.py # Runs run_datafeed() to start feed + WebSocket server
│ │ ├── indicator_server.py # Broadcasts indicator values (ws://localhost:8766)
│ │ └── utils.py # MarketData DB model + feed parsing + DB insert
│ │
│ ├── indicators/ # Indicator-related logic
│ │ ├── init.py
│ │ ├── manager.py # Subscription tracking & routing
│ │ ├── calculator.py # Indicator computation logic
│ │ └── state.py # In-memory cache (dict-based)
│ │
│ ├── clients/ # Handles WebSocket client connections
│ │ ├── init.py
│ │ ├── feed_manager.py
│ │ ├── state.py
│ │ └── utils.py
│ │
│ ├── charting/
│ │ ├── init.py
│ │ ├── charting.py # Chart routes
│ │ └── templates/
│ │ └── charting.html
│ │
│ ├── userDetails/
│ │ ├── init.py
│ │ ├── submit_form.py # Form submission
│ │ └── templates/
│ │ └── createAccount.html
│ │
│ ├── clientAuth/
│ │ ├── init.py
│ │ ├── clientAuth.py # Authentication logic
│ │ └── templates/
│ │ └── clientAuth.html
│ │
│ ├── dashboard/
│ │ ├── init.py
│ │ ├── dashboard.py # Dashboard routes
│ │ └── templates/
│ │ └── dashboard.html
│ │
│ ├── screener/
│ │ ├── init.py
│ │ ├── screener.py # Stock screener logic
│ │ └── templates/
│ │ └── screener.html
│ │
│ └── order/
│ ├── init.py
│ ├── order.py # Order sending + WebSocket connections
│ └── templates/
│ └── order.html
│
├── app.py # Master Flask App
└── run.py # Entry point           # backend process run(datafeed and strategy_engine)


                        +-------------------------+
                        |   Market Data Feed      |
                        +-----------+-------------+
                                    |
                          (real-time data tick)
                                    ↓
                        +-----------v------------+
                        |     Cache Manager      |  <- Redis + custom logic
                        | - Maintain latest bars |
                        | - Update rolling data  |
                        | - Compute indicator(s) |
                        +-----------+------------+
                                    |
                        +-----------v------------+
                        |     Screener Engine     |  <- Flask logic
                        | - Reads from cache      |
                        | - Applies filters       |
                        +-----------+-------------+
                                    |
                            (return results)


screener model :


             ┌──────────────┐
             │  Web Client  │
             └────┬─────────┘
                  │ (1. Request indicators for visible grid)
                  ▼
        ┌────────────────────────┐
        │ Indicator Sub Router   │
        │ (Manages subscriptions │
        │  + visibility window)  │
        └────┬───────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Indicator Calculation Pool │
    │  (Async workers calculate  │
    │   on symbol+tf+indicator)  │
    └────┬────────────┬──────────┘
         ▼            ▼
    Tick Feed    Bar Memory
    (Live Feed)   (Dict or Redis)



        ┌───────────────────────────────────────┐  
        │{                                      │ 
        │  "action": "subscribe",               │
        │  "symbols": ["HBL", "OGDC"],          │
        │  "indicators": ["sma_20", "rsi_14"]   │
        │}                                      │
        │  client message                       │
        └───────────────────────────────────────┘

        {
        "subscribed": true,
        "session_id": "abc123",
        "symbols": [...],
        "indicators": [...]
        }



    ssh -L 0.0.0.0:15012:192.168.99.44:15012 root@202.142.180.18 -p 20176
<!-- 

-- Step 1: Create Enum types
CREATE TYPE strategy_status AS ENUM ('Active', 'Inactive', 'Testing');
CREATE TYPE deploy_status AS ENUM ('Deployed', 'Undeployed');

-- Step 2: Create the strategies table
CREATE TABLE strategies (
    strategy_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    strategy_name VARCHAR NOT NULL,
    description TEXT,
    status strategy_status NOT NULL DEFAULT 'Inactive',
    deploy_status deploy_status NOT NULL DEFAULT 'Undeployed',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);


\copy strategies(client_id, strategy_name, description, status, deploy_status, stocks, allocation_of_assets, strategy_author) FROM '/Users/sanabilmustafa/Documents/Analytics/algominds-app-compilation/modules/strategy/strategies.csv' DELIMITER '-' CSV HEADER;
\copy strategy_stock_allocations(id, strategy_id, stock_symbol,allocation_percent) FROM '/Users/sanabilmustafa/Documents/Analytics/algominds-app-compilation/modules/strategy/stocks_strategies.csv' DELIMITER ',' CSV HEADER;
 -->



    \copy 
            market_data(
            record_identifier,
            symbol_code,
            market_code,
            symbol_state,
            symbol_flag,
            bid_volume,
            bid_price,
            ask_price,
            ask_volume,
            last_trade_price,
            last_trade_volume,
            last_trade_time,
            last_day_close_price,
            symbol_direction,
            average_price,
            high_price,
            low_price,
            net_change,
            total_traded_volume,
            total_trades,
            open_price,
            timestamp
    ) 
    FROM '/Users/rubasmustafa/Desktop/16-07-25-parsed.csv' 
    DELIMITER ',' 
    CSV HEADER;


    INSERT INTO historical (date, close, open, high, low, volume, changepercent, fvol, stock_id, symbol)
    VALUES
    -- BAFL
    ('2025-08-13', 94.99, 94.49, 97.00, 93.25, 5590000, 1.05, '5.59M', 249, 'BAFL'),

    -- AGL
    ('2025-08-13', 82.93, 82.51, 84.39, 78.65, 2430000, 0.16, '2.43M', 191, 'AGL'),

    -- ATRL
    ('2025-08-13', 657.11, 663.00, 664.89, 655.00, 363680, -0.81, '363.68K', 241, 'ATRL'),

    -- HBL
    ('2025-08-13', 275.76, 272.49, 279.49, 270.25, 3300000, 1.73, '3.30M', 468, 'HBL'),

    -- PSO
    ('2025-08-13', 409.90, 413.00, 414.98, 408.00, 4640000, -1.31, '4.64M', 723, 'PSO'),

    -- INIL
    ('2025-08-13', 186.37, 191.11, 193.00, 185.71, 209990, -2.47, '209.99K', 519, 'INIL'),

    -- FCL
    ('2025-08-13', 24.74, 24.76, 25.00, 24.68, 959700, -0.32, '959.70K', 377, 'FCL'),

    -- GATM
    ('2025-08-13', 35.08, 34.88, 35.95, 34.88, 1750000, 0.63, '1.75M', 420, 'GATM');


    CREATE TABLE positions (
        id BIGSERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        quantity NUMERIC(18,4) NOT NULL,
        buy_price NUMERIC(18,4) NOT NULL,
        highest_price NUMERIC(18,4),
        lowest_price NUMERIC(18,4),
        stop_loss NUMERIC(18,4),
        take_profit NUMERIC(18,4),
        unrealized_pnl NUMERIC(18,4),
        opened_at TIMESTAMPTZ NOT NULL,
        strategy_id VARCHAR(50), -- internal strategy reference
        order_id VARCHAR(50), -- Array of broker order ID
        order_hash VARCHAR(50), -- Provided with successful response
        account_id VARCHAR(50), -- Broker account reference
        side VARCHAR(4), -- LONG or SHORT
        risk_percentage NUMERIC(5,2),
        meta JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );




| Column               | Type                                     | Purpose                                                                                    |
| -------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| **id**               | `BIGSERIAL PRIMARY KEY`                  | Unique ID for the position                                                                 |
| **symbol**           | `VARCHAR(10) NOT NULL`                   | Stock/asset symbol                                                                         |
| **quantity**         | `NUMERIC(18,4) NOT NULL`                 | Number of shares/contracts                                                                 |
| **buy\_price**       | `NUMERIC(18,4) NOT NULL`                 | Entry price per unit                                                                       |
| **highest\_price**   | `NUMERIC(18,4)`                          | Highest price since entry                                                                  |
| **lowest\_price**    | `NUMERIC(18,4)`                          | Lowest price since entry                                                                   |
| **stop\_loss**       | `NUMERIC(18,4)`                          | Current stop-loss level                                                                    |
| **take\_profit**     | `NUMERIC(18,4)`                          | Target sell price (optional)                                                               |
| **realized\_pnl**    | `NUMERIC(18,4)`                          | Realized profit/loss (when partially closed)                                               |
| **unrealized\_pnl**  | `NUMERIC(18,4)`                          | Floating P\&L while position is open                                                       |
| **opened\_at**       | `TIMESTAMP WITH TIME ZONE NOT NULL`      | Position open time                                                                         |
| **closed\_at**       | `TIMESTAMP WITH TIME ZONE`               | Position close time (if applicable)                                                        |
| **strategy\_id**     | `VARCHAR(50)`                            | Links to your strategies table                                                             |
| **order\_ids**       | `VARCHAR(50)`                            | Array of related order IDs                                                                 |
| **account\_id**      | `VARCHAR(50)`                            | Trading account that holds this position                                                   |
| **side**             | `VARCHAR(4)`                             | `LONG` or `SHORT`                                                                          |
| **leverage**         | `NUMERIC(5,2)`                           | Leverage multiplier (if margin trading)                                                    |
| **risk\_percentage** | `NUMERIC(5,2)`                           | Percentage of capital at risk                                                              |
| **meta**             | `JSONB`                                  | Flexible storage for strategy-specific info (`{"reason": "...", "signal_strength": 0.85}`) |
| **created\_at**      | `TIMESTAMP WITH TIME ZONE DEFAULT NOW()` | Record creation time                                                                       |
| **updated\_at**      | `TIMESTAMP WITH TIME ZONE DEFAULT NOW()` | Last update time                                                                           |




CREATE TABLE executed_trades (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    quantity NUMERIC(18,4) NOT NULL,
    buy_price NUMERIC(18,4) NOT NULL,
    sell_price NUMERIC(18,4) NOT NULL,
    highest_price NUMERIC(18,4),
    lowest_price NUMERIC(18,4),
    stop_loss NUMERIC(18,4),
    take_profit NUMERIC(18,4),
    realized_pnl NUMERIC(18,4) NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL,
    closed_at TIMESTAMPTZ NOT NULL,
    strategy_id VARCHAR(50),
    order_id VARCHAR(50),
    account_id VARCHAR(50),
    side VARCHAR(4),
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


`Automatically close postion and move it to executed trade----->>>>`


CREATE OR REPLACE FUNCTION close_position(
    p_position_id BIGINT,
    p_sell_price NUMERIC
)
RETURNS VOID AS $$
DECLARE
    pos_record positions%ROWTYPE;
    realized NUMERIC(18,4);
BEGIN
    -- Fetch the position
    SELECT * INTO pos_record
    FROM positions
    WHERE id = p_position_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Position with id % not found', p_position_id;
    END IF;

    -- Calculate realized P&L based on side
    IF pos_record.side = 'LONG' THEN
        realized := (p_sell_price - pos_record.buy_price) * pos_record.quantity;
    ELSIF pos_record.side = 'SHORT' THEN
        realized := (pos_record.buy_price - p_sell_price) * pos_record.quantity;
    ELSE
        RAISE EXCEPTION 'Invalid side % for position id %', pos_record.side, p_position_id;
    END IF;

    -- Insert into executed_trades
    INSERT INTO executed_trades (
        symbol,
        quantity,
        buy_price,
        sell_price,
        highest_price,
        lowest_price,
        stop_loss,
        take_profit,
        realized_pnl,
        opened_at,
        closed_at,
        strategy_id,
        order_id,
        account_id,
        side,
        meta,
        created_at
    )
    VALUES (
        pos_record.symbol,
        pos_record.quantity,
        pos_record.buy_price,
        p_sell_price,
        pos_record.highest_price,
        pos_record.lowest_price,
        pos_record.stop_loss,
        pos_record.take_profit,
        realized,
        pos_record.opened_at,
        NOW(),
        pos_record.strategy_id,
        pos_record.order_id,
        pos_record.account_id,
        pos_record.side,
        pos_record.meta,
        NOW()
    );

    -- Delete from positions
    DELETE FROM positions WHERE id = p_position_id;

END;
$$ LANGUAGE plpgsql;



        SELECT close_position(1, 430.50);





COMMAND GIVEN BY CHATGPT
        INSERT INTO historical (date, close, open, high, low, volume, changepercent, fvol, stock_id, symbol)
        VALUES
        -- BAFL
        ('2025-08-18', 98.71, 95.19, 99.00, 94.70, 7290000, 3.70, '7.29M', 249, 'BAFL'),
        ('2025-08-15', 95.19, 95.00, 95.70, 94.75, 964790, 0.21, '964.79K', 249, 'BAFL'),

        -- AGL
        ('2025-08-18', 81.74, 82.00, 82.48, 80.00, 1700000, -0.16, '1.70M', 191, 'AGL'),
        ('2025-08-15', 81.87, 83.50, 84.00, 79.00, 608660, -1.28, '608.66K', 191, 'AGL'),

        -- ATRL
        ('2025-08-18', 665.36, 655.11, 670.00, 655.00, 808300, 1.59, '808.30K', 241, 'ATRL'),
        ('2025-08-15', 654.93, 661.99, 664.00, 653.00, 328570, -0.33, '328.57K', 241, 'ATRL'),

        -- HBL
        ('2025-08-18', 270.86, 274.10, 274.10, 262.40, 4740000, -1.20, '4.74M', 468, 'HBL'),
        ('2025-08-15', 274.15, 276.50, 277.49, 273.30, 842330, -0.58, '842.33K', 468, 'HBL'),

        -- PSO
        ('2025-08-18', 402.91, 405.00, 406.10, 395.00, 3280000, -0.46, '3.28M', 723, 'PSO'),
        ('2025-08-15', 404.79, 410.10, 414.00, 402.00, 3780000, -1.25, '3.78M', 723, 'PSO'),

        -- INIL
        ('2025-08-18', 193.66, 186.15, 194.50, 186.15, 418190, 2.08, '418.19K', 519, 'INIL'),
        ('2025-08-15', 189.72, 185.01, 194.22, 185.01, 660970, 1.80, '660.97K', 519, 'INIL'),

        -- FCL
        ('2025-08-18', 25.44, 25.05, 25.70, 25.05, 3970000, 2.17, '3.97M', 377, 'FCL'),
        ('2025-08-15', 24.90, 24.81, 25.00, 24.66, 1160000, 0.65, '1.16M', 377, 'FCL'),

        -- GATM
        ('2025-08-18', 35.17, 34.90, 35.55, 34.30, 846910, 1.21, '846.91K', 420, 'GATM'),
        ('2025-08-15', 34.75, 35.15, 35.74, 34.50, 2020000, -0.94, '2.02M', 420, 'GATM');
