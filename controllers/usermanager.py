from flask import Flask, flash, redirect, url_for, session
from functools import wraps
from models.model import *


def login_required(func):

  @wraps(func)
  def wrapper_admin(*args, **kwargs):
    if session.get('loggedin') is None or session['user_type'] != 'admin':
      flash('You need to login first')
      return redirect(url_for('login'))
    return func(*args, **kwargs)

  return wrapper_admin


def login_required_sponsor(func):

  @wraps(func)
  def wrapper_sponsor(*args, **kwargs):
    if session.get('loggedin') is None or session['user_type'] != 'sponsor':
      flash('You need to login first')
      return redirect(url_for('login'))
    return func(*args, **kwargs)

  return wrapper_sponsor


def login_required_influencer(func):

  @wraps(func)
  def wrapper_influencer(*args, **kwargs):
    if session.get('loggedin') is None or session['user_type'] != 'influencer':
      flash('You need to login first')
      return redirect(url_for('login'))
    return func(*args, **kwargs)

  return wrapper_influencer


def userlogin(user, user_type):
  session['loggedin'] = True
  session['user_type'] = user_type
  if user_type == 'admin':
    session['user_id'] = user.admin_id
    session['user_name'] = user.admin_name
  elif user_type == 'sponsor':
    session['user_id'] = user.sponsor_id
    session['user_name'] = user.sponsor_name
  elif user_type == 'influencer':
    session['user_id'] = user.influencer_id
    session['user_name'] = user.influencer_name


def userlogout():
  session.pop('loggedin', None)
  session.pop('user_id', None)
  session.pop('user_name', None)
  session.pop('user_type', None)
  return redirect(url_for('login'))


def isActive():
  user_id = session['user_id']
  user_type = session['user_type']
  if user_type == 'sponsor':
    sponsor = Sponsor.query.filter_by(sponsor_id=user_id).first()
    if sponsor and sponsor.status == "ACTIVE":
      return True
  elif user_type == "influencer":
    influencer = Influencer.query.filter_by(influencer_id=user_id).first()
    if influencer and influencer.status == "ACTIVE":
      return True
  return False
