from ..database import db

class AppFeedbackLike(db.Model):
    __tablename__ = 'app_feedback_like'
    # 点赞记录的唯一标识，自增主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 用户 ID，外键关联到用户表的 user_id 字段
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    # 反馈 ID，外键关联到反馈表的 feedback_id 字段
    feedback_id = db.Column(db.Integer, db.ForeignKey('app_feedback.feedback_id'), nullable=False)
    # 点赞时间，默认为当前时间
    like_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def to_dict(self):
        """将点赞对象转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feedback_id": self.feedback_id,
            # 格式化点赞时间为字符串，如果为 None 则返回 None
            "like_time": self.like_time.strftime('%Y-%m-%d %H:%M:%S') if self.like_time else None
        }

    def __repr__(self):
        return f'<AppFeedbackLike( user_id={self.user_id}, feedback_id={self.feedback_id}, like_time={self.like_time})>'