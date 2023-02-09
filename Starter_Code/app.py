from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)

latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
latest_date = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")
past_year = latest_date.replace(year=latest_date.year-1)


app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    available_routes = [
        "/api/v1.0/precipitation", "/api/v1.0/stations", 
        "/api/v1.0/tobs", "/api/v1.0/<start>", 
        "/api/v1.0/<start>/<end>"]

    return available_routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    date_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date > past_year).all()
    session.close()

    prcp_list = []

    for date,prcp in date_prcp:
        temp = {}
        temp['date'] = date
        temp['precipitation'] = prcp
        prcp_list.append(temp)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    station_list = []

    for row in station_data:
        temp = {}
        temp['station_id'] = row[0]
        temp['name'] = row[1]
        temp['latitude'] = row[2]
        temp['longitude'] = row[3]
        temp['elevation'] = row[4]

        station_list.append(temp)
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    past_year_tobs = session.query(measurement.date, measurement.tobs).filter(measurement.date > past_year).\
                filter(measurement.station == 'USC00519281')
    session.close()

    temperature_list = []

    for row in past_year_tobs:
        temp = {}
        temp["date"] = row[0]
        temp["tobs"] = row[1]
        temperature_list.append(temp)

    return jsonify(temperature_list)

########################################################

@app.route("/api/v1.0/<start>")
def start_(start):
    session = Session(engine)
    temperature_query = session.query(func.min(measurement.tobs), func.max(measurement.tobs),\
        func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    temperature_describe = []

    for row in temperature_query:
        temp = {}
        temp["min temperature"] = row[0]
        temp["max temperature"] = row[1]
        temp["avg temperature"] = row[2]
        temperature_describe.append(temp)

    return jsonify(temperature_describe)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    start = dt.datetime.strptime(start, '%Y/%m/%d')
    temperature_query = session.query(func.min(measurement.tobs), func.max(measurement.tobs),\
        func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    temperature_describe = []

    for row in temperature_query:
        temp = {}
        temp["min temperature"] = row[0]
        temp["max temperature"] = row[1]
        temp["avg temperature"] = row[2]
        temperature_describe.append(temp)

    return jsonify(temperature_describe)

########################################################

if __name__ == "__main__":
    app.run(debug=True)