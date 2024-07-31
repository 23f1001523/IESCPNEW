from datetime import datetime
from flask import Flask, render_template, request, url_for, session, flash, json
from werkzeug.utils import redirect

from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest, Negotiation
from flask import current_app as app
from controllers.usermanager import isActive, login_required_influencer, userlogin
from functools import wraps

fatalerror = "Error Occured. Please contact Administrator"


#INFLUENCER REGISTER
@app.route('/influencer/register', methods=['GET', 'POST'])
def influencers():
  if request.method == 'POST':
    try:
      influencer_name = request.form['influencer_name']
      influencer_id = request.form['influencer_id']
      influencer_password = request.form['influencer_password']
      category = request.form['category']
      niche = request.form['niche']
      reach = request.form['reach']
      status = 'ACTIVE'
      influencer = Influencer.query.filter_by(
          influencer_id=influencer_id).first()
      if influencer:
        flash('Influencer already registered')
      else:
        new_influencer = Influencer(influencer_name=influencer_name,
                                    influencer_id=influencer_id,
                                    influencer_password=influencer_password,
                                    category=category,
                                    niche=niche,
                                    reach=reach,
                                    status=status)
        db.session.add(new_influencer)
        db.session.commit()
        flash("Successfully Registerd as Influencer.Please Login now.")
        return render_template('login.html')
    except:
      flash(fatalerror)
  return render_template('register.html')


#INFLUENCER LOGIN
@app.route('/influencer/login', methods=['GET', 'POST'])
def influencer_login():
  if request.method == 'POST':
    try:
      influencer_id = request.form.get('influencer_id')
      influencer_password = request.form.get('influencer_password')
      if influencer_id == '' or influencer_password == '':
        flash("Please enter all the fields")
        return render_template('login.html')
      influencer = Influencer.query.filter_by(
          influencer_id=influencer_id).first()
      if influencer:
        if influencer.influencer_password == influencer_password:
          userlogin(influencer, "influencer")
          return redirect(url_for('influencerdashboard'))
        else:
          flash("Password is wrong")
      else:
        flash("User ID not registered")
    except:
      flash(fatalerror)
  return render_template('login.html')


#INFLUENCER DASHBOARD AND NOTIFICATIONS ON SIDEBAR
@app.route('/influencer/dashboard')
@login_required_influencer
def influencerdashboard():
  try:
    if isActive():
      influencer_id = session['user_id']
      campaigns = Campaign.query.filter_by(visibility='Public',
                                          status="ACTIVE").all()
      alladrequests = AdRequest.query.filter_by(
          influencer_id=influencer_id).all()
      myadrqeuests = AdRequest.query.filter(
          AdRequest.influencer_id == influencer_id, AdRequest.status
          != "PENDING").all()
      campaigns = Campaign.query.filter_by(visibility='Public',
                                          status="ACTIVE").all()
      pvtNotifications = len([
          adrequest for adrequest in alladrequests
          if adrequest.campaign.visibility == "Private"
      ])
      allPublic = len(campaigns)
      allAdrequests = len(myadrqeuests)
      session['pvtNotifications'] = pvtNotifications
      session['allPublic'] = allPublic
      session['allAdrequests'] = allAdrequests
      return render_template('/influencer/influencer_dashboard_display.html',
                            adrequests=alladrequests)
    else:
      return render_template('error.html')
  except:
    flash(fatalerror)


#INFLUENCER ADREQUEST NEGOTIATION FOR PRIVATE REQUESTS ON SIDEBAR AND DASHBOARD(IN NOTIFICATIONS)
@app.route('/influencer/adrequest/negotiation/<adrequest_id>', methods=['GET', 'POST'])
@login_required_influencer
def negotiation(adrequest_id):
  if request.method == 'POST':
    # try:
    influencer_id=session['user_id']
    negotiation = request.form.get('negotiation')
    # adrequest = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    negotiations=Negotiation.query.filter_by(influencer_id=influencer_id,adrequest_id=adrequest_id).first()
    if negotiations:
      negotiations.negotiation=negotiation
      db.session.commit()
      flash("Successfully updated")
      return redirect(url_for('influencerdashboard'))
    else:
      newNegotiation=Negotiation(influencer_id=influencer_id,adrequest_id=adrequest_id,negotiation=negotiation) 
      db.session.add(newNegotiation)
      db.session.commit()
      flash("Successfully updated")
      return redirect(url_for('influencerdashboard'))
    # except:
      # flash(fatalerror)
  return redirect(url_for('influencerdashboard'))


