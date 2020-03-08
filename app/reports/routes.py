
from flask import flash, redirect, render_template, request, url_for, Blueprint
from app import db
from flask_login import login_required, current_user
from app.utils import db_connect
from app.oee.utils import get_planned_output, get_conformance_to_plan, add_update_oee_details, get_hourly_count
from app.reports.utils import sql_to_arr
from app.models import OEEtbl, Orders, OEEcalc
from datetime import datetime, date, timedelta
from sqlalchemy import desc

reports = Blueprint('reports', __name__, template_folder='templates')

@reports.route("/reports/shift", methods=["GET", "POST"])
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
        good_count = totalUnitCount - totalRejects

        hourlyCount = 8

        # add data into object
        data = OEEcalc(hourlyCount, totalLostMinutes, CPM, totalUnitCount, totalRejects)
        
        # return OEE scores
        availability = round((data.availability()*100),2)
        performance = round((data.performance()*100),2)
        quality = round((data.quality()*100),2)
        oeeScore = round((data.OEEscore()*100),2)

        # get conformance To Plan (CTP) score
        ctp = get_conformance_to_plan(oee_id, good_count)

       
        # format lost time
        totalLostMinutes = timedelta(minutes=totalLostMinutes)

        # format shift length
        shiftLength = timedelta(minutes=data.shiftLength)

        # format good count
        good_count = f'{good_count:,}'

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

        return render_template('shiftreport.html', good_count=good_count, oee_list=oee_list, oeeStats=oeeStats, 
                                availability=availability, performance=performance, quality=quality, oeeScore=oeeScore, 
                                totalLostMinutes=totalLostMinutes, totalUnitCount=totalUnitCount, totalRejects=totalRejects, 
                                shiftLength=shiftLength, runtime=runtime, legend=legend, labels=labels, values=values, oeeInfo=oeeInfo, ctp=ctp)


    oee_list = OEEtbl.query.order_by(desc(OEEtbl.start_date)).limit(20).all()

    return render_template('shiftreport.html', oee_list=oee_list)




@reports.route("/reports/production", methods=["GET", "POST"])
@login_required
def productionReport():

    if request.method == "POST":

        from_date = request.form.get('fromDate')
        to_date = request.form.get('toDate')

        line_num = 'IS NOT NULL'
        
        con = db_connect()
        cur = con.cursor()

        # get daily production count + no. day count 
        cur.execute("""SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS sum_am_count,
                        SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS sum_pm_count,
                        COUNT(DISTINCT start_date) as day_count
                        FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                        WHERE type = 'Product' AND DATE(start_date) >= '{}' 
                        AND DATE(start_date) <= '{}' AND line_num {} GROUP BY start_date  """.format(from_date, to_date, line_num))
        daily_sum_results = cur.fetchall()

        # get daily rejects
        cur.execute(""" SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS sum_am_rejects,
                        SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS sum_pm_rejects FROM 
                        OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                        WHERE type = 'Rejects' AND DATE(start_date) >= '{}' 
                        AND DATE(start_date) <= '{}' AND line_num {} GROUP BY start_date  """.format(from_date, to_date, line_num))
        daily_reject_results = cur.fetchall()

        # average daily downtime 
        cur.execute("""SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS sum_downtime_am,
                                SUM(_15+_16+_17+_18+_19+_20+_21+_22) sum_downtime_pm 
                                FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                                WHERE type != 'Product' AND type !='Rejects' 
                                AND DATE(start_date) >= '{}' 
                                AND DATE(start_date) <= '{}' AND line_num {} GROUP BY start_date """.format(from_date, to_date, line_num))
        daily_downtime_results = cur.fetchall()
    
        # get total avg daily count across shifts (except catch used if no data present)
        try:
            avg_daily_count = (daily_sum_results[0]['sum_am_count'] + daily_sum_results[0]['sum_pm_count']) / daily_sum_results[0]['day_count']
        except:
            avg_daily_count = 0
        # get total avg daily rejects across shifts
        try:
            avg_daily_rejects = (daily_reject_results[0]['sum_am_rejects'] + daily_reject_results[0]['sum_pm_rejects']) / daily_sum_results[0]['day_count']
        except:
            avg_daily_rejects = 0
        # get total avg daily downtime
        try:
            avg_daily_downtime = (daily_downtime_results[0]['sum_downtime_am'] + daily_downtime_results[0]['sum_downtime_pm']) / daily_sum_results[0]['day_count']
        except:
            avg_daily_downtime = 0 

        
        context = {
            'avg_daily_good_count' : f'{avg_daily_count-avg_daily_rejects:,}',
            'avg_daily_rejects' : avg_daily_rejects,
            'avg_daily_downtime' : timedelta(minutes=avg_daily_downtime)
        }


        return render_template('productionreport.html', **context)

    return render_template('productionreport.html')