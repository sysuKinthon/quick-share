# -*- coding: utf-8 -*-
import os
from flask import Blueprint, request, render_template,\
                    url_for, send_from_directory
from flask.ext.api import status
from app import app, db
from app.common import get_file_format, generate_random_hash,\
                                generate_random_num_str
from app.models.share_mod import TmpFileMap, File
share = Blueprint('view_share', __name__)


@share.route('/', methods=['GET'])
def index():
    return render_template("share/index.html")


@share.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        if request.args.get('flowChunkNumber') == '1':
            q_result = TmpFileMap.query.get(request.args.get('flowIdentifier'))
            if not q_result:
                db.session.add(
                    TmpFileMap(
                        file_identifer=request.args.get('flowIdentifier'),
                        file_name=request.args.get('flowFilename'),
                        total_size=int(request.args.get('flowTotalSize')),
                        current_size=0,
                        current_chunk=0,
                        group_code=int(request.args.get('groupCode')),
                    )
                )
                db.session.commit()
        return "Ready for content", status.HTTP_204_NO_CONTENT
    elif request.method == 'POST':
        file_chunk = request.files['file'].read()
        q_result = TmpFileMap.query.get(request.form['flowIdentifier'])
        if q_result.current_chunk + 1\
                == int(request.form['flowChunkNumber']):
            q_result.current_size += int(request.form['flowCurrentChunkSize'])
            q_result.current_chunk += 1
            with open(os.path.join(app.config['TMP_UPLOAD_FOLDER'],
                      request.form['flowIdentifier']), 'a') as f:
                f.write(file_chunk)
        if q_result.current_size == q_result.total_size:
            file_id = generate_random_hash()
            File()
            db.session.add(
                File(
                    file_id=file_id,
                    file_name=q_result.file_name,
                    file_format=q_result.file_format,
                    group_code=q_result.group_code,
                )
            )
            print os.path.join(app.config['TMP_UPLOAD_FOLDER'],
                               q_result.id)
            os.rename(
                os.path.join(app.config['TMP_UPLOAD_FOLDER'],
                             q_result.id),
                os.path.join(app.config['UPLOAD_FOLDER'],
                             file_id))
            db.session.delete(q_result)
        db.session.commit()
        print File.query.all()
        print TmpFileMap.query.all()
        return "OK", status.HTTP_200_OK


@share.route('/download/<string:file_id>', methods=['GET'])
def download_file(file_id):
    file = File.query.get(file_id)
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        file_id,
        as_attachment=True,
        attachment_filename=file.file_name)