# #PUBLIC ADREQUEST FIND BY CAMPAIGN NAME ON INFLUENCER FIND
# @app.route('/influencer/show/<id>', methods=['GET', 'POST'])
# @login_required_influencer
# def show(id):
  if request.method == 'POST':
    try:
      negotiation = request.form.get('negotiation')
      influencer_id = session['user_id']
      adrequest_id = id
      negotiations = Negotiation.query.filter_by(
          influencer_id=influencer_id, adrequest_id=adrequest_id).first()
      if negotiations:
        negotiations.negotiation = negotiation
        db.session.commit()
        flash('Successfully updated')
        return redirect(url_for('public_adrequests_status'))
      else:

        negotiations = Negotiation(negotiation=negotiation,
                                  influencer_id=influencer_id,
                                  adrequest_id=adrequest_id)

        db.session.add(negotiations)
        db.session.commit()
        flash("successfully entered in database")
    except:
      flash(fatalerror)
  return redirect(url_for('influencerdashboard'))




#INFLUENCER PRIVATE ADREQUEST ACCEPT OPTION ON SIDEBAR OF INFLUENCER DASHBOARD(IN NOTIFICATIONS)
@app.route('/influencer/pvtadrequest/accept/<int:id>')
@login_required_influencer
def acceptPvtAdrequest(id):
  try:
    influencer_id = session['user_id']
    adrequest = AdRequest.query.filter_by(adrequest_id=id).first()
    if adrequest.influencer_id == influencer_id:
      adrequest.status = 'ACCEPTED'
      db.session.commit()
      flash("Adrequest Accepted")
      return redirect(url_for('influencerdashboard'))
  except:
    flash(fatalerror)


#INFLUENCER PRIVATE ADREQUEST REJECT OPTION ON SIDEBAR OF INFLUENCER DASHBOARD(IN NOTIFICATIONS)
@app.route('/influencer/pvtadrequest/reject/<int:id>')
@login_required_influencer
def rejectPvtAdrequest(id):
  try:
    influencer_id = session['user_id']
    adrequest = AdRequest.query.filter_by(adrequest_id=id).first()
    if adrequest.influencer_id == influencer_id:
      adrequest.status = 'REJECTED'
      db.session.commit()
      flash("Adrequest Rejected")
      return redirect(url_for('influencerdashboard'))
  except:
    flash(fatalerror)



#INFLUENCER PUBLIC ADREQUEST LINK ON INFLUENCER DASHBOARD(SIDEBAR)
@app.route('/influencer/public/adrequests/show')
@login_required_influencer
def public_adrequests_show():
  try:
    influencer_id = session['user_id']
    # adrequests = AdRequest.query.filter_by(influencer_id=influencer_id).all()
    campaigns = Campaign.query.filter_by(visibility='Public',
                                        status="ACTIVE").all()

    return render_template('/influencer/public_adrequests.html',
                          campaigns=campaigns)
  except:
    flash(fatalerror)


#INFLUENCER MY ADREQUESTS(ACCEPTED ADREQUESTS) SHOW LINK ON INFLUENCER DASHBOARD(SIDEBAR)
@app.route('/influencer/adrequests/accepted/show')
@login_required_influencer
def accepted_adrequests_show():
  try:
    influencer_id = session['user_id']

    myadrqeuests = AdRequest.query.filter(
        AdRequest.influencer_id == influencer_id, AdRequest.status
        != "PENDING").all()
    negotiations=Negotiation.query.filter_by(influencer_id=influencer_id)
    return render_template('/influencer/influencer_adrequest_status.html',
                          adrequests=myadrqeuests,negotiations=negotiations)
  except:
    flash(fatalerror)




