from ..database import db


class UserH5App(db.Model):
    __tablename__ = 'user_h5_apps'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    h5_id = db.Column(db.Integer, db.ForeignKey('h5_apps.h5_id'), primary_key=True)
    sort_order = db.Column(db.Integer, default=0)  # 新增排序字段

    def __repr__(self):
        return f'<UserH5App(user_id={self.user_id}, h5_id={self.h5_id}, sort_order={self.sort_order})>'

