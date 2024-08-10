from database.db import db 
from zero_totp_db_model.model import Notifications
import datetime
from environment import conf
from uuid import uuid4

class Notification:

    def add_notification(message, enabled=True, expiry=None, authenticated_user_only=False):
        notification = Notifications(id=str(uuid4()), message=message, timestamp=datetime.datetime.now(datetime.UTC).timestamp(),  enabled=enabled, expiry=expiry, authenticated_user_only=authenticated_user_only)
        db.session.add(notification)
        db.session.commit()
        return notification

    def get_last_active_notification():
        notif = db.session.query(Notifications).filter_by(enabled=True).order_by(Notifications.timestamp.desc).first()
        return notif if notif.timestamp >= datetime.datetime.now(datetime.UTC).timestamp() else None
            

 
