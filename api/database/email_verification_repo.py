from database.db import db 
from database.model import EmailVerificationToken as EmailVerificationToken_model

class EmailVerificationToken:


    def get_by_user_id(self, user_id):
        return db.session.query(EmailVerificationToken_model).filter_by(user_id=user_id).first()

    def add(self, user_id, token, expires_at):
        email_verification_token = EmailVerificationToken_model(user_id=user_id, token=token, expires_at=expires_at)
        db.session.add(email_verification_token)
        db.session.commit()
        return email_verification_token

    def delete(self, user_id):
        if db.session.query(EmailVerificationToken_model).filter_by(user_id=user_id).first() != None:
            db.session.query(EmailVerificationToken_model).filter_by(user_id=user_id).delete()
        db.session.commit()
        return True