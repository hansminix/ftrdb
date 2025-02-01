from .extensions import db
import sqlalchemy as sqldb
from flask_admin.contrib.sqla import ModelView
from .config import Config
from sqlalchemy.sql import func
from wtforms.validators import Email, Regexp, DataRequired
from wtforms_alchemy import Unique
from wtforms import SelectField
from datetime import datetime
from .config import Config
import itertools

class owner(db.Model):
    __table_name__ = 'owner'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    emailaddress = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)
    firewall=db.relationship('firewall', back_populates='owner')

    def __repr__(self):
        return self.name 

class environment(db.Model): 
    __table_name__ = 'environment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)
    #source=db.relationship('datapath', back_populates='source')
    #destination=db.relationship('datapath', back_populates='destination')

    def __repr__(self):
        return self.name

class environmentchoices():
    def get_enviroments(self):
        engine = sqldb.create_engine(Config.SQLALCHEMY_DATABASE_URI)
        meta_data = sqldb.MetaData()
        meta_data.reflect(bind=engine)
        sql = sqldb.text("SELECT name from environment order by name")
        with engine.connect() as conn:
            result = conn.execute(sql).fetchall()
        choices = list(itertools.chain(*result))
        return choices

class firewall(db.Model):
    __table_name__ = 'firewall'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)
    owner_id= db.Column(db.Integer,db.ForeignKey(owner.id))
    owner=db.relationship("owner", back_populates="firewall")

    def __repr__(self):
        return self.name

class datapath(db.Model):
    __table_name__ = 'datapath'
    id = db.Column(db.Integer, primary_key=True)
    #source_id=db.Column(db.Integer,db.ForeignKey(environment.id), foreign_keys=[environment.id])
    #source = db.relationship("environment", back_populates="source")
    #destination_id=db.Column(db.Integer,db.ForeignKey(environment.id), foreign_keys=[environment.id])
    #destination = db.relationship("environment", back_populates="destination")
    source = db.Column(db.String(255),nullable=False)
    destination = db.Column(db.String(255),nullable=False)
    firewalls=db.relationship("datapath_firewall", back_populates="datapath")

    def __repr__(self):
        return f"{self.source}_{self.destination}"

class datapath_firewall(db.Model):
    __table_name__ = 'datapath_firewall'
    id = db.Column(db.Integer, primary_key=True)
    datapath_id=db.Column(db.Integer,db.ForeignKey(datapath.id))
    datapath=db.relationship("datapath", back_populates="firewalls")
    firewall_id=db.Column(db.Integer,db.ForeignKey(firewall.id))

class ownerview(ModelView):
    can_export = True
    form_columns = ['name', 'emailaddress','description']
    column_labels = dict(name='Naam',emailaddress='Mailadres',description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam','validators': [Unique(owner.name, message='Naam bestaat al')] },
        'emailaddress': { 'label' : 'Mailadres','validators': [Email(message='Geen geldig mail adres')] },
        'description': { 'label': 'Omschrijving'}
        }

class firewallview(ModelView):
    can_export = True
    form_columns = ['name', 'owner', 'description']
    column_labels = dict(name='Naam',owner='Gemandateerde', description='Omschrijving')
    form_args = {
        'name': { 'label' : 'Naam'},
        'owner': { 'label': 'Gemandateerde'},
        'description': { 'label': 'Omschrijving'}
        }

class datapathview(ModelView):
    ev=environmentchoices()
    env_choices=ev.get_enviroments()
    ev=None
    print(env_choices)
    #env_choices=[]
    can_export = True
    form_columns = ['source','destination','firewalls']
    column_labels = dict(source='Bronomgeving',destination='Doelomgeving',firewalls='Firewalls')
    form_extra_fields = {
        'source': SelectField(
            'Source',
            choices=env_choices
            ),
        'destination': SelectField(
            'Destination',
            choices=env_choices
            )
    }
    form_args = {
        'firewalls': { 'label': 'Firewalls'}
        }

class environmentview(ModelView):
    can_export = True
    form_columns = ['name', 'description']
    column_labels = dict(name='Netwerk omgeving',description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam', 'validators': [Regexp('^[0-9a-zA-Z_]+$',message='Alleen letters, cijfers en _ toegestaan'),Unique(environment.name, message='Netwerkomgeving bestaat al')] },
        'description': { 'label': 'Omschrijving'}
        }
