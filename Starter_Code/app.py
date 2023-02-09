from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# This section creates a connection to the local db
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)

# The following calculates the date of the last year
latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
latest_date = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")
past_year = latest_date.replace(year=latest_date.year-1)


app = Flask(__name__)

@app.route("/")
# This creates the homescreen to our server and displays the links to other pages
def home():
    print("Server received request for 'Home' page...")
    available_routes = [
        "/api/v1.0/precipitation", "/api/v1.0/stations", 
        "/api/v1.0/tobs", "/api/v1.0/<start>", 
        "/api/v1.0/<start>/<end>"]

    return available_routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    '''
    description: this function retrieves the date and precipitation data in the past year
    input: none
    output: json represented list
    '''
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
    '''
    description: this function retrieves all information regarding the station
    input: none
    output: json dictionary representing the station data
    '''
    # connects to the db and performs query to retrieve station data
    session = Session(engine)
    station_data = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    station_list = []

    # formats the station data output
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
    '''
    description: this function retrieves the date and temperatures recorded from the most active station
    input: none
    output: json dictionary representing the station data
    '''
    # connects to db and performs query to retrieve the stations' data that is most active
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

@app.route("/api/v1.0/<start>")
def start_(start):
    '''
    description: this function retrieves the min, max and average termperature from the start date to the end date
    input: 
        start str: start date represented as a string
    output: 
        temperature_describe json: json dictionary representing the station data
    '''
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
    '''
    description: this function retrieves the min, max and average termperature from the start date to the end date
    input: 
        start   str: start date represented as a string
        end     str: end date represented as a string
    output: 
        temperature_describe json: json dictionary representing the station data
    '''
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

if __name__ == "__main__":
    app.run(debug=True)