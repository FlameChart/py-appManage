from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler
from ..database import db
from ..models import H5App, AppReview
from ..services.h5_apps_service import (
    get_next_review_id,
    upload_h5_app,
    upload_h5_icon,
    upload_h5_screenshot,
    get_app_detail_service,
    get_user_uploaded_apps,
    update_h5_app_service,
    delete_h5_app_service,
    promote_h5_app_service,
    update_exposure_service, get_next_h5_id, upload_donation_qrcode_file
)
from ..services.auth_service import authenticate_user_service
import os

h5_apps_bp = Blueprint('h5_apps', __name__)
CORS(h5_apps_bp)  # 为蓝图添加 CORS 支持
scheduler = APScheduler()


# 初始化定时任务
def init_scheduler(app):
    scheduler.init_app(app)

    # 添加更新曝光值的定时任务(每天凌晨4点执行)
    @scheduler.task('cron', id='update_exposure', hour=4)
    def scheduled_task():
        with app.app_context():
            update_exposure_service()

    scheduler.start()


@h5_apps_bp.route('/upload_h5', methods=['POST'])
def upload_h5():
    """上传 H5 应用"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        # 验证用户身份
        # user_data, status_code = authenticate_user_service(data)

        # if status_code != 200:
        #     return jsonify({
        #         'success': False,
        #         'message': user_data.get('error', '用户验证失败')
        #     }), status_code

        # # 添加上传者ID到数据中
        # uploader_id = user_data.get('user_data', {}).get('user_id')
        # if not uploader_id:
        #     return jsonify({
        #         'success': False,
        #         'message': '无法获取上传者ID'
        #     }), 400

        # data['uploader'] = uploader_id

        # 检查必要字段
        required_fields = ['h5_name', 'description', 'category', 'deploy_url']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必要字段: {field}'
                }), 400

        # 处理上传（现在会创建审核记录）
        try:
            review = upload_h5_app(data)
            return jsonify({
                'success': True,
                'message': '应用已提交审核',
                'data': review.to_dict()
            }), 201
        except ValueError as ve:
            print(f"提交应用审核失败: {str(ve)}")
            return jsonify({
                'success': False,
                'message': str(ve)
            }), 400
        except Exception as e:
            print(f"提交应用审核时发生未知错误: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': '提交失败，请稍后重试'
            }), 500

    except Exception as e:
        print(f"Error in upload_h5: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@h5_apps_bp.route('/upload_icon', methods=['POST'])
def upload_icon():
    """上传H5图标"""
    try:
        print(f"图标: {request.form}")

        if 'icon' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400

        file = request.files['icon']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        # 获取id参数
        id = request.form.get('id')
        if not id:
            return jsonify({'success': False, 'error': '缺少id参数'}), 400

        # 调用函数保存图标并获取路径
        icon_url = upload_h5_icon(file, id)

        return jsonify({
            'success': True,
            'message': '图标上传成功',
            'path': icon_url,
            'url': icon_url
        }), 200

    except Exception as e:
        print(f"Error in upload_icon: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@h5_apps_bp.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    """上传H5截图"""
    try:
        print(f"截图: {request.form}")
        if 'screenshot' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        index = request.form.get('index')
        if not index:
            return jsonify({'error': '缺少图片序号'}), 400

        file = request.files['screenshot']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        # 获取id参数
        id = request.form.get('id')
        if not id:
            return jsonify({'error': '缺少id参数'}), 400

        screenshot_url = upload_h5_screenshot(file, int(index), int(id))

        return jsonify({
            'success': True,
            'message': '截图上传成功',
            'path': screenshot_url,
            'url': screenshot_url,  # 添加完整的URL
            'index': int(index)
        }), 200

    except Exception as e:
        print(f"Error in upload_screenshot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@h5_apps_bp.route('/get_user_uploaded_apps', methods=['POST'])
def get_user_uploaded_apps_route():
    """获取用户上传的H5应用"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': '缺少用户ID'}), 400

        apps = get_user_uploaded_apps(user_id)
        if apps is not None:
            return jsonify({
                'success': True,
                'data': apps
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '获取应用列表失败'
            }), 500

    except Exception as e:
        print("发生错误:", str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@h5_apps_bp.route('/get_app_detail', methods=['POST'])
def get_app_detail():
    """获取应用详情"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        h5_id = data.get('h5_id')

        if user_id:
            user_id = int(user_id)
        if h5_id:
            h5_id = int(h5_id)

        app_detail = get_app_detail_service(user_id, h5_id)
        if app_detail:
            return jsonify(app_detail)
        return jsonify({"message": "获取应用详情失败"}), 500

    except Exception as e:
        print(f"Error in get_app_detail: {e}")
        return jsonify({'error': str(e)}), 500


@h5_apps_bp.route('/update', methods=['POST'])
def update_app():
    """更新H5应用"""
    try:
        data = request.get_json()
        print("收到的更新数据:", data)
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        result, status_code = update_h5_app_service(data)
        return jsonify(result), status_code

    except Exception as e:
        print(f"Error in update_app: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@h5_apps_bp.route('/delete', methods=['POST'])
def delete_app():
    """下架H5应用"""
    try:
        data = request.get_json()
        if not data or 'h5_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400

        # 验证用户身份
        # user_data, status_code = authenticate_user_service(data)
        # if status_code != 200:
        #     return jsonify({
        #         'success': False,
        #         'message': user_data.get('error', '用户验证失败')
        #     }), status_code

        result, status_code = delete_h5_app_service(data['h5_id'])
        return jsonify(result), status_code

    except Exception as e:
        print(f"Error in delete_app: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@h5_apps_bp.route('/promote', methods=['POST'])
def promote_app():
    """推广H5应用"""
    try:
        data = request.get_json()
        if not data or not all(field in data for field in ['h5_id', 'user_id', 'coin_amount']):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400

        # 验证用户身份
        user_data, status_code = authenticate_user_service(data)
        if status_code != 200:
            return jsonify({
                'success': False,
                'message': user_data.get('error', '用户验证失败')
            }), status_code

        result, status_code = promote_h5_app_service(data)
        return jsonify(result), status_code

    except Exception as e:
        print(f"Error in promote_app: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@h5_apps_bp.route('/upload_donation_qrcode', methods=['POST'])
def upload_donation_qrcode_route():
    """上传H5打赏二维码"""
    try:
        print(f"二维码: {request.form}")
        if 'qrcode' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400

        file = request.files['qrcode']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        # 获取id参数
        id = request.form.get('id')
        if not id:
            return jsonify({'success': False, 'error': '缺少id参数'}), 400

        # 获取后缀，-1代表微信，-2代表支付宝
        suffix = request.form.get('suffix', '')
        if suffix not in ['-1', '-2']:
            return jsonify({'success': False, 'error': '无效的二维码类型，必须是-1(微信)或-2(支付宝)'}), 400

        # 调用函数保存二维码并获取路径
        qrcode_url = upload_donation_qrcode_file(file, int(id), suffix)

        return jsonify({
            'success': True,
            'message': '打赏二维码上传成功',
            'path': qrcode_url,
            'url': qrcode_url,
            'type': '微信' if suffix == '-1' else '支付宝'
        }), 200

    except Exception as e:
        print(f"Error in upload_donation_qrcode: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    

@h5_apps_bp.route('/upload_screenshot_by_url', methods=['POST'])
def upload_screenshot_by_url():
    """通过URL上传截图，解决CORS问题"""
    try:
        print(f"通过URL上传截图: {request.form}")
        
        # 获取参数
        image_url = request.form.get('image_url')
        if not image_url:
            return jsonify({'error': '缺少图片URL'}), 400
            
        index = request.form.get('index')
        if not index:
            return jsonify({'error': '缺少图片序号'}), 400

        # 获取id参数
        id = request.form.get('id')
        if not id:
            return jsonify({'error': '缺少id参数'}), 400
            
        # 在后端下载图片
        try:
            # 如果URL是相对路径，添加BASE_URL
            if not image_url.startswith(('http://', 'https://')):
                if image_url.startswith('/'):
                    base_url = request.host_url.rstrip('/')
                    image_url = f"{base_url}{image_url}"
                else:
                    base_url = request.host_url.rstrip('/')
                    image_url = f"{base_url}/{image_url}"
            
            import requests
            response = requests.get(image_url, stream=True, timeout=10)
            if response.status_code != 200:
                return jsonify({'error': f'获取图片失败，状态码: {response.status_code}'}), 400
                
            # 从内存中创建文件对象
            from io import BytesIO
            file = BytesIO(response.content)
            file.seek(0)  # 确保文件指针在开始位置
            
            # 上传截图
            screenshot_url = upload_h5_screenshot(file, int(index), int(id))
            
            return jsonify({
                'success': True,
                'message': '截图上传成功',
                'path': screenshot_url,
                'url': screenshot_url,
                'index': int(index)
            }), 200
            
        except Exception as e:
            print(f"处理图片URL失败: {str(e)}")
            return jsonify({'error': f'处理图片URL失败: {str(e)}'}), 500

    except Exception as e:
        print(f"Error in upload_screenshot_by_url: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@h5_apps_bp.route('/upload_icon_by_url', methods=['POST'])
def upload_icon_by_url():
    """通过URL上传图标，解决CORS问题"""
    try:
        print(f"通过URL上传图标: {request.form}")
        
        # 获取参数
        image_url = request.form.get('image_url')
        if not image_url:
            return jsonify({'error': '缺少图片URL'}), 400

        # 获取id参数
        id = request.form.get('id')
        if not id:
            return jsonify({'error': '缺少id参数'}), 400
            
        # 在后端下载图片
        try:
            # 如果URL是相对路径，添加BASE_URL
            if not image_url.startswith(('http://', 'https://')):
                if image_url.startswith('/'):
                    base_url = request.host_url.rstrip('/')
                    image_url = f"{base_url}{image_url}"
                else:
                    base_url = request.host_url.rstrip('/')
                    image_url = f"{base_url}/{image_url}"
            
            import requests
            response = requests.get(image_url, stream=True, timeout=10)
            if response.status_code != 200:
                return jsonify({'error': f'获取图片失败，状态码: {response.status_code}'}), 400
                
            # 从内存中创建文件对象
            from io import BytesIO
            file = BytesIO(response.content)
            file.seek(0)  # 确保文件指针在开始位置
            
            # 上传图标
            icon_url = upload_h5_icon(file, int(id))
            
            return jsonify({
                'success': True,
                'message': '图标上传成功',
                'path': icon_url,
                'url': icon_url
            }), 200
            
        except Exception as e:
            print(f"处理图片URL失败: {str(e)}")
            return jsonify({'error': f'处理图片URL失败: {str(e)}'}), 500

    except Exception as e:
        print(f"Error in upload_icon_by_url: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@h5_apps_bp.route('/upload_donation_qrcode_by_url', methods=['POST'])
def upload_donation_qrcode_by_url():
    """通过URL上传打赏二维码，解决CORS问题"""
    try:
        print(f"通过URL上传二维码: {request.form}")
        
        # 获取参数
        image_url = request.form.get('image_url')
        if not image_url:
            return jsonify({'error': '缺少图片URL'}), 400

        # 获取id参数
        id = request.form.get('id')
        if not id:
            return jsonify({'error': '缺少id参数'}), 400
            
        # 获取后缀，-1代表微信，-2代表支付宝
        suffix = request.form.get('suffix', '')
        if suffix not in ['-1', '-2']:
            return jsonify({'success': False, 'error': '无效的二维码类型，必须是-1(微信)或-2(支付宝)'}), 400
            
        # 在后端下载图片
        try:
            # 如果URL是相对路径，添加BASE_URL
            if not image_url.startswith(('http://', 'https://')):
                if image_url.startswith('/'):
                    base_url = request.host_url.rstrip('/')
                    image_url = f"{base_url}{image_url}"
                else:
                    base_url = request.host_url.rstrip('/')
                    image_url = f"{base_url}/{image_url}"
            
            import requests
            response = requests.get(image_url, stream=True, timeout=10)
            if response.status_code != 200:
                return jsonify({'error': f'获取图片失败，状态码: {response.status_code}'}), 400
                
            # 从内存中创建文件对象
            from io import BytesIO
            file = BytesIO(response.content)
            file.seek(0)  # 确保文件指针在开始位置
            
            # 上传二维码
            qrcode_url = upload_donation_qrcode_file(file, int(id), suffix)
            
            return jsonify({
                'success': True,
                'message': '打赏二维码上传成功',
                'path': qrcode_url,
                'url': qrcode_url,
                'type': '微信' if suffix == '-1' else '支付宝'
            }), 200
            
        except Exception as e:
            print(f"处理图片URL失败: {str(e)}")
            return jsonify({'error': f'处理图片URL失败: {str(e)}'}), 500

    except Exception as e:
        print(f"Error in upload_donation_qrcode_by_url: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500