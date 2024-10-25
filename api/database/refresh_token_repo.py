from database.db import db 
from zero_totp_db_model.model import RefreshToken
import datetime
from environment import conf
from uuid import uuid4


class RefreshTokenRepo:

    def create_refresh_token(self, user_id, jti, hashed_token, expiration=-1):
        expiration_timestamp = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=conf.api.refresh_token_validity)).timestamp()
        id = str(uuid4()) if expiration == -1 else expiration
        rt = RefreshToken(id=id, user_id=user_id, jti=jti, hashed_token=hashed_token, expiration=expiration_timestamp)
        db.session.add(rt)
        db.session.commit()
        return rt
    

    def get_refresh_token_by_hash(self, hashed_token):
        return RefreshToken.query.filter_by(hashed_token=hashed_token).first()
    
    def revoke(self, id):
        rt = RefreshToken.query.filter_by(id=id).first()
        rt.revoke_timestamp = datetime.datetime.now(datetime.UTC).timestamp()
        db.session.commit()
        return rt