# -*- coding: utf-8 -*-
from flask import Blueprint, request, render_template, redirect,\
                    url_for, session, current_app
from flask.ext.api import status
from app import app, db
from app.common import generate_random_num_str
from app.models.chat_mod import Room
from . import chat
manage = Blueprint('view_manage', __name__)


@manage.route('/', methods=['GET'])
def index():
    if 'manager_id' not in session:
        return redirect(url_for('view_manage.login'))
    return render_template("manage/index.html",
                           manager_email=session['manager_email'])


@manage.route('/login', methods=['GET'])
def login():
    return render_template("manage/login.html")


@manage.route('/create-room', methods=['POST'])
def create_room():
    if 'manager_email' not in session:
        return redirect(url_for('view_manage.login'))
    while True:
        new_room_id = generate_random_num_str(6)
        if Room.query.get(new_room_id) is None:
            break
    db.session.add(
        Room(
            room_id=new_room_id,
            room_name=request.form['room_name'],
            room_manager=session['manager_email']
        )
    )
    db.session.commit()
    current_app.config[new_room_id] = {
        'current_user_num': 0
    }
    return request.url_root + "chat/" + new_room_id
