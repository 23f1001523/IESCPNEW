from enum import unique
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

from sqlalchemy.sql.base import _DefaultDescriptionTuple
from werkzeug.wrappers import request

#from controllers.sponsor import adrequest
# from flask_SQLAlchemy import SQLAlchemy
db = SQLAlchemy()


class Admin(db.Model):
  __tablename__ = "admin"
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  admin_id = db.Column(db.String(200), nullable=False, unique=True)
  admin_name = db.Column(db.String(200), nullable=False)
  admin_password = db.Column(db.String(50), nullable=False)

  def __init__(self, admin_name, admin_id, admin_password):
    self.admin_name = admin_name
    self.admin_id = admin_id
    self.admin_password = admin_password


class Sponsor(db.Model):
  __tablename__ = "sponsors"
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  sponsor_id = db.Column(db.String(200), nullable=False, unique=True)
  sponsor_name = db.Column(db.String(300), nullable=False)
  sponsor_password = db.Column(db.String(50), nullable=False)
  industry = db.Column(db.String(200), nullable=False)
  budget = db.Column(db.Float, nullable=False)
  status = db.Column(db.String(200), nullable=False)
  campaigns = db.relationship("Campaign", backref="sponsor", lazy=True)
  create_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

  def __init__(self, sponsor_id, sponsor_name, sponsor_password, industry,
               budget, status):
    self.sponsor_id = sponsor_id
    self.sponsor_name = sponsor_name
    self.sponsor_password = sponsor_password
    self.industry = industry
    self.budget = budget
    self.status = status


class Influencer(db.Model):
  __tablename__ = "influencers"
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  influencer_id = db.Column(db.String(200), nullable=False, unique=True)
  influencer_name = db.Column(db.String(200), nullable=False)
  influencer_password = db.Column(db.String(50), nullable=False)
  category = db.Column(db.String(200), nullable=False)
  niche = db.Column(db.String(200), nullable=False)
  reach = db.Column(db.Float, nullable=False)
  status = db.Column(db.String(200), nullable=False)
  create_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
  adrequest = db.relationship("AdRequest", backref="influencer", lazy=True)
  negotiations = db.relationship('Negotiation',
                                 backref='incluencer',
                                 lazy=True)

  def __init__(self, influencer_id, influencer_name, influencer_password,
               category, niche, reach, status):
    self.influencer_id = influencer_id
    self.influencer_name = influencer_name
    self.influencer_password = influencer_password
    self.category = category
    self.niche = niche
    self.reach = reach
    self.status = status


class Campaign(db.Model):
  __tablename__ = 'campaigns'
  campaign_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  name = db.Column(db.String(200), nullable=False)
  description = db.Column(db.String(500), nullable=False)
  start_date = db.Column(db.String(200), nullable=False)
  end_date = db.Column(db.String(200), nullable=False)
  budget = db.Column(db.Float, nullable=False)
  visibility = db.Column(db.String(200), nullable=False)
  goals = db.Column(db.String(200), nullable=False)
  status = db.Column(db.String(200), nullable=False)  #active or inactive
  sponsor_id = db.Column(db.String(200),
                         db.ForeignKey("sponsors.sponsor_id"),
                         nullable=False)
  adrequests = db.relationship("AdRequest", backref="campaign", lazy=True)
  create_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
  expiry = db.Column(db.String(100), nullable=False)  # campaign expiry date

  def __init__(self,
               name,
               description,
               start_date,
               end_date,
               budget,
               visibility,
               goals,
               status,
               sponsor_id,
               expiry=expiry):
    self.name = name
    self.description = description
    self.start_date = start_date
    self.end_date = end_date
    self.budget = budget
    self.visibility = visibility
    self.goals = goals
    self.status = status
    self.sponsor_id = sponsor_id
    self.expiry = expiry


class AdRequest(db.Model):
  __tablename__ = 'adrequests'
  adrequest_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  message = db.Column(db.String(500), nullable=False)
  requirements = db.Column(db.String(500), nullable=False)
  payment_amount = db.Column(db.Float, nullable=False)
  status = db.Column(db.String(200),
                     nullable=False)  #PENDING/ACCEPTED/REJECTED
  flag_status = db.Column(db.String(50), nullable=False)  #active or inactive
  campaign_id = db.Column(db.String(200),
                          db.ForeignKey("campaigns.campaign_id"),
                          nullable=False)
  influencer_id = db.Column(db.String(200),
                            db.ForeignKey("influencers.influencer_id"))
  create_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

  negotiations = db.relationship('Negotiation', backref='adrequest', lazy=True)

  def __init__(self, message, requirements, payment_amount, status,
               flag_status, campaign_id, influencer_id):
    self.message = message
    self.requirements = requirements
    self.payment_amount = payment_amount
    self.status = status
    self.flag_status = flag_status
    self.campaign_id = campaign_id
    self.influencer_id = influencer_id


class Negotiation(db.Model):
  __tablename__ = 'negotiations'
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  negotiation = db.Column(db.String(400))  # negotiation by influencer
  adrequest_id = db.Column(db.Integer,
                           db.ForeignKey('adrequests.adrequest_id'),
                           nullable=False)
  influencer_id = db.Column(db.Integer,
                            db.ForeignKey('influencers.influencer_id'),
                            nullable=False)

  def __init__(self, negotiation, influencer_id, adrequest_id):
    self.negotiation = negotiation
    self.influencer_id = influencer_id
    self.adrequest_id = adrequest_id
