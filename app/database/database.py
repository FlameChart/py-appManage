from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy 实例
db = SQLAlchemy()


def init_db(app):
    """
    初始化数据库连接，并加载模型
    :param app: Flask 应用实例
    """
    db.init_app(app)
    with app.app_context():
        # 动态导入 models 文件夹中的所有模型
        from ..models import (
            User,
            H5App,
            UserH5App,
            AppFeedback,
            AppUserCount,
            AppUserScore,
            UserLoginData,
            AppApproval,
            AppExposure,
            AppReleaseDate,
            AppFeedbackLike,
            AppReview
        )  # noqa: F401

        # 创建所有数据表（包括主数据库和审核数据库）
        db.create_all()

        # 手动挂载 db.models
        db.models = {
            'User': User,
            'H5App': H5App,
            'UserH5App': UserH5App,
            'AppFeedback': AppFeedback,
            'AppUserCount': AppUserCount,
            'AppUserScore': AppUserScore,
            'UserLoginData': UserLoginData,
            'AppApproval': AppApproval,
            'AppExposure': AppExposure,
            'AppReleaseDate': AppReleaseDate,
            'AppFeedbackLike': AppFeedbackLike,
            'AppReview': AppReview
        }

        print("All tables have been created successfully.")


def create_triggers():
    """
    创建数据库触发器
    """
    from .create_triggers import create_triggers as triggers_logic
    triggers_logic()  # 调用 create_triggers.py 中的逻辑
