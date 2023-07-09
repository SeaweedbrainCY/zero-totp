from database.db import db

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    mail = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), nullable=False)
    derivedKeySalt = db.Column(db.String(256), nullable=False)


class ZKE_encryption_key(db.Model):
    __tablename__ = "ZKE_encryption_key"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    ZKE_key = db.Column(db.String(256), nullable=False)


class Storage_Keys(db.Model):
    __tablename__ = "storage_keys"
    uuid = db.Column(db.String(256), primary_key=True, nullable=False)
    storage_key = db.Column(db.String(256), nullable=False)
    expiration = db.Column(db.String(256), nullable=False)