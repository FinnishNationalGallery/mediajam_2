import json
import os
import shutil
import datetime
import uuid
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from modules import mp_metadata
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup

sip_bp = Blueprint('sip', __name__)

config = dotenv_values(".env")
SIGNATURE = config['SIGNATURE']
SIP_path = config['SIP_FOLDER']
SIPLOG_path = config['SIPLOG_FOLDER']
ORGANIZATION = config['ORGANIZATION']
CONTRACTID = config['CONTRACTID']

@sip_bp.route("/sip")
@login_required
def sip():
   diskinfo = get_diskinfo()
   try:
      with open(SIPLOG_path+"output.txt") as f:
         output = f.read()
   except:
      output = ""
   try:   
      with open(SIPLOG_path+"outerror.txt") as f:
         outerr = f.read()
   except:
      outerr = ""
   files = sorted(os.listdir(SIP_path))
   ###
   return render_template('sip.html', files=files, diskinfo=diskinfo, output=output, outerr=outerr, SIP_path=SIP_path)

@sip_bp.route("/sip_make_all")
@login_required
def sip_make_all():
   sip_premis_event_created()
   sip_compile_structmap()
   sip_compile_mets()
   sip_sign_mets()
   return redirect(url_for('sip.sip'))

@sip_bp.route("/sip_premis_event_created") # MuseumPlus digital object creation
@login_required
def sip_premis_event_created():
   redir = request.args.get('flag') # If you want to make own button for this function
   event_type = "creation"
   event_detail = "MuseumPlus object creation"
   event_outcome = "success"
   event_outcome_detail = "MuseumPlus object creation premis-event succeeded"
   agent_name = "MuseumPlus"
   agent_type = "software"
   if not session.get('mp_created'): # Try get date from MuseumPlus Lido read
      session['mp_created'] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()
      #session['mp_created'] = "2018-04-12T14:09:00.233"
   subprocess_args('premis-event', event_type, session['mp_created'], '--event_detail', event_detail, '--event_outcome', event_outcome, '--event_outcome_detail', event_outcome_detail, '--workspace', SIP_path, '--agent_name', agent_name, '--agent_type', agent_type)
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_compile_structmap")
@login_required
def sip_compile_structmap():
   redir = request.args.get('flag') # If you want to make own button for this function
   subprocess_args('compile-structmap', '--workspace', SIP_path)
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_compile_mets")
@login_required
def sip_compile_mets():
   redir = request.args.get('flag') # If you want to make own button for this function
   if not session.get('mp_inv'):
      objid = str(uuid.uuid1())
   else:
      objid = session['mp_inv']
   subprocess_args('compile-mets','--workspace', SIP_path , 'ch', ORGANIZATION, CONTRACTID, '--objid',objid, '--copy_files', '--clean')
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_compile_mets_update")
@login_required
def sip_compile_mets_update():
   redir = request.args.get('flag') # If you want to make own button for this function
   LastmodDate = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat() 
   ###
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   mets_createdate = settings['mets_createdate']
   ###
   if session['mp_inv']:
      objid = session['mp_inv']
   else:
      objid = str(uuid.uuid1())
   subprocess_args('compile-mets','--workspace', SIP_path , 'ch', ORGANIZATION, CONTRACTID, '--objid',objid, '--create_date', mets_createdate, '--last_moddate', LastmodDate, '--record_status', 'update', '--copy_files', '--clean')
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_sign_mets")
@login_required
def sip_sign_mets():
   redir = request.args.get('flag') # If you want to make own button for this function
   #subprocess_args('./sign.sh', SIGNATURE, SIP_path)
   subprocess_args('sign-mets', SIGNATURE, '--workspace', SIP_path)
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_make_tar")
@login_required
def sip_make_tar():
   redir = request.args.get('flag') # If you want to make own button for this function
   lido_inv, lido_id, lido_name, lido_created = mp_metadata.read_mets_lido_xml()
   if lido_id > "":
      sip_filename = lido_id + '.tar'
      message = "TAR package from mets.xml file: "+lido_name + ", Inv nro: " +lido_inv + ", MuseumPlus ID: " + lido_id
      msg_status = "success"
   else:
      sip_filename = str(uuid.uuid1()) + '.tar'
      message = "SOMETHING WENT WRONG! TAR package name is: " + sip_filename
      msg_status = "error"
   subprocess_args('compress', '--tar_filename',  sip_filename, SIP_path)
   if redir == 'once':
      flash( message,msg_status)
      return redirect(url_for('sip.sip'))
   return True








@sip_bp.route("/sip_delete")
@login_required
def sip_delete():
   delete_really = request.args.get('delete') 
   if delete_really == "True":
      try:
         os.remove(SIPLOG_path+"output.txt")
         os.remove(SIPLOG_path+"outerror.txt")
         try:
            os.remove(SIPLOG_path+"datanative.txt")
         except:
            pass
         shutil.rmtree(SIP_path)
         os.mkdir(SIP_path)
         session['mp_inv'] = ""
         session['mp_id'] = ""
         session['mp_name'] = ""
         session['mp_created'] = ""
      except:
         message = "Could not delete folder!"
         flash(message, 'error')
   else:
      message = Markup("Do you really want to delete this folder? <a href=" + url_for('sip.sip_delete', delete="True") + "><button class=\"button is-danger\">Delete</button></a>"+" <a href=" + url_for('sip.sip') + "><button class=\"button is-dark\">Cancel</button> </a>")
      flash(message, 'error')
   return redirect(url_for('sip.sip'))

@sip_bp.route("/sip_file_delete")
@login_required
def sip_file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = SIP_path # This is dummy but secure
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