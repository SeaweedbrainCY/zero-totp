from database.db import db 
from zero_totp_db_model.model import RefreshToken
from zero_totp_db_model.model import Session
import datetime
from environment import conf
from uuid import uuid4


class RefreshTokenRepo:

    def create_refresh_token(self, user_id, session_id, hashed_token, session:Session, expiration=-1) -> RefreshToken:
        expiration_timestamp = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=conf.api.refresh_token_validity)).timestamp() if expiration == -1 else expiration
        id = str(uuid4()) 
        rt = RefreshToken(
            id=id, 
            user_id=user_id, 
            session_token_id=session_id, 
            hashed_token=hashed_token, 
            expiration=expiration_timestamp,
            session=session
            )
        db.session.add(rt)
        db.session.commit()
        return rt
    

    def get_refresh_token_by_hash(self, hashed_token):
        return RefreshToken.query.filter_by(hashed_token=hashed_token).first()
    
    def get_refresh_token_by_id(self, id):
        return RefreshToken.query.filter_by(id=id).first()

    def get_refresh_token_by_session_id(self, session_id):
        return RefreshToken.query.filter_by(session_token_id=session_id).first()
    
    def revoke(self, id):
        rt = RefreshToken.query.filter_by(id=id).first()
        rt.revoke_timestamp = datetime.datetime.now(datetime.UTC).timestamp()
        db.session.commit()
        return rt

    def delete_by_user_id(self, user_id):
        RefreshToken.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True