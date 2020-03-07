from flask import flash, redirect, render_template, request, url_for, Blueprint
from app import db
from flask_login import login_required, current_user
from app.utils import db_connect
from app.oee.utils import get_planned_output, get_conformance_to_plan, add_update_oee_details, get_hourly_count
from app.models import OEEtbl, Orders, OEEcalc
from datetime import datetime, date, timedelta
from sqlalchemy import desc

oee = Blueprint('oee', __name__, template_folder='templates')

@oee.route("/oee")
@login_required
def viewOee():

    """ View OEE list """

    oee_overview = OEEtbl.query.order_by(desc(OEEtbl.start_date)).limit(60).all()


    # for datalist menu
    batch_code = Orders.query.filter(Orders.status != 'Completed').all()


    return render_template('oee.html', oee = oee_overview, batch_code=batch_code)


@oee.route("/oee/add", methods=["POST"])
@login_required
def addOee():
    """ Add new OEE sheet """

    if request.method == "POST":

        # store OEE setup data from form 
        order_id = request.form.get('wOrder_id')
        operator_id = current_user.id
        line_num = request.form.get('lineNum')
        line_speed = request.form.get('cpm')
        actual_operators = request.form.get('actOperators')

        # get date
        todays_date = date.today()

        # get planned output
        planned_output = get_planned_output(line_num)
        
        # stop new sheet creation if one already exists for that line
        sheet_check = OEEtbl.query.filter_by(start_date=todays_date, line_num=line_num).first()
        if sheet_check:
            flash('An OEE sheet has already been created today for that line number.')
            return redirect(url_for('oee.viewOee'))


        # add new OEE sheet
        new_oee = OEEtbl(order_id=order_id, operator_id=operator_id, line_num=line_num, start_date=todays_date, speed=line_speed, actual_operators=actual_operators, planned_output=planned_output)
        db.session.add(new_oee)
        db.session.commit()

        
        # update Order status column to indicate job has started
        con = db_connect()
        cur = con.cursor()
        sql = "UPDATE orders SET status=? WHERE order_id=? "
        status = "In Progress"
        cur.execute(sql, (status, order_id))
        con.commit()
        con.close()
    
        flash('New OEE sheet added. Click to view.')
        return redirect(url_for('oee.viewOee'))
    else:
        flash('error')
        return redirect(url_for('oee.viewOee'))



@oee.route("/oee/<int:oee_id>", methods=["GET", "POST"])
@login_required
def oeedetails(oee_id):
    
    if request.form.get('selector'):
        selectTime = request.form.get('time')
        units = request.form.get('unitData')
        selectTime = request.form.get('time')
        selectorType = request.form.get('selector')

        # pass details into add / update function
        add_update_oee_details(oee_id, selectorType, selectTime,units)
        
        return redirect(url_for('oee.oeedetails', oee_id=oee_id))
    

    oeeInfo = OEEtbl.query.filter(OEEtbl.id==oee_id).first()
    

    con = db_connect()
    cur = con.cursor()
    cur.execute("""SELECT *, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amSum, 
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmSum 
                                    FROM OEE_details WHERE oee_id = :oee_id GROUP BY type
                                    ORDER BY (CASE type WHEN 'Product' THEN 1 END) DESC""", {'oee_id':oee_id})
    
    oeeStats = cur.fetchall()

    # get planned output (data is stored in OEE but originally set in schedule details. See utils)
    query = OEEtbl.query.filter_by(id=oee_id).first()

    planned_output = query.planned_output
   

    """
    --------------
    # calculate OEE (Availability * Performance * Quality = Overall Equipment Effectiveness)
    --------------
    """
    
    cur.execute("""SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amShift,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmShift FROM 
                                    OEE_details WHERE type != 'Product' AND type !='Rejects' AND oee_id = :oee_id  """, {'oee_id':oee_id})
    downtimeStats = cur.fetchall()

    cur.execute(""" SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amRejects,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmRejects FROM 
                                    OEE_details WHERE type = 'Rejects' AND oee_id = :oee_id  """, {'oee_id':oee_id})

    rejectStats = cur.fetchall()
    
    if downtimeStats[0]['amShift'] or downtimeStats[0]['pmShift']:

        # calc total lost minutes
        totalLostMinutes = downtimeStats[0]['amShift'] + downtimeStats[0]['pmShift']
        # calc total units produced
        totalUnitCount = oeeStats[0]['amSum'] + oeeStats[0]['pmSum']
        # calc total rejected products
        if rejectStats[0]['amRejects']:
            totalRejects = rejectStats[0]['amRejects'] + rejectStats[0]['pmRejects']
        else:
            totalRejects = 0
        
        CPM = oeeInfo.speed


        # get hourly count
        hourlyCount = get_hourly_count(oee_id)
        

        # add data into object
        data = OEEcalc(hourlyCount, totalLostMinutes, CPM, totalUnitCount, totalRejects)
        
        # return OEE scores
        availability = round((data.availability()*100),2)
        performance = round((data.performance()*100),2)
        quality = round((data.quality()*100),2)
        oeeScore = round((data.OEEscore()*100),2)

        
        return render_template('oeedetails.html', oeeInfo=oeeInfo, oeeStats=oeeStats, availability=availability, performance=performance, quality=quality, oeeScore=oeeScore, planned_output=planned_output)
    else:
        return render_template('oeedetails.html', oeeInfo=oeeInfo, oeeStats=oeeStats, planned_output=planned_output)


