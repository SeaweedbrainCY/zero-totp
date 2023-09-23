from database.db import db
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    mail = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), nullable=False)
    derivedKeySalt = db.Column(db.String(256), nullable=False)
    isVerified = db.Column(db.Boolean, nullable=False)
    passphraseSalt = db.Column(db.String(256), nullable=False)
    createdAt = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(256), nullable=False, default="user")
    isBlocked =  db.Column(db.Boolean, nullable=False, default=False)
    googleDriveSync = db.Column(db.Boolean, nullable=True)


class ZKE_encryption_key(db.Model):
    __tablename__ = "ZKE_encryption_key"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    ZKE_key = db.Column(db.String(256), nullable=False)

class TOTP_secret(db.Model):
    __tablename__ = "totp_secret_enc"
    uuid = db.Column(db.String(256), primary_key=True, nullable=False, autoincrement=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    secret_enc = db.Column(db.Text, nullable=False);

class Admin(db.Model):
    __tablename__ = "admin_tokens"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    token_hashed = db.Column(db.Text, nullable=False)
    token_expiration = db.Column(db.String(256), nullable=True, default=None)


class Oauth_tokens(db.Model):
    __tablename__ = "oauth_tokens"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    enc_credentials = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)