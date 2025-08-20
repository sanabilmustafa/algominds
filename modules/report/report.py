from flask import render_template
import uuid
import json
import asyncio
from modules.indicators.calculator import sma, rsi
from modules.indicators.state import get_historical_bars
from . import report_bp
report_id = str(uuid.uuid4())
print(report_id)
import datetime


TIMEFRAMES = ["1d", "1h", "30min"]
INDICATORS = [
    {"name": "sma", "length": 200},
    {"name": "sma", "length": 45},
    {"name": "rsi", "length": 14},
]

# Categories definition based on score
def get_category(score):
    if score == 9:
        return "A+"
    elif score >= 7:
        return "A"
    elif score >= 5:
        return "B"
    elif score >= 3:
        return "C"
    elif score >= 1:
        return "D"
    else:
        return "F"

async def evaluate_stock(symbol):
    score = 0
    for tf in TIMEFRAMES:
        bars = await get_historical_bars(symbol, tf)
        if not bars or len(bars) < 200:
            continue  # skip if not enough data

        close = bars[-1]["close"]

        sma_200 = sma(bars, 200)[-1]
        sma_45 = sma(bars, 45)[-1]
        rsi_val = rsi(bars, 14)[-1]

        if sma_200 and close > sma_200:
            score += 1
        if sma_45 and close > sma_45:
            score += 1
        if rsi_val and rsi_val > 60:
            score += 1

    category = get_category(score)
    return symbol, category

# async def _generate_report(symbols):
#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     report_id = str(uuid.uuid4())

#     category_data = {
#         "A+": [],
#         "A": [],
#         "B":[],
#         "C": [],
#         "D": [],
#         "F":[],
#     }

#     tasks = [evaluate_stock(symbol) for symbol in symbols]
#     results = await asyncio.gather(*tasks)

#     for symbol, category in results:
#         category_data[category].append(symbol)

#     report = {
#         "report_id": report_id,
#         "timestamp": timestamp,
#         "categories": category_data
#     }
#     return report

async def _generate_report(stock_list):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = str(uuid.uuid4())

    category_data = {
        "A+": [],
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "F": [],
    }

    tasks = [evaluate_stock(stock["symbol"]) for stock in stock_list]
    results = await asyncio.gather(*tasks)

    for stock, (_, category) in zip(stock_list, results):
        stock_info = {
            "symbol": stock["symbol"],
            "company": stock["company"]
        }
        category_data[category].append(stock_info)

    report = {
        "report_id": report_id,
        "timestamp": timestamp,
        "categories": category_data
    }
    return report



def generate_report(stock_list):
    return asyncio.run(_generate_report(stock_list))

@report_bp.route("/daily_report", methods=["GET"])
def report_daily():
    with open('modules/report/stocks.json') as f:
        raw_symbols = json.load(f)  # already a list of dicts with symbol + company

    report = generate_report(raw_symbols)
    print(report["report_id"])
    return render_template("dailyReport.html", report=report, report_id=report['report_id'])

@report_bp.route("/")
def report_home():
    return render_template("reports.html")
    

# @report_bp.route("/generate", methods=["GET"])
# def report_home():
#     with open('modules/report/stocks.json') as f:
#         raw_symbols = json.load(f)
#     report = generate_report(raw_symbols)
#     print(report["report_id"])
#     return render_template("dailyReport.html", report=report, report_id=report['report_id'])


# @report_bp.route("/generate", methods=["GET"])
# def report_home():
#     with open('modules/report/stocks.json') as f:
#         raw_symbols = json.load(f)
#     # stock_symbols = []
#     # for item in raw_symbols:
#     #     parts = item.split(" - ")
#     #     if len(parts) >= 2:
#     #         symbol = parts[0].strip()
#     #         label = item.strip()
#     #         stock_symbols.append({"value": symbol, "label": label})
#     #     else:
#     #         # fallback if no company name
#     #         stock_symbols.append({"value": item.strip(), "label": item.strip()})

#     # report = generate_report([stock["value"] for stock in stock_symbols])
#     report = generate_report(raw_symbols)
#     print(report["report_id"])
#     return render_template("dailyReport.html", report=report, report_id=report['report_id'])