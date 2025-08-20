from flask import  jsonify, request, render_template, redirect, url_for
from modules.order.api_calls import get_client_auth
from . import client_auth_bp

@client_auth_bp.route('/')
def chart_home():
    return render_template('clientAuth.html')

@client_auth_bp.route('/', methods=['POST'])
def client_authentication():
    print("inside client authentication")
    username = request.form.get('username')
    password = request.form.get('password')
    
    headers, socket_token, authResponse = get_client_auth(username, password)
    # print(authResponse)
    if authResponse.get('success') == True:
        print('Auth response true')
        return jsonify({
            "status": "success",
            "redirect_url": url_for('dashboard.dashboard_home')
        })
    #     return jsonify({
    #         "status": "success",
    #         "message": "Authentication successful",
    #         "data": authResponse.get('data')
    #     })
    else:
        print("Auth response false")
        return jsonify({
            "status": "error",
            "message": authResponse.get('message', 'Unknown error')
        }), 401
   