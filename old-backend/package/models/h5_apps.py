from . import AppReleaseDate
from ..database import db


class H5App(db.Model):
    __tablename__ = 'h5_apps'

    h5_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uploader = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    h5_name = db.Column(db.String(255), nullable=False)
    deploy_url = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.Text)
    description = db.Column(db.Text)
    detail_description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    navbar = db.Column(db.Boolean)
    status = db.Column(db.Integer, default=1)  # 1-上架 0-下架
    donation_qrcode_wx = db.Column(db.String(255))
    donation_qrcode_zfb = db.Column(db.String(255))
    screenshot = db.Column(db.Text)
    release_date = db.relationship('AppReleaseDate', backref='h5_app', uselist=False)
    user_count = db.relationship('AppUserCount', backref='h5_app', uselist=False)

    def to_dict(self):
        return {
            'h5_id': self.h5_id,
            'uploader': self.uploader,
            'h5_name': self.h5_name,
            'deploy_url': self.deploy_url,
            'logo': self.logo,
            'description': self.description,
            'detail_description': self.detail_description,
            'category': self.category,
            'navbar': self.navbar,
            'status': self.status,
            'donation_qrcode_wx': self.donation_qrcode_wx,
            'donation_qrcode_zfb': self.donation_qrcode_zfb,
            'screenshot': self.screenshot,
            'release_date': self.release_date.release_date.strftime('%Y-%m-%d') if self.release_date else None,
            'user_number': self.user_count.user_number if self.user_count else 0
        }

    def __repr__(self):
        return f'<H5App {self.h5_name}>'
