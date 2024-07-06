from db_models.db import db 
from db_models.model import RateLimiting
import datetime
from environment import conf
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
        if conf.features.rate_limiting.login_attempts_limit_per_ip <= 0:
            return False
        time_period = datetime.datetime.utcnow() - datetime.timedelta(minutes=conf.features.rate_limiting.login_ban_time) 
        rl = db.session.query(RateLimiting).filter_by(ip=ip, action_type="failed_login").filter(RateLimiting.timestamp > time_period).all()
        if len(rl) >= conf.features.rate_limiting.login_attempts_limit_per_ip:
            return True
        return False
    
    def is_send_verification_email_rate_limited(self, user_id):
        if conf.features.rate_limiting.send_email_attempts_limit_per_user <= 0:
            return False
        time_period = datetime.datetime.utcnow() - datetime.timedelta(minutes=conf.features.rate_limiting.email_ban_time ) 
        rl = db.session.query(RateLimiting).filter_by(user_id=user_id, action_type="send_verification_email").filter(RateLimiting.timestamp > time_period).all()
        if len(rl) >= conf.features.rate_limiting.send_email_attempts_limit_per_user :
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
        max_ban_time = max(conf.features.rate_limiting.login_ban_time, conf.features.rate_limiting.email_ban_time)
        time_period = datetime.datetime.utcnow() - datetime.timedelta(minutes=max_ban_time) 
        db.session.query(RateLimiting).filter(RateLimiting.timestamp < time_period).delete()
        db.session.commit()
        return True