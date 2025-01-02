from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,DateTimeField
from wtforms.validators import DataRequired,Email,EqualTo,Length


class SearchMuseumPlus(FlaskForm):
    objectid = StringField('objectid', validators = [Length(min=0, max=100)])
    inventorynumber = StringField('inventorynumber', validators= [Length(min=0, max=100)])
    title = StringField('title', validators = [Length(min=0, max=100)])
    submit = SubmitField('Search')

class Settings(FlaskForm):
    premis_video_normalization_date = DateTimeField('Your premis_video_normalization_date', format='%Y-%m-%dT%H:%M')    
    premis_video_normalization_agent = StringField('premis_video_normalization_agent', validators= [Length(min=0, max=200)])
    mets_createdate = StringField('mets_createdate', validators= [Length(min=0, max=200)])
    submit = SubmitField('Save')

class LidoSave(FlaskForm):
    lidoRecID = StringField('Lido Record ID', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    actorName = StringField('Actor Name', validators=[DataRequired()])
    eventDate = StringField('Event Date', validators=[DataRequired()])
    recordID = StringField('Record ID', validators=[DataRequired()])
    aineistotyyppi = StringField('Aineistotyyppi', validators=[DataRequired()])
    paaluokka = StringField('Pääluokka', validators=[DataRequired()])
    erikoisluokka = StringField('Erikoisluokka', validators=[DataRequired()])
    inventaarionumero = StringField('Inventaarionumero', validators=[DataRequired()])
    submit = SubmitField('Generate Lido-XML')

