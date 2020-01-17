from flask import flash, redirect, render_template, request, url_for, Blueprint
from app import db
from flask_login import login_required, current_user
from app.utils import db_connect
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
    order_numbers = Orders.query.filter(Orders.status != 'Completed').all()


    return render_template('oee.html', oee = oee_overview, order_numbers=order_numbers)


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

        # add new OEE sheet
        new_oee = OEEtbl(order_id=order_id, operator_id=operator_id, line_num=line_num, start_date=todays_date, speed=line_speed, actual_operators=actual_operators)
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
            if request.form.get('selector') == "Product":   
                
                # with order_id I can sum all rows in table for orders that span across multiple days
                cur.execute("""SELECT order_id, SUM(_07+_08+_09+_10+_11+_12+_13+_14+_15+_16+_17+_18+_19+_20+_21+_22) AS sum 
                                                    FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                                                    WHERE type = 'Product' """)

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
            
            con.close()
            return redirect(url_for('oee.oeedetails', oee_id=oee_id))
    

    oeeInfo = OEEtbl.query.filter(OEEtbl.id==oee_id).first()
    
    
    con = db_connect()
    cur = con.cursor()
    cur.execute("""SELECT *, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amSum, 
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmSum 
                                    FROM OEE_details WHERE oee_id = :oee_id GROUP BY type
                                    ORDER BY (CASE type WHEN 'Product' THEN 1 END) DESC""", {'oee_id':oee_id})
    
    oeeStats = cur.fetchall()
    

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
        

        # add data into object
        data = OEEcalc(totalLostMinutes, CPM, totalUnitCount, totalRejects)
        
        # return OEE scores
        availability = round((data.availability()*100),2)
        performance = round((data.performance()*100),2)
        quality = round((data.quality()*100),2)
        oeeScore = round((data.OEEscore()*100),2)

        return render_template('oeedetails.html', oeeInfo=oeeInfo, oeeStats=oeeStats, availability=availability, performance=performance, quality=quality, oeeScore=oeeScore)
    else:
        return render_template('oeedetails.html', oeeInfo=oeeInfo, oeeStats=oeeStats)


@oee.route("/oee/reports/shift", methods=["GET", "POST"])
@login_required
def shiftreport():

    if request.method == "POST":
        oee_id = request.form.get('shiftSelect')

        if oee_id == None:
            flash('No shift reports available')
            return redirect(url_for('oee.shiftreport'))

        con = db_connect()
        cur = con.cursor()

        # unit count 
        cur.execute("""SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amShift,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmShift FROM 
                                    OEE_details WHERE type = 'Product' AND oee_id = :oee_id  """, {'oee_id':oee_id})
        unitCount = cur.fetchall()
        

        # overall shift details
        cur.execute("""SELECT *, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amSum, 
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmSum 
                                    FROM OEE_details WHERE oee_id = :oee_id GROUP BY type
                                    ORDER BY (CASE type WHEN 'Product' THEN 1 END) DESC""", {'oee_id':oee_id})
        oeeStats = cur.fetchall()

        # rejects
        cur.execute(""" SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amRejects,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmRejects FROM 
                                    OEE_details WHERE type = 'Rejects' AND oee_id = :oee_id  """, {'oee_id':oee_id})
        rejectStats = cur.fetchall()

        # downtime stats
        cur.execute("""SELECT *, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amShift,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmShift FROM 
                                    OEE_details WHERE type != 'Product' AND type !='Rejects' AND oee_id = :oee_id  """, {'oee_id':oee_id})
        downtimeStats = cur.fetchall()

        # machine running speed (CPM)
        query = OEEtbl.query.filter(OEEtbl.id==oee_id).first()
        CPM = query.speed

        
        # chart downtime data
        cur.execute("""SELECT type, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amSum, 
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmSum 
                                    FROM OEE_details WHERE type != 'Product' AND type !='Rejects' AND oee_id = :oee_id GROUP BY type
                                    """, {'oee_id':oee_id})
        chart_data = cur.fetchall()        


        # calc total lost minutes
        try:
            totalLostMinutes = downtimeStats[0]['amShift'] + downtimeStats[0]['pmShift']
        except TypeError:
            totalLostMinutes = 0
        # calc total units produced
        try:
            totalUnitCount = unitCount[0]['amShift'] + unitCount[0]['pmShift']
        except TypeError:
            totalUnitCount = 0
        # calc total rejected products
        try:
            totalRejects = rejectStats[0]['amRejects'] + rejectStats[0]['pmRejects']
        except TypeError:
            totalRejects = 0
        # calc good count
        goodCount = totalUnitCount - totalRejects

        # add data into object
        data = OEEcalc(totalLostMinutes, CPM, totalUnitCount, totalRejects)
        
        # return OEE scores
        availability = round((data.availability()*100),2)
        performance = round((data.performance()*100),2)
        quality = round((data.quality()*100),2)
        oeeScore = round((data.OEEscore()*100),2)
        
       
        # format lost time
        totalLostMinutes = timedelta(minutes=totalLostMinutes)

        # format shift length
        shiftLength = timedelta(minutes=data.shiftLength)

        # format good count
        goodCount = f'{goodCount:,}'

        # format total unit count
        totalUnitCount = f'{totalUnitCount:,}'

        # calc run time
        runtime = shiftLength - totalLostMinutes

        """ Chart Data """
        
        legend = 'Downtime Data (Minutes)'

        labels = []
        for i in chart_data:
            labels.append(i[0])
        
        values = []
        for i in chart_data:
            values.append(i[1] + i[2])
        
        
        
        oeeInfo = OEEtbl.query.filter_by(id = oee_id).first()

        oee_list = OEEtbl.query.order_by(desc(OEEtbl.start_date)).limit(20).all()

        return render_template('shiftreport.html', goodCount=goodCount, oee_list=oee_list, oeeStats=oeeStats, 
                                availability=availability, performance=performance, quality=quality, oeeScore=oeeScore, 
                                totalLostMinutes=totalLostMinutes, totalUnitCount=totalUnitCount, totalRejects=totalRejects, 
                                shiftLength=shiftLength, runtime=runtime, legend=legend, labels=labels, values=values, oeeInfo=oeeInfo)


    oee_list = OEEtbl.query.order_by(desc(OEEtbl.start_date)).limit(20).all()

    return render_template('shiftreport.html', oee_list=oee_list)





