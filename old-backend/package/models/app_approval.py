from ..database import db  # 使用相对路径导入 db


class AppApproval(db.Model):
    """
    App 综合排序表
    """
    __tablename__ = 'app_approval'  # 数据库表名

    h5_id = db.Column(db.Integer, db.ForeignKey('h5_apps.h5_id'), primary_key=True)  # H5 应用 ID，外键关联 H5App 表
    approval = db.Column(db.Float, nullable=False, default=0.0)  # 综合评分，根据用户量、评分、发布日期、曝光度加权计算

    def __repr__(self):
        return f'<AppApproval(h5_id={self.h5_id}, approval={self.approval})>'

    def to_dict(self):
        """
        将记录转换为字典格式
        """
        return {
            "h5_id": self.h5_id,
            "approval": round(self.approval, 2)  # 保留两位小数
        }
