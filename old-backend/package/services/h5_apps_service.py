import glob
from _operator import not_
from urllib import request

from flask import jsonify

from ..models.app_feedback_like import AppFeedbackLike
from ..database import db
from ..models.h5_apps import H5App
from ..models.app_approval import AppApproval
from ..models.app_exposure import AppExposure
from ..models.app_feedback import AppFeedback
from ..models.app_release_date import AppReleaseDate
from sqlalchemy import text
from ..models.app_user_count import AppUserCount
from ..models.app_user_scores import AppUserScore
from ..models.user_h5_apps import UserH5App
from ..models.users import User
from sqlalchemy import func
from datetime import datetime
import math
import os
from ..models.app_review import AppReview
from ..utils.oss import upload, OssDir


# 验证文件类型
def allowed_file(filename):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_next_h5_id():
    """获取下一个可用的h5_id"""
    try:
        max_id = db.session.query(db.func.max(H5App.h5_id)).scalar()
        return (max_id if max_id else 0) + 1
    except Exception as e:
        raise ValueError(f'获取H5 ID失败: {str(e)}')
    
def get_next_review_id():
    """获取下一个可用的review_id"""
    try:
        max_id = db.session.query(db.func.max(AppReview.id)).scalar()
        return (max_id if max_id else 0) + 1
    except Exception as e:
        raise ValueError(f'获取审核APP ID失败: {str(e)}')


def upload_h5_icon(file, id):
    """
    上传H5应用图标到OSS
    :param file: 上传的文件对象
    :param id: 应用ID
    :return: 图标的OSS访问URL
    """
    # 文件名格式化
    filename = f"{id}.png"
    
    # 使用OSS工具上传文件
    url = upload(file, filename, OssDir.APP_ICON)
    
    return url


def upload_h5_screenshot(file, index, id):
    """
    上传H5应用截图到OSS
    :param file: 上传的文件对象
    :param index: 截图索引
    :param id: 应用ID
    :return: 截图的OSS访问URL
    """
    # 文件名格式化
    filename = f"{id}-{index}.png"
    
    # 使用OSS工具上传文件
    url = upload(file, filename, OssDir.APP_SCREENSHOT)
    
    return url


def upload_h5_app(data):
    """
    上传新的 H5 应用
    :param data: 包含 H5 应用信息的字典
    :return: 创建的H5App对象
    """
    try:
        print("上传H5应用数据:", {k: v if k != 'password' else '******' for k, v in data.items()})

        # 验证uploader字段
        if 'uploader' not in data:
            raise ValueError("缺少uploader字段，无法确定上传者")

        # 获取下一个可用的h5_id
        new_h5_id = get_next_h5_id()

        cleaned_data = {
            'h5_id': new_h5_id,
            'uploader': str(data['uploader']),  # 转换为字符串
            'h5_name': data['h5_name'][:8],
            'deploy_url': data['deploy_url'].strip(),
            'description': data['description'][:14],
            'detail_description': data.get('detail_description', '')[:200],
            'category': data['category'],
            'navbar': 1 if (data.get('navbar') == True or data.get('navbar') == 'true' or data.get('navbar') == '需要') else 0,
            'logo': data.get('logo', ''),  # 直接使用传递的logo URL
            'donation_qrcode_wx': data.get('donation_qrcode_wx', None),
            'donation_qrcode_zfb': data.get('donation_qrcode_zfb', None),
            'screenshot': data.get('screenshot', None),
            'status': 1  # 设置为上架状态
        }

        print("清理后的数据:", cleaned_data)

        try:
            # 开启事务
            new_app = H5App(**cleaned_data)
            db.session.add(new_app)
            # 先提交H5App，确保h5_id存在
            db.session.flush()
            
            # 创建相关记录
            # 初始化曝光值为0
            app_exposure = AppExposure(h5_id=new_h5_id, exposure=0)
            db.session.add(app_exposure)
            
            # 初始化用户数量为0
            app_user_count = AppUserCount(h5_id=new_h5_id, user_number=0)
            db.session.add(app_user_count)
            
            # 记录发布日期
            app_release_date = AppReleaseDate(h5_id=new_h5_id, release_date=datetime.now())
            db.session.add(app_release_date)
            
            # 添加用户与应用关联记录
            max_sort_order = db.session.query(func.max(UserH5App.sort_order)).filter(UserH5App.user_id == str(data['uploader'])).scalar() or 0
            new_user_h5_app = UserH5App(user_id=str(data['uploader']), h5_id=new_h5_id, sort_order=max_sort_order + 1)
            db.session.add(new_user_h5_app)

            # 添加应用评分记录
            app_user_score = AppUserScore(h5_id=new_h5_id, app_score=0)
            db.session.add(app_user_score)
            
            # 最后提交所有更改
            db.session.commit()

            return new_app

        except Exception as e:
            db.session.rollback()
            print(f"数据库错误: {str(e)}")
            raise ValueError(f"保存H5应用失败: {str(e)}")

    except ValueError as ve:
        raise ve
    except Exception as e:
        print(f"错误详情: {str(e)}, 类型: {type(e)}")
        raise ValueError(f'保存H5应用失败: {str(e)}')


