from database.db import db 
from zero_totp_db_model.model import LoginLogs as LoginLogs_Model
from uuid import uuid4
import datetime as dt
from environment import logging

class LoginLogs:
    def create_login_log(self, source_ip,user_id):
        if not source_ip:
            logging.error(f"Was creating login logs for {user_id} but IP is None")
            return "-1"  # to not make fail futur call, but will generate error login
        log = LoginLogs_Model(id=str(uuid4()), timestamp=dt.datetime.now(dt.UTC).timestamp(), source_ip=source_ip, user_id=user_id)
        db.session.add(log)
        db.session.commit()
        return log.id

    def update_login_status(self, id, status, outcome):
        log = db.session.query(LoginLogs_Model).filter_by(id=id).first()
        if log == None:
            logging.error(f"Was updating login logs {id}. But hasn't been find. Seatch for error on log creation above.")
            return None 
        log.status = status 
        log.outcome = outcome 
        return log