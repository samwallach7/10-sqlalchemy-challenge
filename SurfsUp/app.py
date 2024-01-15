# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
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
        f"/api/v1.0/<start>"
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

@app.route("/api/v1.0/<start>")

@app.route("/api/v1.0/<start>/<end>")

if __name__ == '__main__':
    app.run(debug=True)