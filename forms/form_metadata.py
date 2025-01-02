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
    actorName = StringField('Creator', validators=[DataRequired()])
    eventDate = StringField('Creation time', validators=[DataRequired()])
    recordID = StringField('Record ID', validators=[DataRequired()])
    aineistotyyppi = StringField('Classification_\"Aineistotyyppi\"', validators=[DataRequired()])
    paaluokka = StringField('Classification_\"Pääluokka\"', validators=[DataRequired()])
    erikoisluokka = StringField('Classification_\"Erikoisluokka\"', validators=[DataRequired()])
    inventaarionumero = StringField('Inventory number', validators=[DataRequired()])
    submit = SubmitField('Generate Lido-XML')

