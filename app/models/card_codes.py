from ..database import db


class CardCode(db.Model):
    __tablename__ = 'card_codes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增ID，主键
    code = db.Column(db.String(255), nullable=False, unique=True)  # 卡密内容，唯一
    value = db.Column(db.Integer, nullable=False)  # 面值（对应H币数量）
    is_used = db.Column(db.Boolean, default=False)  # 是否已使用
    used_at = db.Column(db.DateTime, nullable=True)  # 兑换时间
    used_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)  # 兑换用户ID，外键关联用户表
    
    def to_dict(self):
        """将卡密对象转换为字典"""
        return {
            "id": self.id,
            "code": self.code,
            "value": self.value,
            "is_used": self.is_used,
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "used_by": self.used_by
        }
    
    def __repr__(self):
        return f'<CardCode {self.code} - Value: {self.value}>'
