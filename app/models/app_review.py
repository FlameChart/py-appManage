from ..database.database import db


class AppReview(db.Model):
    __tablename__ = 'app_review'
    __bind_key__ = 'review_db'  # 指定使用review_db

    # 状态常量
    PENDING = 1  # 待审核
    REJECTED = 2  # 不合格
    APPROVED = 3  # 已通过

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    uploader = db.Column(db.String(255), nullable=False, comment='开发者/上传者')
    h5_name = db.Column(db.String(255), nullable=False, comment='应用名')
    deploy_url = db.Column(db.String(255), nullable=False, comment='部署地址')
    logo = db.Column(db.String(255), comment='图标URL')
    description = db.Column(db.Text, comment='简要描述')
    detail_description = db.Column(db.Text, comment='详细描述')
    category = db.Column(db.String(100), comment='分类')
    navbar = db.Column(db.Integer, default=0, comment='导航栏置顶状态（0.不置顶 1.置顶）')
    status = db.Column(db.Integer, default=1, comment='状态（1.待审核 2.不合格 3.已通过）')
    donation_qrcode = db.Column(db.String(255), comment='打赏二维码URL')
    reply = db.Column(db.Text, comment='回复内容')

    def to_dict(self):
        return {
            'id': self.id,
            'uploader': self.uploader,
            'h5_name': self.h5_name,
            'deploy_url': self.deploy_url,
            'logo': self.logo,
            'description': self.description,
            'detail_description': self.detail_description,
            'category': self.category,
            'navbar': self.navbar,
            'status': self.status,
            'donation_qrcode': self.donation_qrcode,
            'reply': self.reply
        }

    @property
    def status_text(self):
        """获取状态的文本描述"""
        status_map = {
            self.PENDING: '待审核',
            self.REJECTED: '不合格',
            self.APPROVED: '已通过'
        }
        return status_map.get(self.status, '未知状态')

    def __repr__(self):
        return f'<AppReview {self.h5_name}>' 