def get_user_uploaded_apps(user_id):
    try:
        # 查询已上架的应用
        approved_apps = db.session.query(
            H5App,
            AppUserScore.app_score,
            AppExposure.exposure
        ).outerjoin(
            AppUserScore, H5App.h5_id == AppUserScore.h5_id
        ).outerjoin(
            AppExposure, H5App.h5_id == AppExposure.h5_id
        ).filter(
            H5App.uploader == user_id
        ).all()

        # # 查询审核中的应用
        # reviewing_apps = AppReview.query.filter(
        #     AppReview.uploader == str(user_id)  # 转换为字符串
        # ).all()

        # 合并结果
        result = []
        
        # 添加已上架的应用
        for app in approved_apps:
            result.append({
                **app[0].to_dict(),
                'app_score': app[1] or 0,
                'exposure': app[2] or 0,
                'status': 'approved'  # 标记为已上架
            })
        
        # # 添加审核中的应用
        # for review in reviewing_apps:
        #     result.append({
        #         **review.to_dict(),
        #         'app_score': 0,
        #         'exposure': 0,
        #         'status': review.status_text  # 使用状态文本
        #     })

        return result
    except Exception as e:
        print(f"获取用户上传的应用失败: {e}")
        return None


def get_app_detail_service(user_id=None, h5_id=None):
    """获取应用详情"""
    try:
        base_query1 = db.session.query(
            H5App.h5_id,
            H5App.logo.label('应用图标'),
            H5App.deploy_url,
            H5App.navbar,
            H5App.donation_qrcode_wx.label('微信打赏二维码'),  
            H5App.donation_qrcode_zfb.label('支付宝打赏二维码'),
            H5App.screenshot.label('应用截图'),
            H5App.h5_name.label('应用名称'),
            H5App.category.label('应用分类'),
            H5App.description,
            H5App.detail_description,
            User.user_name,
            User.avatar,
            AppReleaseDate.release_date,
            AppUserScore.app_score.label('应用评分'),
            AppUserCount.user_number.label('用户数量'),
            AppExposure.exposure.label('曝光值')  # 确保获取曝光值
        )

        subquery_relation_count = db.session.query(db.func.count()).filter(
            UserH5App.h5_id == h5_id
        )
        if user_id is not None:
            subquery_relation_count = subquery_relation_count.filter(
                UserH5App.user_id == user_id
            )
        subquery_relation_count = subquery_relation_count.scalar_subquery()

        query1 = base_query1.add_columns(
            (subquery_relation_count > 0).label('是否关联')
        ).outerjoin(
            AppUserScore, H5App.h5_id == AppUserScore.h5_id
        ).outerjoin(
            AppUserCount, H5App.h5_id == AppUserCount.h5_id
        ).outerjoin(
            AppReleaseDate, H5App.h5_id == AppReleaseDate.h5_id
        ).outerjoin(
            AppExposure, H5App.h5_id == AppExposure.h5_id
        ).join(
            User, H5App.uploader == User.user_id
        ).filter(
            H5App.h5_id == h5_id
        )
        result1 = query1.all()

        like_count_subquery = db.session.query(
            AppFeedbackLike.feedback_id,
            func.count(AppFeedbackLike.id).label('like_count')
        ).group_by(AppFeedbackLike.feedback_id).subquery()

        query2 = db.session.query(
            User.avatar,
            User.user_name,
            AppFeedback.feedback_id,
            AppFeedback.user_score,
            AppFeedback.date,
            AppFeedback.feedback,
            func.coalesce(like_count_subquery.c.like_count, 0).label('like_count')
        ).join(
            User, User.user_id == AppFeedback.user_id
        ).outerjoin(
            like_count_subquery, AppFeedback.feedback_id == like_count_subquery.c.feedback_id
        ).filter(
            AppFeedback.h5_id == h5_id
        )
        result2 = query2.all()

        subquery = db.session.query(UserH5App.h5_id).filter(
            UserH5App.user_id == user_id
        ).subquery()

        query3 = db.session.query(
            H5App.h5_id,
            H5App.logo,
            H5App.h5_name,
            AppUserScore.app_score
        ).outerjoin(
            AppUserScore, H5App.h5_id == AppUserScore.h5_id
        ).filter(H5App.h5_id.notin_(subquery))
        result3 = query3.all()

        query4 = db.session.query(
            AppUserScore.h5_id,
            AppUserScore.app_score
        )
        result4 = query4.all()

        combined_result = {
            "基本信息": [row._asdict() for row in result1],
            "用户反馈信息": [row._asdict() for row in result2],
            "未关联用户应用信息": [row._asdict() for row in result3],
            "AppUserScore": {row[0]: row[1] for row in result4}
        }
        return combined_result
    except Exception as e:
        print(f"数据库查询出现错误: {e}")
        db.session.rollback()
        return None


