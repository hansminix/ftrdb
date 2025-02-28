from .extensions import db
import sqlalchemy as sqldb
from flask_admin.contrib.sqla import ModelView
from .config import Config
from sqlalchemy.sql import func
from wtforms.validators import Email, Regexp, DataRequired
#from wtforms_alchemy import Unique
from wtforms import SelectField, StringField
from datetime import datetime
from .config import Config
import itertools

class owner(db.Model):
    __table_name__ = 'owner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255),nullable=False)
    emailaddress = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return self.name 

class environment(db.Model): 
    __table_name__ = 'environment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return self.name

class firewall(db.Model):
    __table_name__ = 'firewall'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)  # Relatie naar owner
    description = db.Column(db.Text, nullable=True)
    owner = db.relationship('owner', backref=db.backref('firewalls', lazy=True))  # Relatie naar Owner

    def __repr__(self):
        return self.name

class datapath(db.Model):
    __table_name__ = 'datapath'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)  # Relatie naar environment
    destination_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)  # Relatie naar environment
    source = db.relationship('environment', foreign_keys=[source_id], backref=db.backref('source_datapaths', lazy=True))
    destination = db.relationship('environment', foreign_keys=[destination_id], backref=db.backref('destination_datapaths', lazy=True))
    name = db.Column(db.String(100))
    
    def __repr__(self):
        return f"{self.name}"

class datapath_firewall(db.Model):
    __table_name__ = 'datapath_firewall'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datapath_id = db.Column(db.Integer, db.ForeignKey('datapath.id'), nullable=False)  # Relatie naar datapath
    firewall_id = db.Column(db.Integer, db.ForeignKey('firewall.id'), nullable=False)  # Relatie naar firewall
    datapath = db.relationship('datapath', backref=db.backref('datapath_firewalls', lazy=True))
    firewall = db.relationship('firewall', backref=db.backref('datapath_firewalls', lazy=True))

class ownerview(ModelView):
    can_export = True
    form_columns = ['name', 'emailaddress','description']
    column_labels = dict(name='Naam',emailaddress='Mailadres',description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam' },
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
    can_export = True
    form_columns = ['name','source','destination']
    column_labels = dict(source='Bronomgeving',destination='Doelomgeving')
    column_filters = ('name',)
    form_args = {
        'source' : { 'label': 'Bronomgeving'},
        'destination' : { 'label': 'Doelomgeving'},
        }
    form_extra_fields = {
        'name': StringField('Naam')
    }
    form_widget_args = {
        'name':{
            'readonly':True
        }
    }
    
    def on_model_change(self, form, model, is_created):
        model.name = f"{form.data.get('source', None)} - to - {form.data.get('destination', None)}"

class datapath_firewallview(ModelView):
    can_export = True
    form_columns = ['datapath','firewall']
    column_labels = dict(datapath='Datapad',firewall='Firewall')
    column_filters = ('datapath',)
    form_args = {
        'datapath' : { 'label': 'Datapad'},
        'firewall' : { 'label': 'Firewall'},
        }

class environmentview(ModelView):
    can_export = True
    form_columns = ['name', 'description']
    column_labels = dict(name='Netwerk omgeving',description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam', 'validators': [Regexp('^[0-9a-zA-Z_]+$',message='Alleen letters, cijfers en _ toegestaan')]},
        'description': { 'label': 'Omschrijving'}
        }
