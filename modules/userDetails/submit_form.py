from flask import request, jsonify, render_template
import psycopg2
import config
from . import user_details_bp
# app = Flask(__name__)
# CORS(app)


def insert_into_db(form_data):
    # Convert checkbox "on"/"true"/"false" to actual bools
    def to_bool(val):
        return str(val).lower() in ["true", "on", "1"]

    # Map field names to values
    data = {field['name']: field.get('value') for field in form_data}

    with psycopg2.connect(    
        dbname=config.DB_NAME,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO account_application (
                    firstname, lastname, gender, maritalstatus, dateofbirth, placeofbirth,
                    idcardnumber, dateofissue, dateofexpiry, cnicfront, cnicback,
                    email, phonenumber, pta, mailingaddress, add_checkbox,
                    bankname, iban, proofiban, employment,
                    zakat, digitalsignature,
                    nom_name, nom_id, nom_id_front, nom_id_back, nom_id_exp_date, nom_id_exp,
                    relation_with_nominee, nom_proof, ukn, proof_ukn
                ) VALUES (
                    %(firstname)s, %(lastname)s, %(gender)s, %(maritalstatus)s, %(dateofbirth)s, %(placeofbirth)s,
                    %(idcardnumber)s, %(dateofissue)s, %(dateofexpiry)s, %(cnicfront)s, %(cnicback)s,
                    %(email)s, %(phonenumber)s, %(pta)s, %(mailingaddress)s, %(add)s,
                    %(bankname)s, %(iban)s, %(proofiban)s, %(employment)s,
                    %(zakat)s, %(digitalsignature)s,
                    %(nom-name)s, %(nom-id)s, %(nom-id-front)s, %(nom-id-back)s, %(nom-id-exp-date)s, %(nom-id-exp)s,
                    %(Relation-w-nominee)s, %(nom-proof)s, %(ukn)s, %(proof-ukn)s
                )
            """, {
                k: to_bool(v) if k in ['pta', 'add', 'zakat', 'nom-id-exp'] else v
                for k, v in data.items()
            })
    return True

# @user_details_bp.route('/submit-form', methods=['POST'])
# def submit_form():
#     print("Received form submission")
#     if not request.is_json:
#         return jsonify({'error': 'Invalid or missing JSON data'}), 400
    
#     form_data = request.json.get('formFields')
    
#     if not form_data:
#         return jsonify({'error': 'Missing formFields'}), 400
#     try:
#         insert_into_db(form_data)
#         return jsonify({'message': 'Form submitted successfully'}), 200
#     except Exception as e:
#         print("Error:", e)
#         return jsonify({'error': str(e)}), 500
    

@user_details_bp.route('/user-details/submit-form', methods=['POST'])
def submit_form():
    data = request.get_json()
    if not data or 'formFields' not in data:
        return jsonify({'error': 'Invalid or missing formFields'}), 400

    form_data = data['formFields']
    try:
        insert_into_db(form_data)
        return jsonify({'message': 'Form submitted successfully'}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500


@user_details_bp.route('/')
def form_home():
    return render_template('createaccount.html')
