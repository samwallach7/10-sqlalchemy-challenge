# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime, timedelta

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes

# Landing Page
@app.route("/")
def welcome():
    return (
        f"Welcome to Sam Wallach's Hawaii Station API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/user_input_start_date<br>"
        f"/api/v1.0/user_input_start_date/user_input_end_date<br>"
        f"<br>"
        f"Note: For the the user input start and end dates, please replace the text with a date (after 2010-01-01) using the format below<br>"
        f"<br>"
        f"For Start Date only: /api/v1.0/YYYY-MM-DD<br>"
        f"For Start and End Date: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br>"
        f"<br>"
        f"Thank you!"
    )

# Precipitation Page
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

# Stations Page
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.station, Station.name).all()
    session.close()

    # Creating a dictionary from the row data and append to a list
    all_stations = []
    for station, name in station_list:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)
    
    return jsonify(all_stations)

# Temperature Observation Page
@app.route("/api/v1.0/tobs")
def temperature_observations():
    session = Session(engine)
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previous_year).\
        order_by(Measurement.date).all()
    session.close()

    # Creating a dictionary from the row data and append to a list
    usc00519281_previous_year = []
    for date, tobs in most_active_station_tobs:
        most_active_dict = {}
        most_active_dict["date"] = date
        most_active_dict["tobs"] = tobs
        usc00519281_previous_year.append(most_active_dict)

    return jsonify(usc00519281_previous_year)

# Starting Date Page
@app.route("/api/v1.0/<start>")
def temperature_start(start):
    session = Session(engine)
    user_start_date = start
    date_format = "%Y-%m-%d"
    # There were issues with the app returning the first day from the query 
    # so the user input is being adjusted to one day prior. The query then starts after this date.
    date_object = datetime.strptime(user_start_date, date_format) - timedelta(1)
    
    sel = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]
    user_start_query = session.query(*sel).\
        filter(Measurement.date > date_object).all()
    session.close()

    # Creating a dictionary from the row data and append to a list
    user_start_tobs = []
    for min, max, avg in user_start_query:
        user_start_dict = {}
        user_start_dict["tmin"] = min
        user_start_dict["tmax"] = max
        user_start_dict["tavg"] = avg
        user_start_tobs.append(user_start_dict)

    return jsonify(user_start_tobs)

# Starting and Ending Date Page
@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    session = Session(engine)
    user_start_date = start
    user_end_date = end
    date_format = '%Y-%m-%d'
    # There were issues with the app returning the first day from the query 
    # so the user input is being adjusted to one day prior. The query then starts after this date.
    start_date_object = datetime.strptime(user_start_date, date_format) - timedelta(1)
    end_date_object = datetime.strptime(user_end_date, date_format)
    
    sel = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]
    user_start_query = session.query(*sel).\
        filter(Measurement.date > start_date_object).\
        filter(Measurement.date <= end_date_object).\
        order_by(Measurement.date).all()
    session.close()

    # Creating a dictionary from the row data and append to a list
    user_start_end_tobs = []
    for min, max, avg in user_start_query:
        user_start_end_dict = {}
        user_start_end_dict["tmin"] = min
        user_start_end_dict["tmax"] = max
        user_start_end_dict["tavg"] = avg
        user_start_end_tobs.append(user_start_end_dict)

    return jsonify(user_start_end_tobs)



if __name__ == '__main__':
    app.run(debug=True)