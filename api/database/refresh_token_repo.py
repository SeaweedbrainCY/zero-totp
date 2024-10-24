from database.db import db 
from zero_totp_db_model.model import RefreshToken
import datetime
from environment import conf
from uuid import uuid4


class RefreshTokenRepo:

    def create_refresh_token(self, user_id, jti, hashed_token):
        expiration_timestamp = datetime.datetime.utcnow() + datetime.timedelta(seconds=conf.api.refresh_token_valid)
        id = str(uuid4())
        rt = RefreshToken(id=id, user_id=user_id, jti=jti, hashed_token=hashed_token, expiration=expiration_timestamp)
        db.session.add(rt)
        db.session.commit()
        return rt