import sqlite3
from app import mail
from flask_mail import Message
from app.models import User, Schedule, ScheduleDetails, OEEtbl
from flask import url_for
from datetime import datetime, date, timedelta
from sqlalchemy import func


# sqlite db connection
def db_connect(arg=None):
    con = sqlite3.connect('app/database.db')
    if not arg:
        con.row_factory = sqlite3.Row
        return con
    elif arg == 'update':
        return con
    else:
        return 'error'


# had problems with serializing object, both with alchemy & sqlite. 
# (data) Solution below from https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
# turned above solution into a function for reusability
def serialize(cur, result):
    data = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    return data


def send_reset_email(user):
    token = user.reset_token()
    msg = Message('Password Reset Request', sender='noreply@nutreelife.co.uk', recipients=[user.email])

    msg.body = f''' To reset your password, please visit the following link:
{url_for('users.reset_token', token=token, _external=True)}    
'''
    mail.send(msg)



def get_planned_output(line_num):

    # get index of day
    today_index = date.weekday(date.today())

    # get week commencement date
    wc_date = date.today() - timedelta(days=today_index)
    
    # get schedule id using the wc date date
    sid = Schedule.query.filter(Schedule.wc_date==wc_date).first()

    if sid:
        # query for planned output based on day of the week
        if today_index == 0:
            planned_output = ScheduleDetails.query.with_entities(func.sum(ScheduleDetails.monday).label('sum')).filter_by(schedule_id=sid.id, line_num=line_num).first()
        elif today_index == 1:
            planned_output = ScheduleDetails.query.with_entities(func.sum(ScheduleDetails.tuesday).label('sum')).filter_by(schedule_id=sid.id, line_num=line_num).first()
        elif today_index == 2:
            planned_output = ScheduleDetails.query.with_entities(func.sum(ScheduleDetails.wednesday).label('sum')).filter_by(schedule_id=sid.id, line_num=line_num).first()
        elif today_index == 3:
            planned_output = ScheduleDetails.query.with_entities(func.sum(ScheduleDetails.thursday).label('sum')).filter_by(schedule_id=sid.id, line_num=line_num).first()
        elif today_index == 4:
            planned_output = ScheduleDetails.query.with_entities(func.sum(ScheduleDetails.friday).label('sum')).filter_by(schedule_id=sid.id, line_num=line_num).first()
        elif today_index == 5:
            planned_output = ScheduleDetails.query.with_entities(func.sum(ScheduleDetails.saturday).label('sum')).filter_by(schedule_id=sid.id, line_num=line_num).first()
        elif today_index == 6:
            planned_output = ScheduleDetails.query.with_entities(func.sum(ScheduleDetails.sunday).label('sum')).filter_by(schedule_id=sid.id, line_num=line_num).first()

        return planned_output.sum
    
    else:
        return 0


def get_conformance_to_plan(oee_id, good_count):

    """ Conformance To Plan (CTP) score """

    query = OEEtbl.query.filter_by(id=oee_id).first()
    planned_output = query.planned_output

    try:
        ctp = round(((good_count / planned_output)*100),1)
    except ZeroDivisionError:
        ctp = 0
    
    return ctp
