# Bootcamp assignment week 10

# Code by: Ricardo G. Mora, Jr.  11/19/2021


# Dependencies:
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

# create engine to hawaii.sqlite:
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model:
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table:
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup:
app = Flask(__name__)

# Flask Routes:

# Index route:
@app.route("/")
def welcome():
    return (
        f"Welcome to the Honolulu Hawaii Climate API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date/&LT;startdate&GT;<br/>"
        f"/api/v1.0/dates/&LT;startdate&GT;/&LT;enddate&GT;"
    )

# Precipitation route:
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all precipitation readings for the final 12 months of data
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    yearprior = str(dt.datetime.strptime(lastdate,"%Y-%m-%d") - dt.timedelta(days=365)).split(' ')[0]
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= yearprior).all()

    # Close session
    session.close()

    # Convert the query result into a dictionary
    output = {}
    for tuple in results:
        output[tuple[0]] = tuple[1]

    # Return json
    return jsonify(output)

# Stations route:
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations in the Stations table
    results = session.query(Station.station).all()

    # Close session
    session.close()

    # Convert list of tuples into normal list
    output = list(np.ravel(results))

    # Return json
    return jsonify(output)

# Tobs route:
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all tobs readings for the final 12 months of data at the most active station
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    yearprior = str(dt.datetime.strptime(lastdate,"%Y-%m-%d") - dt.timedelta(days=365)).split(' ')[0]
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= yearprior).\
        filter(Measurement.station == "USC00519281").all()

    # Close session
    session.close()

    # Convert the query result into a dictionary
    output = {}
    for tuple in results:
        output[tuple[0]] = tuple[1]

    # Return json
    return jsonify(output)


# Tobs startdate route:
@app.route("/api/v1.0/date/<startdate>")
def tobs_start(startdate):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all tobs readings after start_date and get min, avg, and max
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).all()
   
    # Close session
    session.close()

    # Convert query into dictionary
    output = {}
    for mintemp, avgtemp, maxtemp in results:
        output["Min"] = mintemp
        output["Max"] = maxtemp 
        try:      
            output["Avg"] = round(avgtemp, 1)
        except:
            output["Avg"] = avgtemp

    # Return json
    return jsonify(output)

# Tobs startdate/enddate route:
@app.route("/api/v1.0/dates/<startdate>/<enddate>")
def tobs_start_end(startdate, enddate):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all tobs readings after start_date and get min, avg, and max
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).\
        filter(Measurement.date <= enddate).all()

    # Close session
    session.close()

    # Convert query into dictionary
    output = {}
    for mintemp, avgtemp, maxtemp in results:
        output["Min"] = mintemp
        output["Max"] = maxtemp        
        try:      
            output["Avg"] = round(avgtemp, 1)
        except:
            output["Avg"] = avgtemp

    # Return json
    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)
