from ..database import db


class AppUserScore(db.Model):
    """
    App 用户评分排序表
    """
    __tablename__ = 'app_user_scores'

    h5_id = db.Column(db.Integer, db.ForeignKey('h5_apps.h5_id'), primary_key=True)  # H5 应用 ID
    app_score = db.Column(db.Float, nullable=False, default=0.0)  # H5 应用评分

    def __repr__(self):
        return f'<AppUserScore(h5_id={self.h5_id}, app_score={self.app_score})>'

    def to_dict(self):
        """将评分记录转换为字典"""
        return {
            "h5_id": self.h5_id,
            "app_score": self.app_score
        }
