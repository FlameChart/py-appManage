from flask import Flask, request
from flask_cors import CORS
from flask_apscheduler import APScheduler
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from config import Config
from package.database import init_db, create_triggers
from package.routers import register_blueprints
from package.utils.mail import mail
from package.routers.h5_apps import init_scheduler
from package.utils.jwt import jwt_middleware

def create_app():
    """
    创建并配置 Flask 应用实例
    :return: Flask 应用实例
    """
    # 创建 Flask 应用实例
    app = Flask(__name__)
    
    # 从配置对象加载配置
    app.config.from_object(Config)

    # 配置 CORS（跨域资源共享）
    # 允许所有来源的跨域请求，并指定允许的 HTTP 方法和头部
    CORS(app, resources={r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }})

    # 处理预检请求（OPTIONS 请求）
    @app.before_request
    def handle_preflight():
        """处理浏览器发送的预检请求"""
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            return response

    # 添加 JWT 中间件，用于处理需要身份验证的请求
    @app.before_request
    def middleware_wrapper():
        """在每个请求之前执行 JWT 中间件"""
        response = jwt_middleware()
        if response:  # 如果中间件返回响应，直接返回，不再处理请求
            return response

    # 配置 JWT（JSON Web Token）
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY  # 设置 JWT 密钥
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES  # 设置 token 过期时间

    # 初始化邮件工具
    mail.init_app(app)

    # 初始化 JWT 管理器
    JWTManager(app)

    # 初始化数据库
    init_db(app)

    # 注册所有路由蓝图
    register_blueprints(app)

    # 初始化定时任务调度器
    init_scheduler(app)

    # 定义根路由
    @app.route('/')
    def welcome():
        """网站根路径的欢迎页面"""
        return "欢迎来到林智清的服务器后台，但是这里什么都没有，去别处看看吧"

    return app


if __name__ == '__main__':
    # 创建应用实例
    app = create_app()

    # 在应用上下文中创建数据库触发器
    with app.app_context():
        create_triggers()

    # 启动应用服务器
    # host='0.0.0.0' 表示监听所有网络接口
    # port=5001 指定服务器端口
    # debug=True 启用调试模式
    app.run(host='0.0.0.0', port=5001, debug=True)