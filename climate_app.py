# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    """List all available api routes."""
    return (
        f"Hawaii Surfs Up Available API Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start_date<br>"
        f"/api/v1.0/start_date/end_date<br>"
        f"Note: start_date and end_date would be in 'YYYY-MM-DD' format.<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query results to a Dictionary using `date` as the key and `prcp` as the value.
    prcp_results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date).all()
    
    all_prcp = {}
    for result in prcp_results:
        date = result[0]
        prcp = result[1]
        all_prcp[date] = prcp

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Return a json list of stations from the dataset.
    station_results = session.query(Station.station).all()

    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def prev_temp():
    # Return a json list of Temperature Observations (tobs) for the previous year - 
    # Using 2016-08-23 as previous year date start point since the last data point is 2017-08-23
    prev_results = session.query(Measurement.tobs).filter(Measurement.date >= "2016-08-23").all()
    prev_tobs = []
    prev_tobs = list(np.ravel(prev_results))

    return jsonify(prev_tobs)

@app.route("/api/v1.0/<start_date>")
def temp_start(start_date):
    # Query using start date
    start_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).first()
    # Create dictionary from results
    temp_start_dict = {"TMIN": start_results[0], "TMAX": start_results[1], "TAVG": start_results[2]}
    return jsonify(temp_start_dict)

#start/end date route
@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_start_end(start_date, end_date):
    # Query using start date and end date
    start_end_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).first()
    # Create dictionary from results
    temp_end_dict = {"TMIN": start_end_results[0], "TMAX": start_end_results[1], "TAVG": start_end_results[2]}
    return jsonify(temp_end_dict)

if __name__ == '__main__':
    app.run(debug=True)