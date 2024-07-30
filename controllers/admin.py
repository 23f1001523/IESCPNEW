from flask import Flask, render_template, request, url_for, flash, session, jsonify

from werkzeug.utils import redirect
from application.config import LocalDevelopmentConfig

import json
from flask import current_app as app

from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest
from controllers.usermanager import userlogin, login_required, userlogout

fatalerror="Error Occured. Please contact Administrator"
# ADMIN REGISTER
@app.route('/admin/register', methods=['GET', 'POST'])
def adminregister():
  if request.method == 'POST':
    try:
      admin_id = request.form['admin_id']
      admin_name = request.form['admin_name']
      admin_password = request.form['admin_password']
      admin_register = Admin(admin_name=admin_name,
                             admin_id=admin_id,
                             admin_password=admin_password)
      db.session.add(admin_register)
      db.session.commit()
      return render_template('login.html')
    except:
      flash(fatalerror)
  return render_template('register.html')


# ADMIN LOGIN
@app.route('/admin/login', methods=['GET', 'POST'])
def checkAdminLogin():
  if request.method == 'POST':
    try:
      admin_id = request.form.get('admin_id')
      password = request.form.get('admin_password')
      if admin_id == '' or password == '':
        flash("Please enter all the fields")
        return render_template('login.html')
      admin = Admin.query.filter_by(admin_id=admin_id).first()
      if admin:
        if admin.admin_password == password:
          userlogin(admin, 'admin')
          return redirect(url_for('admindashboard'))
        else:
          flash("Password is wrong")
          return render_template('login.html')
      else:
        flash("User ID not registered")
        return render_template('login.html')
    except:
      flash(fatalerror)
  return render_template("login.html")


# ADMIN DASHBOARD
@app.route('/admin/dashboard')
@login_required
def admindashboard():
  try:
    user_id = session['user_id']
    return render_template('/admin/admin_dashboard.html', user_id=user_id)
  except:
    flash(fatalerror)


# ADMIN PROFILE LINK ON ADMIN DASHBOARD
@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
  try:
    admin_id = session["user_id"]
    if request.method == 'POST':
      new_password = request.form.get('new_password')
      confirm_new_password = request.form.get('confirm_new_password')
      admin_password = request.form.get('admin_password')
  
      admin = Admin.query.filter_by(admin_id=admin_id).first()
      if admin:
        if admin.admin_password == admin_password:
          if new_password == confirm_new_password:
            admin.admin_password = new_password
            db.session.commit()
            flash("Password Successfully Updated")
            return render_template('admin/admin_profile.html', admin_id=admin_id)
          else:
            flash("Your Passwords do not match")
            return render_template('admin/admin_profile.html', admin_id=admin_id)
        else:
          flash(
              "The Password entered is Incorrect. You are not allowed to change password"
          )
          return render_template('admin/admin_profile.html', admin_id=admin_id)
      else:
        flash("User ID not registered")
        return render_template('admin/admin_profile.html', admin_id=admin_id)
  except:
    flash(fatalerror)
  return render_template('/admin/admin_profile.html', admin_id=admin_id)


# ADMIN INFO LINK ON ADMIN DASHBOARD
@app.route('/admin/info')
@login_required
def admin_info():
  try:
    admin_id = session["user_id"]
    sponsors = Sponsor.query.order_by(Sponsor.sponsor_id).all()
    influencers = Influencer.query.order_by(Influencer.influencer_id).all()
    campaigns = Campaign.query.order_by(Campaign.campaign_id).all()
    adrequests = AdRequest.query.order_by(AdRequest.campaign_id).all()
    return render_template('/admin/admin_info.html',
                          admin_id=admin_id,
                          sponsors=sponsors,
                          influencers=influencers,
                          campaigns=campaigns,
                          adrequests=adrequests)
  except:
    flash(fatalerror)


# FLAG SPONSOR BUTTON ON SPONSOR TABLE ON ADMIN INFO LINK
@app.route('/admin/sponsor/flag/<id>')
@login_required
def flagsponsor(id):
  try:
    sponsor = Sponsor.query.filter_by(sponsor_id=id).first()
    if sponsor.status == 'ACTIVE':
      sponsor.status = 'INACTIVE'
      db.session.commit()
      flash("Status Updated successfully for " +id)
    else:
      sponsor.status = 'ACTIVE'
      db.session.commit()
      flash("Status Updated successfully for " +id)
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


#FLAG INFLUENCER BUTTON ON INFLUENCER TABLE ON ADMIN INFO LINK
@app.route('/admin/influencer/flag/<id>')
@login_required
def flaginfluencer(id):
  try:
    influencer = Influencer.query.filter_by(influencer_id=id).first()
    if influencer.status == 'ACTIVE':
      influencer.status = 'INACTIVE'
      db.session.commit()
      flash("Status Updated successfully for " +id)
    else:
      influencer.status = 'ACTIVE'
      db.session.commit()
      flash("Status Updated successfully for " +id)
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


