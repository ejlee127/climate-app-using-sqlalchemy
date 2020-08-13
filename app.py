
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect tables
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<br>"
        f"Welcome to Hawaii Climate API<br/>"
        f"<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart_date&gt<br/>"
        f"/api/v1.0/&ltstart_date&gt/&ltend_date&gt<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precp():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query the last date in measurement dataset
    last_dt = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Query the precipitation data for the last 12 months
    year_ago = dt.datetime.strptime(last_dt[0], "%Y-%m-%d") - dt.timedelta(days=365)
    prcp_data = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date > year_ago).\
            order_by(measurement.date).all()

    session.close()

    prcp_dict_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_dict_list.append(prcp_dict)

    return jsonify(prcp_dict_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the most active stations
    active_st = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.date).desc()).first()

    # Query one year data for the most active station
    last_dt = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(last_dt[0], "%Y-%m-%d") - dt.timedelta(days=365)

    tobs_data = session.query(measurement.date, measurement.tobs).\
            filter(measurement.date > year_ago).\
            filter(measurement.station == active_st[0]).\
            order_by(measurement.date).all()

    session.close()

    tobs_dict_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_dict_list.append(tobs_dict)

    return jsonify(tobs_dict_list)

@app.route("/api/v1.0/<start_date>")
def start_date_tobs(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query tobs data for all days from <start_date>

    tobs_data = session.query(
            measurement.date, 
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    tobs_dict_list = []
    for date, tmin, tavg, tmax in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = round(tavg, 1)
        tobs_dict["TMAX"] = tmax
        tobs_dict_list.append(tobs_dict)

    return jsonify(tobs_dict_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_tobs(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query tobs data for all days from <start_date>

    tobs_data = session.query(
            measurement.date, 
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).\
            filter(measurement.date <= end_date).\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    tobs_dict_list = []
    for date, tmin, tavg, tmax in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = round(tavg, 1)
        tobs_dict["TMAX"] = tmax
        tobs_dict_list.append(tobs_dict)

    return jsonify(tobs_dict_list)

if __name__ == '__main__':
    app.run(debug=True)

