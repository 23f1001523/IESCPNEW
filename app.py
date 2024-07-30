from flask import Flask, render_template, request, url_for

from sqlalchemy.sql.sqltypes import DATETIME
from werkzeug.utils import redirect
from datetime import datetime
from application.config import LocalDevelopmentConfig

from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest
from controllers.usermanager import userlogout

app = None
# migrate=Migrate()


def createApp():
  app = Flask(__name__, template_folder='templates')
  app.config.from_object(LocalDevelopmentConfig)
  app.app_context().push()
  db.init_app(app)
  db.create_all()
  admin = Admin.query.filter_by(admin_id="admin").first()
  if not admin:
    admin = Admin(admin_id="admin", admin_name="admin", admin_password="admin")
    db.session.add(admin)
    db.session.commit()
  intialiseApp()
 
  return app


def isValid(enddate):
  enddate = enddate.split("-")
  newdate = datetime(int(enddate[0]), int(enddate[1]), int(enddate[2]))
  if datetime.now() > newdate:
    return True
  return False


def intialiseApp():
  campaigns = Campaign.query.all()
  if campaigns:
    for campaign in campaigns:
      if (isValid(campaign.end_date)):
        campaign.validity = "EXPIRED"
        db.session.commit()
      else:
        campaign.validity = "UNEXPIRED"
        db.session.commit()


app = createApp()


@app.route('/base_dashboard')
def index():
  return render_template('base_dashboard.html')


@app.route('/')
def home():
  return render_template('index.html')

  # return render_template('users.html', admins=admins)


@app.route('/register', methods=['GET', 'POST'])
def register():
  return render_template('register.html')


@app.route('/about', methods=['GET', 'POST'])
def about():
  return render_template('about.html')


@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
  return render_template('contactus.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
  userlogout()
  return render_template('login.html')


from controllers.admin import *
from controllers.sponsor import *
from controllers.influencer import *

if __name__ == '__main__':
  app.run('0.0.0.0', debug=True)