#FLAG CAMPAIGN BUTTON ON CAMPAIGN TABLE ON ADMIN INFO LINK
@app.route('/admin/campaign/flag/<id>')
@login_required
def flagcampaign(id):
  try:
    campaign = Campaign.query.filter_by(campaign_id=id).first()
    if campaign.status == 'ACTIVE':
      campaign.status = 'INACTIVE'
      db.session.commit()
      flash("Status Updated successfully for " +campaign.name)
    elif campaign.status == 'INACTIVE':
      campaign.status = 'ACTIVE'
      db.session.commit()
      flash("Status Updated successfully for " +campaign.name)
    else:
      flash("Campaign already Deleted.")
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


# #FLAG ADREQUEST BUTTON ON ADREQUEST TABLE ON ADMIN INFO LINK
@app.route('/admin/adrequest/flag/<id>')
@login_required
def flagadrequest(id):
  try:
    adrequest = AdRequest.query.filter_by(adrequest_id=id).first()
    if adrequest.flag_status == 'ACTIVE' and adrequest.status=="PENDING":
      adrequest.flag_status = 'INACTIVE'
      db.session.commit()
      flash("Status Updated successfully for AdRequest" + str(adrequest.adrequest_id))
    elif adrequest.flag_status == 'INACTIVE' and adrequest.status=="PENDING":
      adrequest.flag_status = 'ACTIVE'
      db.session.commit()
      flash("Status Updated successfully for AdRequest" + str(adrequest.adrequest_id))
    else:
      flash("Status cannot be changed.")
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


#ADMIN FIND LINK ON DASHBOARD
@app.route('/admin/find')
@login_required
def admin_find():
  try:
    admin_id = session["user_id"]
    return render_template('/admin/admin_find.html', admin_id=admin_id)
  except:
    flash(fatalerror)

#SPONSOR SEARCH CARD ON ADMIN FIND
@app.route("/admin/sponsor/search", methods=['GET', 'POST'])
@login_required
def sponsor_search():
  if request.method == 'POST':
    try:
      sponsor_search_type = request.form.get('sponsor_search_type')
      sponsor_search = request.form.get('sponsor_search')

      if sponsor_search_type == 'name':
        sponsors = Sponsor.query.filter(
            Sponsor.sponsor_name.like("%" + sponsor_search + "%")).all()
        if sponsors:
          return render_template('/admin/admin_find.html', sponsors=sponsors)
        else:
          flash('No Sponsors Found')
      elif sponsor_search_type == 'industry':
        sponsors = Sponsor.query.filter(
            Sponsor.industry.like("%" + sponsor_search + "%")).all()
        if sponsors:
          return render_template('/admin/admin_find.html', sponsors=sponsors)
        else:
          flash('No Sponsors Found')
      elif sponsor_search_type == 'budget':
        sponsors = Sponsor.query.filter(Sponsor.budget>=sponsor_search).all()
        if sponsors:
          return render_template('/admin/admin_find.html', sponsors=sponsors)
        else:
          flash('No Sponsors Found')
      elif sponsor_search_type == 'status':
        sponsors = Sponsor.query.filter(status=(sponsor_search).upper()).all()
        if sponsors:
          return render_template('/admin/admin_find.html', sponsors=sponsors)
        else:
          flash('No Sponsors Found')
    except:
      flash(fatalerror)
  return render_template('/admin/admin_find.html')


#INFLUENCER SEARCH CARD ON ADMIN FIND
@app.route("/admin/influencer/search", methods=['GET', 'POST'])
@login_required
def influencer_search():
  if request.method == 'POST':
    try:
      influencer_search_type = request.form.get('influencer_search_type')
      influencer_search = request.form.get('influencer_search')

      if influencer_search_type == 'name':
        influencers = Influencer.query.filter(
          Influencer.influencer_name.like("%" + influencer_search + "%")).all()
        if influencers:
          return render_template('/admin/admin_find.html',
                                influencers=influencers)
        else:
          flash('No influencers found')
      elif influencer_search_type == 'category':
        influencers = Influencer.query.filter(
          Influencer.category.like("%" + influencer_search + "%")).all()
        if influencers:
          return render_template('/admin/admin_find.html',
                                influencers=influencers)
        else:
          flash('No influencers found')
      elif influencer_search_type == 'niche':
        influencers = Influencer.query.filter(
          Influencer.niche.like("%" + influencer_search + "%")).all()
        if influencers:
          return render_template('/admin/admin_find.html',
                                influencers=influencers)
        else:
          flash('No influencers found')
      elif influencer_search_type == 'reach':
        influencers = Influencer.query.filter(Influencer.reach>=influencer_search ).all()
        if influencers:
          return render_template('/admin/admin_find.html',
                                influencers=influencers)
        else:
          flash('No influencers found')
      elif influencer_search_type == 'status':
        influencers = Influencer.query.filter_by(status=influencer_search.upper()).all()
        if influencers:
          return render_template('/admin/admin_find.html',
                                influencers=influencers)
        else:
          flash('No influencers found')
    except:
      flash(fatalerror)
  return render_template('/admin/admin_find.html')





