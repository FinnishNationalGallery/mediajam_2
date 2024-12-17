import os
import shutil
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
import modules.mp_metadata as mp_metadata
from forms.form_metadata import *

metadata_bp = Blueprint('metadata', __name__)

config = dotenv_values(".env")
DATA_path = config['DATA_FOLDER']
METADATA_path = config['METADATA_FOLDER']
SIP_path = config['SIP_FOLDER']
SERVER_ffmpeg = config['SERVER_FFMPEG']

@metadata_bp.route("/metadata")
@login_required
def metadata():
   files = sorted(os.listdir(METADATA_path))
   return render_template('metadata.html', files=files, environment=mp_metadata.MP_ENV, METADATA_path=METADATA_path)

@metadata_bp.route("/metadata_get")
@login_required
def metadata_get():
   return render_template('index.html')

@metadata_bp.route("/metadata_save_object_by_id")
@login_required
def metadata_save_object_by_id():
   objectid = request.args.get('objectid')
   #object_id = request.vars.object_id
   message = mp_metadata.save_object_by_id(objectid)
   if len(message) > 1:
          flash("Something went wrong when saving object XML file. ERROR MESSAGE: " + message, 'error')
   return redirect(url_for('data.data'))

@metadata_bp.route("/metadata_create_lido_xml")
@login_required
def metadata_create_lido_xml():
   objectid = request.args.get('objectid')
   session['mp_inv'] = ""
   session['mp_id'] = ""
   session['mp_name'] = ""
   #object_id = request.vars.object_id
   message = mp_metadata.create_lido_xml(objectid)
   if len(message) > 1:
          flash("Something went wrong when creating Lido XML file. ERROR MESSAGE: " + message, 'error')
   return redirect(url_for('metadata.metadata'))

@metadata_bp.route("/metadata_load_attachment")
@login_required
def metadata_load_attachment():
   objectid = request.args.get('objectid')
   objectname = request.args.get('objectname')
   object_id = request.args.get('img_id')
   object_name = request.args.get('img_name')
   try:
      input = mp_metadata.load_attachment(object_id)
      with open(DATA_path+object_name,'wb') as f:
         shutil.copyfileobj(input, f)
      message = Markup("<a href="+url_for('metadata.metadata_object_by_id', objectid=objectid)+"> Go back to previous MuseumPlus Object!</a>")
      flash(message, 'success')
   except:
      flash("Something went wrong when downloading attachment file!", 'error' )
   return redirect(url_for('data.data'))

@metadata_bp.route("/metadata_read_lido_xml")
@login_required
def metadata_read_lido_xml():
   mp_inv, mp_id, mp_name, mp_created = mp_metadata.read_lido_xml()
   session['mp_inv'] = mp_inv
   session['mp_id'] = mp_id
   session['mp_name'] = mp_name
   session['mp_created'] = mp_created
   files = os.listdir(METADATA_path)
   return render_template('metadata.html', files=files)
   #return render_template('metadata_read_lido.html', mp_inv=mp_inv, mp_id=mp_id, mp_created=mp_created)

@metadata_bp.route('/metadata_import_description')
@login_required
def metadata_import_description():
   subprocess_args('import-description', METADATA_path+'lido_description.xml', '--workspace', SIP_path)
   return redirect(url_for('sip.sip'))


@metadata_bp.route('/metadata_search/', methods=['GET', 'POST'])
@login_required
def metadata_search():
   form = SearchMuseumPlus()
   if form.validate_on_submit():
      objectid = form.objectid.data
      invnumber = form.inventorynumber.data
      title = form.title.data
      message = objectid + invnumber + title
      if len(objectid) > 3:
         return redirect(url_for('metadata.metadata_object_by_id', objectid=objectid))
      elif len(invnumber) > 3:
         return redirect(url_for('metadata.get_object_by_inv', invnumber=invnumber))
      elif len(title) > 3:
         return redirect(url_for('metadata.get_object_by_title', title=title))
      else:
         flash('Minimum length for search field is 3 characters!', 'error')
         return render_template('metadata_search.html', form=form, message=message)
   message = ""
   return render_template('metadata_search.html', form=form, message=message, environment=mp_metadata.MP_ENV)

@metadata_bp.route('/metadata_object_by_id/', methods=['GET', 'POST'])
@login_required
def metadata_object_by_id():
   back = request.referrer
   objectid = request.args.get('objectid')
   xml_data, thumb_status = mp_metadata.get_object_by_id(objectid)
   return render_template('metadata_object_by_id.html', xml_data=xml_data, thumb_status=thumb_status, objectid=objectid, back=back)

@metadata_bp.route('/get_object_by_inv/', methods=['GET', 'POST'])
@login_required
def get_object_by_inv():
   back = request.referrer
   invnumber = request.args.get('invnumber')
   totalSize, mylist, xml = mp_metadata.get_object_by_number(invnumber)
   return render_template('metadata_object_by_inv.html', totalSize=totalSize, objects=mylist, xml=xml, back=back)

@metadata_bp.route('/get_object_by_title/', methods=['GET', 'POST'])
@login_required
def get_object_by_title():
   back = request.referrer
   title = request.args.get('title')
   totalSize, mylist, xml = mp_metadata.get_object_by_title(title)
   return render_template('metadata_object_by_title.html', title=title, totalSize=totalSize, objects=mylist, xml=xml, back=back)

@metadata_bp.route("/metadata_delete")
@login_required
def metadata_delete():
   delete_really = request.args.get('delete') 
   if delete_really == "True":
      try:
         shutil.rmtree(METADATA_path)
         os.mkdir(METADATA_path)
         session['mp_inv'] = ""
         session['mp_id'] = ""
         session['mp_name'] = ""
         session['mp_created'] = ""
      except:
         message = "Could not delete folder!"
         flash(message, 'error')
   else:
      message = Markup("Do you really want to delete this folder? <a href=" + url_for('metadata.metadata_delete', delete="True") + "><button class=\"button is-danger\">Delete</button></a>"+" <a href=" + url_for('metadata.metadata') + "><button class=\"button is-dark\">Cancel</button> </a>")
      flash(message, 'error')
   return redirect(url_for('metadata.metadata'))

@metadata_bp.route("/metadata_file_delete")
@login_required
def metadata_file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = METADATA_path # This is dummy but secure
   deleteMessage = ""
   if os.path.isfile(path + file):
      try:
         os.remove(path + file)
      except:
         deleteMessage = "Cannot delete file!"
   elif os.path.isdir(path + file):
      try:
         shutil.rmtree(path + file)
      except:
         deleteMessage = "Cannot delete directory!"
   return redirect(url_for(view))
