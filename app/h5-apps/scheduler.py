from flask_apscheduler import APScheduler

from app.database import db
from app.models import AppExposure

scheduler = APScheduler()

def updateScheduler(flask):
    scheduler.init_app(flask)

    @scheduler.task('cron', hour=4)
    def task():
        with flask.app_context():
            try:
                exposures = AppExposure.query.all()
                current_time = datetime.now()

                for exp in exposures:
                    if exp.exposure > 0:
                        new_exposure = math.floor(exp.exposure * 0.97)
                        exp.exposure = new_exposure
                        exp.last_update = current_time

                db.session.commit()
                return {'success': True, 'message': f'成功更新 {len(exposures)} 个应用的曝光值'}, 200
            except Exception as e:
                print(f"更新曝光值失败: {e}")
                db.session.rollback()
                return {'success': False, 'message': str(e)}, 500

    scheduler.start()