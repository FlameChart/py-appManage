from datetime import date

from ..database import db


class AppFeedback(db.Model):
    __tablename__ = 'app_feedback'
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 反馈的唯一 ID
    h5_id = db.Column(db.Integer, db.ForeignKey('h5_apps.h5_id'), nullable=False)  # 应用 ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 用户 ID
    feedback = db.Column(db.Text, nullable=False)  # 反馈内容
    date = db.Column(db.Date, default=date.today, nullable=False)  # 反馈日期
    user_score=db.Column(db.Integer, nullable=False)  # 用户评分
    def __repr__(self):
        return f'<AppFeedback(feedback_id={self.feedback_id}, h5_id={self.h5_id}, user_id={self.user_id}, date={self.date})>'

    def to_dict(self):
        """将反馈对象转换为字典"""
        return {
            "feedback_id": self.feedback_id,
            "h5_id": self.h5_id,
            "user_id": self.user_id,
            "feedback": self.feedback,
            "date": self.date
        }
