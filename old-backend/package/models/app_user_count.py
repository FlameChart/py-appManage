from ..database import db


class AppUserCount(db.Model):
    __tablename__ = 'app_user_count'
    h5_id = db.Column(db.Integer, db.ForeignKey('h5_apps.h5_id'), primary_key=True)  # H5应用ID
    user_number = db.Column(db.Integer, nullable=False, default=0)  # 用户数量

    def __repr__(self):
        return f'<AppUserCount(h5_id={self.h5_id}, user_number={self.user_number})>'

    def to_dict(self):
        """将用户数量记录转换为字典"""
        return {
            "h5_id": self.h5_id,
            "user_number": self.user_number
        }