#CAMPAIGN SEARCH CARD ON ADMIN FIND LINK
@app.route("/admin/campaign/search", methods=['GET', 'POST'])
@login_required
def campaign_search():
  if request.method == 'POST':
    try:
      campaign_search_type = request.form.get('campaign_search_type')
      campaign_search = request.form.get('campaign_search')

      if campaign_search_type == 'name':
        campaigns = Campaign.query.filter(
          Campaign.name.like("%" + campaign_search + "%")).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
      elif campaign_search_type == 'budget':
        campaigns = Campaign.query.filter(Campaign.budget>=campaign_search).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
      elif campaign_search_type == 'visibility':
        campaigns = Campaign.query.filter(
          Campaign.visibility.like("%" + campaign_search + "%")).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
      elif campaign_search_type == 'start_date':
        campaigns = Campaign.query.filter_by(start_date= campaign_search ).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
      elif campaign_search_type == 'end_date':
        campaigns = Campaign.query.filter_by(end_date= campaign_search ).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
      elif campaign_search_type == 'description':
        campaigns = Campaign.query.filter(
          Campaign.description.like("%" + campaign_search + "%")).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
      elif campaign_search_type == 'status':
        campaigns = Campaign.query.filter_by(status=(campaign_search).upper()).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
      elif campaign_search_type == 'expiry':
        campaigns = Campaign.query.filter_by(expiry=(campaign_search).upper()).all()
        if campaigns:
          return render_template('/admin/admin_find.html', campaigns=campaigns)
        else:
          flash('No campaigns found')
    except:
      flash(fatalerror)
  return render_template('/admin/admin_find.html')


#ADREQUEST SEARCH CARD ON ADMIN FIND LINK
@app.route("/admin/adrequest/search", methods=['GET', 'POST'])
@login_required
def adrequest_search():
  if request.method == 'POST':
    try:
      adrequest_search_type = request.form.get('adrequest_search_type')
      adrequest_search = request.form.get('adrequest_search')

      if adrequest_search_type == 'payment_amount':
        adrequests = AdRequest.query.filter(
            AdRequest.payment_amount>=adrequest_search).all()
        if adrequests:
          return render_template('/admin/admin_find.html', adrequests=adrequests)
        else:
          flash('No adrequests found')
      elif adrequest_search_type == 'message':
        adrequests = AdRequest.query.filter(
            AdRequest.message.like("%" + adrequest_search + "%")).all()
        if adrequests:
          return render_template('/admin/admin_find.html', adrequests=adrequests)
        else:
          flash('No adrequests found')
      elif adrequest_search_type == 'requirements':
        adrequests = AdRequest.query.filter(
            AdRequest.requirements.like("%" + adrequest_search + "%")).all()
        if adrequests:
          return render_template('/admin/admin_find.html', adrequests=adrequests)
        else:
          flash('No adrequests found')
      elif adrequest_search_type == 'requirements':
        adrequests = AdRequest.query.filter(
            AdRequest.requirements.like("%" + adrequest_search + "%")).all()
        if adrequests:
          return render_template('/admin/admin_find.html', adrequests=adrequests)
        else:
          flash('No adrequests found')
      elif adrequest_search_type == 'status':
        adrequests = AdRequest.query.filter_by(status=(adrequest_search).upper()).all()
        if adrequests:
          return render_template('/admin/admin_find.html', adrequests=adrequests)
        else:
          flash('No AdRequest found')
      elif adrequest_search_type == 'flaggedstatus':
        adrequests = AdRequest.query.filter_by(flag_status=(adrequest_search).upper()).all()
        if adrequests:
          return render_template('/admin/admin_find.html', adrequests=adrequests)
        else:
          flash('No AdRequest found')
    except:
      flash(fatalerror)
  return render_template('/admin/admin_find.html')


#ADMIN STATS LINK ON DASHBOARD
@app.route('/admin/show/stats')
@login_required
def show_stats():
  try:
    return render_template('/admin/admin_chart.html')
  except:
    flash(fatalerror)




# ADMIN STATS NO OF USERS(CHART ONE)
@app.route('/admin/fetchChart')
@login_required
def fetchChart():
  try:
    noOfSponsors = Sponsor.query.count()
    noOfInfluencers = Influencer.query.count()
    data_labels = {'users': "Sponsors", "value": noOfSponsors}
    data_values = {"users": "Influencers", "value": noOfInfluencers}
    data = []
    data.append(data_labels)
    data.append(data_values)
    return data
  except:
    flash(fatalerror)


#ADMIN STATS SPONSORS ON THE BASIS OF BUDGET(SECOND CHART)
@app.route('/admin/stats')
@login_required
def admin_stats():
  try:
    admin_id = session["user_id"]
    sponsors = Sponsor.query.all()
    data = []
    for sponsor in sponsors:
      data.append({'users': sponsor.sponsor_name, 'value': sponsor.budget})
    data.sort(key=lambda x: x['value'], reverse=True)

    return data
  except:
    flash(fatalerror)  