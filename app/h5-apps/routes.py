from flask import Blueprint, jsonify, request

h5_apps_blueprint = Blueprint('h5_apps', __name__)

@h5_apps_blueprint.route('/delete', method=['POST'])
def delete():
    data = request.get_json()

    if not data or 'h5_id' not in data:
        return jsonify({ 'success': False, 'message': 'No id is presented in your request.'}), 400


    return jsonify(), 200

# Helloworld endpoint

@h5_apps_blueprint.route('/')
def index():
    return jsonify({'message': 'Hello World', 'success': True})

# removed API endpoint

def APIRemoved():
    return jsonify({ 'success': False, 'message': 'This API Endpoint is being removed.'})

@h5_apps_blueprint.route('/upload_h5', methods=['POST'])
def upload_h5():
    return APIRemoved(), 410

@h5_apps_blueprint.route('/upload_icon', methods=['POST'])
def upload_icon():
    return APIRemoved(), 410

@h5_apps_blueprint.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    return APIRemoved(), 410

@h5_apps_blueprint.route('/upload_screenshot_by_url', methods=['POST'])
def upload_screenshot_by_url():
    return APIRemoved(), 410

@h5_apps_blueprint.route('/upload_donation_qrcode', methods=['POST'])
def upload_donation_qrcode():
    return APIRemoved(), 410

@h5_apps_blueprint.route('/upload_donation_qrcode_by_url', methods=['POST'])
def upload_donation_qrcode_by_url():
    return APIRemoved(), 410
