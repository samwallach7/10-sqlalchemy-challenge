# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to Sam Wallach's Hawaii Station API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Query all dates and precipitation values
    
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    previous_year_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= previous_year).\
        order_by(Measurement.date).all()
    
    session.close()

    # Creating a dictionary from the row data and append to a list
    all_prcp_data = []
    for date, prcp in previous_year_prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp_data.append(prcp_dict)
    
    return jsonify(all_prcp_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.station, Station.name).all()
    session.close()

    all_stations = []
    for station, name in station_list:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)
    
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature_observations():
    session = Session(engine)
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previous_year).\
        order_by(Measurement.date).all()
    session.close()

    usc00519281_previous_year = []
    for date, tobs in most_active_station_tobs:
        most_active_dict = {}
        most_active_dict["date"] = date
        most_active_dict["tobs"] = tobs
        usc00519281_previous_year.append(most_active_dict)

    return jsonify(usc00519281_previous_year)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    session = Session(engine)
    dates_tobs = session.query(Measurement.date, Measurement.tobs).\
        order_by(Measurement.date).all()
    for date in dates_tobs:
        search_term = date["date"]

        if search_term == start:
            sel = [Measurement.date,
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)]
            selected_tobs_data = session.query(*sel).\
                filter(Measurement.date >= start).\
                order_by(Measurement.date).all()
            start_tobs = []
            for sel in selected_tobs_data:
                start_dict = {}
                start_dict["min tobs"] = func.min(Measurement.tobs)
                start_dict["avg tobs"] = func.avg(Measurement.tobs)
                start_dict["max tobs"] = func.max(Measurement.tobs)
                start_tobs.append(start_dict)

            
            return jsonify(start_tobs)
    return jsonify({"error": "Date {start} not found. Please enter date as 'yyyy-mm-dd'"}), 404

@app.route("/api/v1.0/<start>/<end>")
def temperature_end(start, end):
    session = Session(engine)
    station_dates = session.query(Measurement.date, Measurement.tobs).\
        order_by(Measurement.date).all()
    for date in station_dates:
        search_term = date["date"]

        if search_term == end:
            sel = [Measurement.date,
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)]
            start_end_tobs_data = session.query(*sel).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                order_by(Measurement.date).all()
            return jsonify(start_end_tobs_data)
    return jsonify({"error": "Date {start} or {end} not found. Please enter date as 'yyyy-mm-dd'"}), 404



if __name__ == '__main__':
    app.run(debug=True)