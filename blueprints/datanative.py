import json
import os
import shutil
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
from dateutil import parser

datanative_bp = Blueprint('datanative', __name__)

config = dotenv_values(".env")
DATA_path = config['DATA_FOLDER']
DATANATIVE_path = config['DATANATIVE_FOLDER']
SIP_path = config['SIP_FOLDER']
SIPLOG_path = config['SIPLOG_FOLDER']
SERVER_ffmpeg = config['SERVER_FFMPEG']

@datanative_bp.route('/datanative')
@login_required
def datanative():
   files = sorted(os.listdir(DATANATIVE_path))
   files_outcome = sorted(os.listdir(DATA_path))
   diskinfo = get_diskinfo()
   try:
      with open(SIPLOG_path+"datanative.txt") as f:
         datanative = f.read()
   except:
      datanative = ""
   if 'message' in session:
      pass
   else:
      session['message'] = ""
   return render_template('datanative.html', files=files, files_outcome=files_outcome, diskinfo=diskinfo, datanative=datanative, DATANATIVE_path=DATANATIVE_path)

@datanative_bp.route('/datanative_import/', methods=['GET', 'POST'])
@login_required
def datanative_import():
   diskinfo = get_diskinfo()
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   event_time = settings['prem_norm_date']
   agent_name = settings['prem_norm_agent']
   try:
      with open(SIPLOG_path+"datanative.txt") as f:
         datanative = f.read()
   except:
      datanative = ""
   if request.method == 'POST':
      file = request.form['file']
      outcome = request.form['outcome']
      datetime_obj = parser.parse(event_time)
      CreateDate = datetime_obj.isoformat()
      subprocess_args('import-object', '--workspace', SIP_path, '--skip_wellformed_check', DATANATIVE_path + file)
      subprocess_args('premis-event', 'normalization', CreateDate, '--workspace', SIP_path, '--event_detail', 'File conversion with FFMPEG program', '--event_outcome', 'success', '--event_outcome_detail', 'FFV1 video in Matroska container', '--agent_name', agent_name, '--agent_type', 'software', '--linking_object', 'source', DATANATIVE_path + file, '--linking_object', 'outcome', DATA_path + outcome, '--add_object_links')
      #
      logfile_datanative("Original file: "+file+" >>> "+"Normalized file: "+outcome+"\n")   

   #return redirect(url_for('datanative.datanative'))
   return render_template('datanative_import.html', file=file, outcome=outcome, diskinfo=diskinfo, datanative=datanative)

@datanative_bp.route("/datanative_file_delete")
@login_required
def datanative_file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = DATANATIVE_path # This is dummy but secure
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
