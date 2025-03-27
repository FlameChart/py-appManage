from .database import db
from sqlalchemy import text

def create_triggers():
    """
    创建数据库触发器
    """
    trigger_insert = """
    CREATE TRIGGER after_user_h5_apps_insert
    AFTER INSERT ON user_h5_apps
    FOR EACH ROW
    BEGIN
        INSERT INTO app_user_count (h5_id, user_number)
        VALUES (NEW.h5_id, 1)
        ON DUPLICATE KEY UPDATE user_number = user_number + 1;
    END
    """

    trigger_delete = """
    CREATE TRIGGER after_user_h5_apps_delete
    AFTER DELETE ON user_h5_apps
    FOR EACH ROW
    BEGIN
        UPDATE app_user_count
        SET user_number = user_number - 1
        WHERE h5_id = OLD.h5_id;
    END
    """

    # trigger_rating_update = """
    # CREATE TRIGGER after_app_ratings_update
    # AFTER INSERT ON app_ratings
    # FOR EACH ROW
    # BEGIN
    #     INSERT INTO app_user_scores (h5_id, app_score)
    #     VALUES (NEW.h5_id, (SELECT AVG(score) FROM app_ratings WHERE h5_id = NEW.h5_id))
    #     ON DUPLICATE KEY UPDATE app_score = (SELECT AVG(score) FROM app_ratings WHERE h5_id = NEW.h5_id);
    # END
    # """
    trigger_user_count = """
     CREATE TRIGGER after_app_user_count_update
     AFTER UPDATE ON app_user_count
     FOR EACH ROW
     BEGIN
         DECLARE new_approval FLOAT;
         SET new_approval = (
             -- app_score: 40%权重
             COALESCE((SELECT app_score / 5.0 FROM app_user_scores WHERE h5_id = NEW.h5_id), 0) * 0.4 +

             -- user_number: 30%权重
             (SELECT COUNT(CASE WHEN uc.user_number <= NEW.user_number THEN 1 END) * 1.0 / COUNT(*) 
              FROM app_user_count uc) * 0.3 +

             -- exposure: 20%权重
             COALESCE((SELECT COUNT(CASE WHEN e.exposure <= (SELECT exposure FROM app_exposure WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*)
              FROM app_exposure e), 0) * 0.2 +

             -- release_date: 10%权重
             COALESCE((SELECT COUNT(CASE WHEN rd.release_date <= (SELECT release_date FROM app_release_date WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*)
              FROM app_release_date rd), 0) * 0.1
         );

         INSERT INTO app_approval (h5_id, approval)
         VALUES (NEW.h5_id, new_approval)
         ON DUPLICATE KEY UPDATE approval = new_approval;
     END
     """

    trigger_user_scores = """
     CREATE TRIGGER after_app_user_scores_update
     AFTER UPDATE ON app_user_scores
     FOR EACH ROW
     BEGIN
         DECLARE new_approval FLOAT;
         SET new_approval = (
             COALESCE(NEW.app_score / 5.0, 0) * 0.4 +

             (SELECT COUNT(CASE WHEN uc.user_number <= (SELECT user_number FROM app_user_count WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*) 
              FROM app_user_count uc) * 0.3 +

             COALESCE((SELECT COUNT(CASE WHEN e.exposure <= (SELECT exposure FROM app_exposure WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*)
              FROM app_exposure e), 0) * 0.2 +

             COALESCE((SELECT COUNT(CASE WHEN rd.release_date <= (SELECT release_date FROM app_release_date WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*)
              FROM app_release_date rd), 0) * 0.1
         );

         INSERT INTO app_approval (h5_id, approval)
         VALUES (NEW.h5_id, new_approval)
         ON DUPLICATE KEY UPDATE approval = new_approval;
     END
     """

    trigger_exposure = """
     CREATE TRIGGER after_app_exposure_update
     AFTER UPDATE ON app_exposure
     FOR EACH ROW
     BEGIN
         DECLARE new_approval FLOAT;
         SET new_approval = (
             COALESCE((SELECT app_score / 5.0 FROM app_user_scores WHERE h5_id = NEW.h5_id), 0) * 0.4 +

             (SELECT COUNT(CASE WHEN uc.user_number <= (SELECT user_number FROM app_user_count WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*) 
              FROM app_user_count uc) * 0.3 +

             COALESCE((SELECT COUNT(CASE WHEN e.exposure <= NEW.exposure THEN 1 END) * 1.0 / COUNT(*)
              FROM app_exposure e), 0) * 0.2 +

             COALESCE((SELECT COUNT(CASE WHEN rd.release_date <= (SELECT release_date FROM app_release_date WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*)
              FROM app_release_date rd), 0) * 0.1
         );

         INSERT INTO app_approval (h5_id, approval)
         VALUES (NEW.h5_id, new_approval)
         ON DUPLICATE KEY UPDATE approval = new_approval;
     END
     """

    trigger_release_date = """
     CREATE TRIGGER after_app_release_date_insert
     AFTER UPDATE ON app_release_date
     FOR EACH ROW
     BEGIN
         DECLARE new_approval FLOAT;
         SET new_approval = (
             COALESCE((SELECT app_score / 5.0 FROM app_user_scores WHERE h5_id = NEW.h5_id), 0) * 0.4 +

             (SELECT COUNT(CASE WHEN uc.user_number <= (SELECT user_number FROM app_user_count WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*) 
              FROM app_user_count uc) * 0.3 +

             COALESCE((SELECT COUNT(CASE WHEN e.exposure <= (SELECT exposure FROM app_exposure WHERE h5_id = NEW.h5_id) THEN 1 END) * 1.0 / COUNT(*)
              FROM app_exposure e), 0) * 0.2 +

             COALESCE((SELECT COUNT(CASE WHEN rd.release_date <= NEW.release_date THEN 1 END) * 1.0 / COUNT(*)
              FROM app_release_date rd), 0) * 0.1
         );

         INSERT INTO app_approval (h5_id, approval)
         VALUES (NEW.h5_id, new_approval)
         ON DUPLICATE KEY UPDATE approval = new_approval;
     END
     """

    with db.engine.connect() as connection:
        try:
            print("Creating triggers...")
            # 开始事务
            with connection.begin():
                # 删除旧触发器，使用text()包装SQL语句
                connection.execute(text("DROP TRIGGER IF EXISTS after_user_h5_apps_insert"))
                connection.execute(text("DROP TRIGGER IF EXISTS after_user_h5_apps_delete"))
                # connection.execute(text("DROP TRIGGER IF EXISTS after_app_ratings_update"))
                connection.execute(text("DROP TRIGGER IF EXISTS after_app_user_count_update"))
                connection.execute(text("DROP TRIGGER IF EXISTS after_app_user_scores_update"))
                connection.execute(text("DROP TRIGGER IF EXISTS after_app_exposure_update"))
                connection.execute(text("DROP TRIGGER IF EXISTS after_app_release_date_insert"))

                # 创建新触发器，同样使用text()包装
                connection.execute(text(trigger_insert))
                connection.execute(text(trigger_delete))
                # connection.execute(text(trigger_rating_update))
                connection.execute(text(trigger_user_count))
                connection.execute(text(trigger_user_scores))
                connection.execute(text(trigger_exposure))
                connection.execute(text(trigger_release_date))
            
            print("Triggers created successfully.")
        except Exception as e:
            print(f"Error creating triggers: {e}")


