"""Keys model module."""

from . import db

class Keys(db.Model):
    """Define a key model."""
    __tablename__ = 'keys'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    value = db.Column(db.String(1024))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_date = db.Column(db.DateTime(True), nullable=False)
    updated_date = db.Column(db.DateTime(True), nullable=False) 