#INFLUENCER PROFILE LINK ON INFLUENCER DASHBOARD ALLOWED TO CHANGE PASSWORD THERE
@app.route('/influencer/profile', methods=['GET', 'POST'])
@login_required_influencer
def influencer_profile():

  user_id = session['user_id']
  if request.method == 'POST':
    try:
      new_password = request.form.get('new_password')
      confirm_new_password = request.form.get('confirm_new_password')
      influencer_id = request.form.get('influencer_id')
      influencer_password = request.form.get('influencer_password')
      influencer = Influencer.query.filter_by(
          influencer_id=influencer_id).first()
      if influencer:
        if influencer.influencer_password == influencer_password:
          if new_password == confirm_new_password:
            influencer.influencer_password = new_password
            db.session.commit()
            flash("Password Successfully Updated")

          else:
            flash("Confirm Passwords do not match")

        else:
          flash("Password entered is incorrect")

      else:
        flash("User ID not registered")

    except:
      flash(fatalerror)
  influencer = Influencer.query.filter_by(influencer_id=user_id).first()
  return render_template('/influencer/influencer_profile.html',
                         influencer=influencer)


#INFLUENCER UPDATE PROFILE ON INFLUENCER PROFILE LINK
@app.route('/influencer/updateProfile', methods=['GET', 'POST'])
@login_required_influencer
def influencer_change_category():
  if request.method == 'POST':
    try:
      category = request.form.get('category')
      niche = request.form.get('niche')
      reach = request.form.get('reach')
      influencer = Influencer.query.filter_by(
          influencer_id=session['user_id']).first()
      if influencer:
        influencer.category = category
        influencer.niche = niche
        influencer.reach = reach
        db.session.commit()
        flash("Profile Update Successfully.")
      else:
        flash("Influencer ID not registered")
      influencer = Influencer.query.filter_by(
          influencer_id=session['user_id']).first()
      return redirect(url_for('influencer_profile'))
    except:
      flash(fatalerror)




#INFLUENCER FIND LINK ON INFLUENCER DASHBOARD
@app.route('/influencer/find')
@login_required_influencer
def influncer_find():
  try:
    return render_template('/influencer/influencer_find.html')
  except:
    flash(fatalerror)



# CAMPAIGN SEARCH OPTION ON INFLUENCER FIND LINK
@app.route("/influencer/campaign/search", methods=['GET', 'POST'])
@login_required_influencer
def influencer_campaign_search():
  if request.method == 'POST':
    try:
      campaign_search_type = request.form.get('campaign_search_type')
      campaign_search = request.form.get('campaign_search')

      if campaign_search_type == 'name':
        campaigns = Campaign.query.filter_by(name=campaign_search,
                                            visibility='Public').all()
        if campaigns:
          flash("search complete")
          return render_template('/influencer/influencer_find.html',
                                campaigns=campaigns)
        else:
          flash("You can not search for a Private Campaign")
          return render_template('/influencer/influencer_find.html')
      elif campaign_search_type == 'budget':
        campaigns = Campaign.query.filter_by(budget=campaign_search,
                                            visibility='Public').all()

        if campaigns:
          flash("search complete")
          return render_template('/influencer/influencer_find.html',
                                campaigns=campaigns)
        else:
          flash("You can not search for a Private Campaign")
          return render_template('/influencer/influencer_find.html')

      elif campaign_search_type == 'start_date':
        campaigns = Campaign.query.filter_by(start_date=campaign_search,
                                            visibility='Public').all()
        if campaigns:
          flash("search complete")
          return render_template('/influencer/influencer_find.html',
                                campaigns=campaigns)
        else:
          flash("You can not search for a Private Campaign")
          return render_template('/influencer/influencer_find.html')

      elif campaign_search_type == 'end_date':
        campaigns = Campaign.query.filter_by(end_date=campaign_search,
                                            visibility='Public').all()
        if campaigns:
          flash("search complete")
          return render_template('/influencer/influencer_find.html',
                                campaigns=campaigns)
        else:
          flash("You can not search for a Private Campaign")
          return render_template('/influencer/influencer_find.html')
    except:
      flash(fatalerror)
  return render_template('/influencer/influencer_find.html')


