from datetime import date

from ..database import db


class UserLoginData(db.Model):
    __tablename__ = 'user_login_data'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)  # 用户ID，联合主键之一
    login_date = db.Column(db.Date, primary_key=True, default=date.today)  # 登录日期，联合主键之一

    def __repr__(self):
        return f'<UserLoginData(user_id={self.user_id}, login_date={self.login_date})>'

    def to_dict(self):
        """将登录记录转换为字典"""
        return {
            "user_id": self.user_id,
            "login_date": self.login_date
        }
