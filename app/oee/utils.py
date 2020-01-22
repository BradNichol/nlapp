from app.models import User, Schedule, ScheduleDetails, OEEtbl
from app.utils import db_connect
from datetime import datetime, date, timedelta
from sqlalchemy import func
from flask import request, redirect


def add_update_oee_details(oee_id, selectorType, selectTime, units):
    """ Function to add / update OEE details and update job status """

    # connect and update database
    con = db_connect()
    cur = con.cursor()

    cur.execute("SELECT oee_id FROM OEE_details WHERE oee_id =:oee_id AND type=:type", {'oee_id':oee_id, 'type':selectorType})
    row = cur.fetchall()

    if len(row) != 1:

        # Insert
        sql = """INSERT INTO OEE_details (oee_id, type, {}) VALUES (?, ?, ?)""".format(selectTime)
        cur.execute(sql, (oee_id, selectorType, units))
        con.commit()

    else:
        # update
        sql = """UPDATE OEE_details SET {}=? WHERE oee_id=? AND type=? """.format(selectTime)
        cur.execute(sql, (units, oee_id, selectorType))
        con.commit()
        
        # check if units produced > ordered units and update orders to 'Completed'
        if selectorType == "Product":
            update_job_status(oee_id)

    con.close()
            
        
    return 'Success'


def update_job_status(oee_id):
    """ Update job status to 'Complete' if produced qty > ordered qty """

    # connect and update database
    con = db_connect()
    cur = con.cursor()

    # with order_id I can sum all rows in table for orders that span across multiple days
    cur.execute("""SELECT order_id, SUM(_07+_08+_09+_10+_11+_12+_13+_14+_15+_16+_17+_18+_19+_20+_21+_22) AS sum 
                                        FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                                        WHERE type = 'Product' AND oee_id =:oee_id """, {'oee_id': oee_id})

    row = cur.fetchall()
    
    order_id = row[0]['order_id']
    totalUnits = row[0]['sum']


    # get total ordered units
    cur.execute("""SELECT units, status FROM orders WHERE order_id=:order_id""", {'order_id':order_id})
    row = cur.fetchall()
    try:
        orderedUnits = row[0]['units']
    except:
        orderedUnits = 0

    if totalUnits >= orderedUnits:
    
        # update 
        sql = """UPDATE orders SET status=? WHERE order_id=? """
        status = "Completed"
        cur.execute(sql, (status, order_id))
        con.commit()
        con.close()

        return 1
    else:
        return 0
    
    




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