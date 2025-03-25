import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class H5Apps(Base):
    __tablename__ = 'h5_apps'

    h5_id = Column(Integer, primary_key=True, autoincrement=True)
    h5_name = Column(String(255), nullable=False)
    description = Column(Text)
    detail_description = Column(Text)
    uploader = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    deploy_url = Column(String(255), nullable=False)
    logo = Column(Text)
    category = Column(String(100), nullable=False)
    navbar = Column(Boolean)
    status = Column(Integer, default=1)  # 1-上架 0-下架
    donation_qrcode_wx = Column(String(255))
    donation_qrcode_zfb = Column(String(255))
    screenshot = Column(Text)
    release_date = relationship('AppReleaseDate', backref='h5_app', uselist=False)
    user_count = relationship('AppUserCount', backref='h5_app', uselist=False)

    def to_dict(self):
        return {
            'h5_id': self.h5_id,
            'h5_name': self.h5_name,
            'description': self.description,
            'detail_description': self.detail_description,
            'uploader': self.uploader,
            'deploy_url': self.deploy_url,
            'logo': self.logo,
            'category': self.category,
            'navbar': self.navbar,
            'status': self.status,
            'donation_qrcode_wx': self.donation_qrcode_wx,
            'donation_qrcode_zfb': self.donation_qrcode_zfb,
            'screenshot': self.screenshot
        }

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
