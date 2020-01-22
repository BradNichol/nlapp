from app.models import User, Schedule, ScheduleDetails, OEEtbl
from datetime import datetime, date, timedelta
from sqlalchemy import func



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