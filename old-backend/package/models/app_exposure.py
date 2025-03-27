from ..database import db  # 使用相对路径导入 db


class AppExposure(db.Model):
    """
    App 曝光排序表
    """
    __tablename__ = 'app_exposure'

    h5_id = db.Column(db.Integer, db.ForeignKey('h5_apps.h5_id'), primary_key=True)
    exposure = db.Column(db.Float, nullable=False)

    def __init__(self, h5_id, exposure=0.0):
        self.h5_id = h5_id
        self.exposure = float(exposure)

    def __repr__(self):
        return f'<AppExposure {self.h5_id}>'

    def to_dict(self):
        return {
            'h5_id': self.h5_id,
            'exposure': self.exposure
        }
