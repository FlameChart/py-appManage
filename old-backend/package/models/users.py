from werkzeug.security import generate_password_hash, check_password_hash  # 用于密码加密

from ..database import db


class  User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(512), nullable=False)  # 增加密码字段长度，因为加密后的密码会很长
    coin = db.Column(db.Integer, nullable=True, default=0)

    # 定义与H5应用的关系
    h5_apps = db.relationship('H5App', secondary='user_h5_apps', backref='users')

    def set_password(self, password):
        """对密码进行加密"""
        if password:  # 确保密码不为空
            self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """验证密码"""
        if not password or not self.password:  # 增加空值检查
            return False
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "avatar": self.avatar,
            "email": self.email,
            "coin": self.coin,
        }
