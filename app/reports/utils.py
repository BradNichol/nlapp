
from app.utils import db_connect
from app.models import OEEcalc

# Function to get product/reject numbers by date
def get_product_count(from_date, to_date, line_num, unit_type):
    con = db_connect()
    cur = con.cursor()

    if unit_type == 'Product' or 'Rejects':
        cur.execute("""SELECT start_date, type, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS sum_am_count,
                        SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS sum_pm_count
                        FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                        WHERE DATE(start_date) >= '{}' 
                        AND DATE(start_date) <= '{}' AND line_num {} AND type='{}' GROUP BY start_date  """.format(from_date, to_date, line_num, unit_type ))
        results = cur.fetchall()

        return results

# Function to get downtime minutes
def get_downtime_minutes(from_date, to_date, line_num, col_type):
    con = db_connect()
    cur = con.cursor()
    cur.execute("""SELECT type, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS sum_downtime_am,
                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) sum_downtime_pm 
                    FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                    WHERE type != 'Product' AND type !='Rejects' 
                    AND DATE(start_date) >= '{}' 
                    AND DATE(start_date) <= '{}' AND line_num {} GROUP BY {} """.format(from_date, to_date, line_num, col_type))
    results = cur.fetchall()
    
    
    return results

# function to pass a range of PAQ-OEE data into dictionary
def oee_to_dict(downtime, line_speed, production, rejects):

    """ total_reject in object variable set to 0. 
        Manufacturing team are not currently recording rejects
        but I've left this feature in. Can't use list currently until
        data is present otherwise I get a out of index error. 
        Change to rejects[i] once team start to use """ 
   
    
    availability = []
    performance = []
    quality = []
    oee_score = []

    for i in range(len(production)):
        data = OEEcalc(hourly_count=8, total_lost_minutes=downtime[i], CPM=line_speed[i], total_unit_count=production[i], total_rejects=0) # see notes on rejects above
        availability.append(round((data.availability()*100),2))
        quality.append(round((data.quality()*100),2))
        performance.append(round((data.performance()*100),2))
        oee_score.append(round((data.OEEscore()*100),2))

     # add data into dictionary
    OEE_dict = {
        'availability' : availability,
        'performance' : performance,
        'quality' : quality,
        'OEE' : oee_score    
    }
    
    return OEE_dict