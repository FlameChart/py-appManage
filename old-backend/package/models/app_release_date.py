from datetime import date

from ..database import db  # 使用相对路径导入 db


class AppReleaseDate(db.Model):
    """
    App 发布日期排序表
    """
    __tablename__ = 'app_release_date'

    h5_id = db.Column(db.Integer, db.ForeignKey('h5_apps.h5_id'), primary_key=True)  # H5 应用 ID
    release_date = db.Column(db.Date, nullable=False, default=date.today)  # 发布日期，默认当天

    def __repr__(self):
        return f'<AppReleaseDate(h5_id={self.h5_id}, release_date={self.release_date})>'

    def to_dict(self):
        """将记录转换为字典"""
        return {
            "h5_id": self.h5_id,
            "release_date": self.release_date.strftime('%Y-%m-%d') if self.release_date else None
        }

    @staticmethod
    def get_sorted_by_date_desc():
        """
        获取按发布日期降序排列的记录
        """
        return AppReleaseDate.query.order_by(AppReleaseDate.release_date.desc()).all()
