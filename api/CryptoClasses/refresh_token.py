from uuid import uuid4
from hashlib import sha256
from database.refresh_token_repo import RefreshTokenRepo



def generate_refresh_token(user_id, jti):
    token = str(uuid4())
    hashed_token = sha256(token.encode()).hexdigest()
    rt_repo = RefreshTokenRepo()
    rt = rt_repo.create_refresh_token(user_id, jti, hashed_token)
    return token if rt else None
    
    

