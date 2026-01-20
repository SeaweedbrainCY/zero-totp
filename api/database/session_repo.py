from database.db import db 
from zero_totp_db_model.model import Session
import datetime as dt
from environment import conf, logging
from uuid import uuid4

class SessionRepo:

    def create_new_session(self, user_id:int, ip_address:str|None, encrypted_user_agent:str|None=None, encrypted_device_name:str|None=None, encrypted_platform:str|None=None) -> Session :
        id = str(uuid4())
        expiration_timestamp = dt.datetime.now(dt.UTC).timestamp() + conf.api.session_validity
        session = Session(
            id=id,
            user_id=user_id,
            encrypted_user_agent=encrypted_user_agent,
            encrypted_device_name=encrypted_device_name,
            encrypted_platform=encrypted_platform,
            ip_address=ip_address,
            created_at=dt.datetime.now(dt.UTC).timestamp(),
            last_active_at=dt.datetime.now(dt.UTC).timestamp(),
            expiration_timestamp=expiration_timestamp
        )
        return session
    
    def update_last_active(self, session_id:str, timestamp:float, ip: str|None) -> bool:
        session = db.session.query(Session).filter(Session.id == session_id).first()
        if session != None:
            session.last_active_at = timestamp
            session.ip_address = ip
            db.session.commit()
            return True
        return False


    def get_session_by_id(self, session_id:str) -> Session|None:
        return db.session.query(Session).filter(Session.id == session_id).first()
    
    def revoke(self, session_id:str) -> bool:
        session = self.get_session_by_id(session_id)
        if session != None:
            session.revoke_timestamp = dt.datetime.now(dt.UTC).timestamp()
            db.session.commit()
            return True
        return False

    def delete_by_user_id(self, user_id:int) -> None:
        sessions = db.session.query(Session).filter(Session.user_id == user_id).all()
        for session in sessions:
            db.session.delete(session)
        db.session.commit()