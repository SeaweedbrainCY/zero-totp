from database.db import db 
from zero_totp_db_model import model
import datetime
from environment import conf
from uuid import uuid4
from environment import logging

class Notifications:

    def get_last_active_notification(self):
        try:
            notif = None
            notifications = db.session.query(model.Notifications).filter_by(enabled=True).order_by(model.Notifications.timestamp.desc()).all()
            for n in notifications:
                if n.expiry:
                    if float(n.expiry) >= datetime.datetime.now(datetime.UTC).timestamp():
                        notif = n
                        break
                else:
                    notif = n
                    break
        except Exception as e:
            logging.error(e)
            return None
        if notif:
            if notif.expiry:
                return notif if float(notif.expiry) >= datetime.datetime.now(datetime.UTC).timestamp() else None
            else :
                return notif
        else:
            return None
            

 