# ADREQUEST SEARCH OPTION ON INFLUENCER FIND LINK
@app.route("/influencer/adrequest/search", methods=['GET', 'POST'])
@login_required_influencer
def influencer_adrequest_search():

  if request.method == 'POST':
    try:
      adrequest_search_type = request.form.get('adrequest_search_type')
      adrequest_search = request.form.get('adrequest_search')

      if adrequest_search_type == 'payment_amount':

        adds = []
        adrequests = AdRequest.query.filter_by(
            payment_amount=adrequest_search).all()
        for ads in adrequests:
          camp = Campaign.query.filter_by(campaign_id=ads.campaign_id).first()
          if camp.visibility == 'Public':
            adds.append(ads)
        return render_template('/influencer/influencer_find.html',
                              adrequests=adds)
      elif adrequest_search_type == 'message':
        adrequests = AdRequest.query.filter(
            AdRequest.message.like("%" + adrequest_search + "%")).all()
        if adrequests:
          return render_template('/influencer/influencer_find.html',
                                adrequests=adrequests)
        else:
          flash('No adrequests found')
      elif adrequest_search_type == 'requirements':
        adrequests = AdRequest.query.filter(
            AdRequest.requirements.like("%" + adrequest_search + "%")).all()
        if adrequests:
          return render_template('/influencer/influencer_find.html',
                                adrequests=adrequests)
        else:
          flash('No adrequests found')
    except:
      flash(fatalerror)
  return render_template('/influencer/influencer_find.html')


#INFLUENCER STATS LINK ON INFLUENCER DASHBOARD
@app.route('/influencer/stats')
@login_required_influencer
def influencer_stats():
  try:
    return render_template('/influencer/influencer_stats.html')
  except:
    flash(fatalerror)

#INFLUENCER CAMPAIGN PROGRESS CHART ON INFLUENCER STATS LINK
@app.route('/influencer/campaign/progress/chart')
@login_required_influencer
def inluencercampaignprogresschart():
  try:
    campaigns = Campaign.query.all()
    data = []
    for campaign in campaigns:
      dict = {}
      start_date = campaign.start_date.split('-')
      end_date = campaign.end_date.split('-')
      starting_date = datetime(int(start_date[0]), int(start_date[1]),
                              int(start_date[2]))
      ending_date = datetime(int(end_date[0]), int(end_date[1]),
                            int(end_date[2]))
      campaign_duration = (ending_date - starting_date).days

      present_date = datetime.now()
      campaign_progress = (present_date - starting_date).days
      present_date = str(present_date)
      current_date = present_date.split('-')

      if int(current_date[0]) < int(start_date[0]):
        percentage_progress = 0
      elif int(current_date[0]) > int(end_date[0]):
        percentage_progress = campaign_duration
      else:
        percentage_progress = (campaign_progress / campaign_duration) * 100

      dict = {
          "id": campaign.campaign_id,
          "name": campaign.name,
          "progress": percentage_progress
      }
      data.append(dict)
    return data
  except:
    flash(fatalerror)


#INFLUENCER BUDGET PROGRESS CHART ON INFLUENCER STATS LINK
@app.route('/influencer/adrequests/budget/chart')
@login_required_influencer
def campaign_budget_chart():
  try:
    influencer_id = session['user_id']
    adrequests = AdRequest.query.filter_by(influencer_id=influencer_id,
                                          status='ACCEPTED').all()
    data = []
    for adrequest in adrequests:
      dict = {}
      dict = {"name": adrequest.adrequest_id, "budget": adrequest.payment_amount}
      data.append(dict)
    return data
  except:
    flash(fatalerror)





