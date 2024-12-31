import os
import logging
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    promo_code = db.Column(db.String(50))
    final_amount = db.Column(db.Float)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
