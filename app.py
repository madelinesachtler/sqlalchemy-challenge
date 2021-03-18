from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
################################
#    DATABASE SET UP 
################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
Base = automap_base()

Base.prepare(engine, reflect=True)

measurment = Base.classes.measurement
station = Base.classes.station

##########
# ---- Flask Set up ---- # 
##########
app = Flask(__name__)
session = Session(engine)
#############
# -------Flask Routes -------------------------------------------------------- # 
#############

@app.route("/")
def home(): 
    """List all available API routes"""
    
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start_date/start <br/>"
        f" /api/v1.0/date/start/end <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation(): 
    #connecting our session from python to the database
    session = Session(engine)
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    precip_results = session.query(measurment.date, measurment.prcp).all()
    other_list = []
    for results in precip_results: 
        date_list = {}
        date_list["date"] = results[0]
        date_list["prcp"] = results[1]
        other_list.append(date_list)
    return jsonify(other_list)
    #Return the JSON representation of your dictionary.

@app.route("/api/v1.0/stations")
def stations():  
    session = Session(engine)
    # return JSON list of stations from data set 
   
    station_results = session.query(station.station).all()
    station_list = []
    for station2 in station_results: 
        station_list.append(station2[0])

    station_counts = session.query(measurment.station,func.count(measurment.station)).\
                    group_by(measurment.station).\
                    order_by(func.count(measurment.station).desc())

    station_count_list = []
    for row in station_counts: 
        station_count_list.append(row)
        
    
    return jsonify(station_list, station_count_list)
    

@app.route("/api/v1.0/tobs")
def temps(): 
    # Query the dates and temperature observations of the most active station for the last year of data.
    max_date = session.query(func.max(measurment.date)).first()
    twelve_months_prior = dt.datetime.strptime(max_date[0],"%Y-%m-%d") - dt.timedelta(days=365)
    
    active_station = session.query(measurment.station,func.count(measurment.station)).\
                    group_by(measurment.station).\
                    order_by(func.count(measurment.station).desc()).first()   
   
    query_active_station = session.query(measurment.tobs, measurment.date).\
                    filter(measurment.date >= twelve_months_prior, measurment.station == active_station[0]).\
                    order_by(measurment.date).all()

    return jsonify(query_active_station)
    
##this is not working 
@app.route("/api/v1.0/start_date/<start>")
def first(start): 
    max_temp = session.query(func.max(measurment.tobs)).\
               filter(measurment.date >= start).all() 
    
    min_temp = session.query(func.min(measurment.tobs)).\
               filter(measurment.date >= start).all()             

    avg_temp = session.query(func.avg(measurment.tobs)).\
               filter(measurment.date >= start).all() 
    start_list = []
    start_list.append(max_temp[0][0])
    start_list.append(min_temp[0][0])
    start_list.append(avg_temp[0][0])
    print(start_list)
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def last(start,end):


    max_temp1 = session.query(func.max(measurment.tobs)).\
               filter(measurment.date >= start, measurment.date<= end).all() 
    min_temp1 = session.query(func.min(measurment.tobs)).\
               filter(measurment.date >= start, measurment.date<= end).all()             

    avg_temp1 = session.query(func.avg(measurment.tobs)).\
               filter(measurment.date >= start, measurment.date<= end).all() 


    start_end_list = []

    start_end_list.append(max_temp1[0][0])
    start_end_list.append(min_temp1[0][0])
    start_end_list.append(avg_temp1[0][0])

    return jsonify(start_end_list)

if __name__ == "__main__": 
    app.run(debug=True)
