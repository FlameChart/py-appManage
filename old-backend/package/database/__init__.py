"""
database 包的初始化文件

集中导入数据库实例和所有模型：
- db: SQLAlchemy 实例
- init_db: 数据库初始化函数
- create_triggers: 数据库触发器创建函数
"""

from .database import db, init_db, create_triggers
