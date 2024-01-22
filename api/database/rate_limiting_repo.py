from database.db import db 
from database.model import RateLimiting
import datetime

class RateLimitingRepo:
    def add_failed_login(self, ip, user_id):
        rl = RateLimiting(ip=ip, user_id=user_id, action_type="failed_login", timestamp= datetime.datetime.utcnow())
        db.session.add(rl)
        db.session.commit()
        return rl
    
    def add_send_verification_email(self, ip, user_id):
        rl = RateLimiting(ip=ip, user_id=user_id, action_type="send_verification_email", timestamp= datetime.datetime.utcnow())
        db.session.add(rl)
        db.session.commit()
        return rl
    
    def is_login_rate_limited (self, ip):
        time_period = datetime.datetime.utcnow() - datetime.timedelta(minutes=60) 
        rl = db.session.query(RateLimiting).filter_by(ip=ip, action_type="failed_login").filter(RateLimiting.timestamp > time_period).all()
        if len(rl) >= 10:
            return True
        return False
    
    def is_send_verification_email_rate_limited (self, user_id):
        time_period = datetime.datetime.utcnow() - datetime.timedelta(minutes=60) 
        rl = db.session.query(RateLimiting).filter_by(user_id=user_id, action_type="send_verification_email").filter(RateLimiting.timestamp > time_period).all()
        if len(rl) >= 5:
            return True
        return False
    
    def flush_login_limit(self, ip):
        db.session.query(RateLimiting).filter_by(ip=ip).delete()
        db.session.commit()
        return True
    
    def flush_email_verification_limit(self, user_id):
        db.session.query(RateLimiting).filter_by(user_id=user_id).delete()
        db.session.commit()
        return True
    
    def flush_outdated_limit(self):
        time_period = datetime.datetime.utcnow() - datetime.timedelta(minutes=60) 
        db.session.query(RateLimiting).filter(RateLimiting.timestamp < time_period).delete()
        db.session.commit()
        return True