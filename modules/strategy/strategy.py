from flask import jsonify, request, render_template, redirect, url_for
from . import strategy_bp , db 
import json
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from collections import defaultdict
from .models import Strategy, StrategyStocks


@strategy_bp.route('/deploy', methods=['POST'])
def deploy_strategy():
    data = request.get_json()
    print(data)
    
    strategy_id = data.get("strategy_id")
    if not strategy_id:
        return jsonify({'error': 'Strategy ID is required. Creation of new strategies is not allowed.'}), 400

    strategy = Strategy.query.get(strategy_id)
    # strategyStocks = StratetegyStocks.query.filter_by(strategy_id=strategy_id).all()
    
    if not strategy:
        return jsonify({'error': 'Strategy not found.'}), 404
    if not strategy.allow_update:
        return jsonify({'error': 'This strategy cannot be updated.'}), 403

    # Determine if it's a deploy or undeploy action
    deploy_status = data.get("deploy_status")
    status = data.get("status")

    # Update basic fields
    strategy.strategy_name = data.get("strategy_name", strategy.strategy_name)
    strategy.strategy_author = data.get("strategy_author", strategy.strategy_author)
    strategy.description = data.get("description", strategy.description)
    strategy.client_id = data.get("client_id", strategy.client_id)

  # Remove existing allocations and insert new ones
    StrategyStocks.query.filter_by(strategy_id=strategy_id).delete()

    stock_allocations = data.get('stock_allocations', [])
    for allocation in stock_allocations:
        stock = StrategyStocks(
            strategy_id=strategy_id,
            stock_symbol=allocation['stock_symbol'],
            allocation_percent=allocation['allocation_percent']
        )
        db.session.add(stock)
    if deploy_status == "Deployed" and status == "Active":
        # Deployment action
        strategy.deploy_status = "Deployed"
        strategy.status = "Active"
        # strategy.stocks = data.get("stocks", strategy.stocks)
        strategy.allocation_of_assets = data.get("allocation_of_assets", strategy.allocation_of_assets)
    elif deploy_status == "Undeployed" and status == "Inactive":
        # Undeployment action
        # strategy.stocks = data.get("stocks", strategy.stocks)
        strategy.allocation_of_assets = data.get("allocation_of_assets", strategy.allocation_of_assets)
        strategy.deploy_status = "Undeployed"
        strategy.status = "Inactive"
    else:
        return jsonify({'error': 'Invalid deploy_status or status values.'}), 400

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Strategy {"deployed" if strategy.deploy_status == "Deployed" else "undeployed"} successfully',
        'strategy_id': strategy.strategy_id
    }), 200

    
@strategy_bp.route('/activation', methods=['POST'])
def activate_or_deactivate_strategy():
    data = request.get_json()
    strategy_id = data.get("strategy_id")
    new_status = data.get("status")  # 'Active' or 'Inactive'

    if not strategy_id:
        return jsonify({'error': 'Strategy ID is required.'}), 400

    if new_status not in ['Active', 'Inactive']:
        return jsonify({'error': 'Invalid status value. Must be "Active" or "Inactive".'}), 400

    strategy = Strategy.query.get(strategy_id)
    if not strategy:
        return jsonify({'error': 'Strategy not found.'}), 404

    # Update the strategy status
    strategy.status = new_status
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Strategy {new_status.lower()}d successfully',
        'strategy_id': strategy.strategy_id,
        'status': strategy.status
    }), 200



@strategy_bp.route('/strategies', methods=['GET'])
def get_strategies():
    client_id = request.args.get("client_id")
    deploy_status = request.args.get("deploy_status")  # e.g., "Deployed"

    # Validate client_id
    if not client_id:
        return jsonify({'error': 'client_id is required as a query parameter.'}), 400

    # Optional validation for deploy_status
    valid_deploy_statuses = ['Deployed', 'Undeployed']
    if deploy_status and deploy_status not in valid_deploy_statuses:
        return jsonify({'error': f'Invalid deploy_status value. Must be one of {valid_deploy_statuses}.'}), 400

    # Build the query
    query = Strategy.query.filter_by(client_id=client_id)
    if deploy_status:
        query = query.filter_by(deploy_status=deploy_status)

    strategies = query.all()

    # Convert strategies to JSON
    strategies_list = [
        {
            'strategy_id': s.strategy_id,
            'name': s.strategy_name,
            'author': s.strategy_author,
            'description': s.description,
            'status': s.status,
            'deploy_status': s.deploy_status,
        }
        for s in strategies
    ]

    return jsonify({
        'success': True,
        'count': len(strategies_list),
        'strategies': strategies_list
    }), 200
    
    
    
@strategy_bp.route('/strategies/<int:strategy_id>')
def strategy_status(strategy_id):
    # Fetch strategy details
    strategy = Strategy.query.get(strategy_id)
    if not strategy:
        return jsonify({'error': 'Strategy not found'}), 404

    # Example: Fetch stock allocations
    stock_allocations = StrategyStocks.query.filter_by(strategy_id=strategy_id).all()

    # Example: Fetch statistics (assuming you have a separate table or computed fields)
    # Replace with your real DB logic
    stats = {
        'total_pnl': 15000.50,
        'win_rate': 72.5,
        'avg_trade_duration': '3 days',
        'total_positions': len(stock_allocations)
    }

    return render_template(
        'strategy_status.html',
        strategy=strategy,
        stock_allocations=stock_allocations,
        stats=stats
    )
    
    

@strategy_bp.route('/')
def strategy_home():
    with open('modules/strategy/stocks.json') as f:
        stock_symbols = json.load(f)
    # print(stock_symbols)
    strategies = Strategy.query.all()
    strategies_stocks = StrategyStocks.query.all()
    # Group stock allocations by strategy_id
    stocks_by_strategy = defaultdict(list)
    for stock in strategies_stocks:
        stocks_by_strategy[stock.strategy_id].append({
        'stock_symbol': stock.stock_symbol.upper(),
        'allocation_percent': stock.allocation_percent
    })
    # print(stocks_by_strategy)
    return render_template('strategy.html', 
                           strategies=strategies,         
                           stocks_by_strategy=stocks_by_strategy,
                           stock_symbols=stock_symbols)