def update_h5_app_service(data):
    """更新H5应用信息"""
    try:
        app = H5App.query.get(data['h5_id'])
        if not app:
            return {'success': False, 'message': '应用不存在'}, 404

        if 'status' in data:
            app.status = data['status']
        if 'h5_name' in data:
            app.h5_name = data['h5_name']
        if 'deploy_url' in data:
            app.deploy_url = data['deploy_url']
        if 'description' in data:
            app.description = data['description']
        if 'detail_description' in data:
            app.detail_description = data['detail_description']
        if 'category' in data:
            app.category = data['category']
        if 'donation_qrcode_wx' in data:
            app.donation_qrcode_wx = data['donation_qrcode_wx']
        if 'donation_qrcode_zfb' in data:
            app.donation_qrcode_zfb = data['donation_qrcode_zfb']
        if 'screenshot' in data:
            app.screenshot = data['screenshot']
        if 'logo' in data:
            app.logo = data['logo']


        db.session.commit()

        return {
            'success': True,
            'message': '更新成功',
            'data': app.to_dict()
        }, 200
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500


def delete_h5_app_service(h5_id):
    """下架H5应用"""
    try:
        # delete app_user_count
        app_user_count = AppUserCount.query.get(h5_id)
        if app_user_count  != None:
            db.session.delete(app_user_count)
            db.session.commit()

        # delete app_release_date
        app_release_date = AppReleaseDate.query.get(h5_id)
        if app_release_date != None:
            db.session.delete(app_release_date)
            db.session.commit()

        # delete app_approval
        app_approval = AppApproval.query.get(h5_id)
        if app_approval != None:
            db.session.delete(app_approval)
            db.session.commit()

        # delete app_exposure
        app_exposure = AppExposure.query.get(h5_id)
        if app_exposure != None:
            db.session.delete(app_exposure)
            db.session.commit()

        app = H5App.query.get(h5_id)
        if not app:
            return {'success': False, 'message': '应用不存在'}, 404

        db.session.delete(app)
        db.session.commit()
        return {'success': True, 'message': '下架成功'}, 200
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500


def promote_h5_app_service(data):
    """推广H5应用"""
    try:
        h5_id = int(data.get('h5_id'))
        user_id = int(data.get('user_id'))
        coin_amount = int(data.get('coin_amount', 0))

        # 基础验证
        if not all([h5_id, user_id, coin_amount]):
            return {'success': False, 'message': '缺少必要参数'}, 400

        # 验证用户
        user = db.models["User"].query.get(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}, 404

        # 验证H币余额
        if user.coin < coin_amount:
            return {'success': False, 'message': 'H币余额不足'}, 400

        # 验证应用
        app = db.models["H5App"].query.get(h5_id)
        if not app:
            return {'success': False, 'message': '应用不存在'}, 404
        if getattr(app, 'status', 1) == 0:
            return {'success': False, 'message': '应用已下架'}, 400

        # 扣除H币
        user.coin -= coin_amount

        # 增加曝光值
        exposure = db.models["AppExposure"].query.get(h5_id)
        if not exposure:
            exposure = db.models["AppExposure"](h5_id=h5_id, exposure=0.0)
            db.session.add(exposure)

        # 每个H币增加100曝光值
        exposure.exposure += float(coin_amount * 100)  # 确保使用浮点数

        try:
            db.session.commit()  # 这会触发更新触发器

            return {
                'success': True,
                'message': '推广成功',
                'data': {
                    'remaining_coin': user.coin,
                    'current_exposure': exposure.exposure
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            print(f"Error in promote_h5_app_service while committing: {e}")
            return {'success': False, 'message': '数据库更新失败'}, 500

    except ValueError as e:
        return {'success': False, 'message': '参数格式错误'}, 400
    except Exception as e:
        print(f"Error in promote_h5_app_service: {e}")
        db.session.rollback()
        return {'success': False, 'message': '推广失败，请稍后重试'}, 500


def upload_donation_qrcode_file(file, id, suffix):
    """
    上传打赏二维码到OSS
    :param file: 上传的文件对象
    :param id: 应用ID
    :param suffix: 后缀（区分微信和支付宝）
    :return: 二维码的OSS访问URL
    """
    # 文件名格式化
    filename = f"{id}{suffix}.png"
    
    # 使用OSS工具上传文件
    url = upload(file, filename, OssDir.APP_DONATION_QRCODE)
    
    return url


def update_exposure_service():
    """更新所有应用的曝光值(每日定时任务)"""
    try:
        exposures = AppExposure.query.all()
        current_time = datetime.now()

        for exp in exposures:
            # 计算3%的折损
            if exp.exposure > 0:
                new_exposure = math.floor(exp.exposure * 0.97)
                exp.exposure = new_exposure
                exp.last_update = current_time

        db.session.commit()
        return {'success': True, 'message': f'成功更新 {len(exposures)} 个应用的曝光值'}, 200
    except Exception as e:
        print(f"更新曝光值失败: {e}")
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500
    
    