"""
ENGG1001 Assignment 2
Semester 1, 2021
"""

__author__ = "William Sawyer 46963608"
__email__ = "w.sawyer@uqconnect.edu.au"
__date__ = "Friday 23 April, 2021"

import pandas as pd


def arriving_buses(stop_name, start_time, end_time, date, interval):
    """ Determines the number of buses which arrive at a given stop per given
    interval of time within given period of time by calling other functions.

    Parameters:
        stop_name           (str): Name of the bus stop.
        start_time          (str): Time that the period starts (HH:MM format).
        end_time            (str): Time that the period ends (HH:MM format).
        date                (str): Date of the timetable (YYYYMMDD format).
        interval            (int): Length of time intervals checked (minutes).

    Return:
        list:               Number of buses arriving in each interval.
    """

    trips, stops, stop_times, calendar = read_data()

    service_ids = find_service(calendar, date)

    stoptime_subset, trip_subset = create_subsets(stops, stop_times, trips,
                                                  calendar, stop_name, date)

    counts = calculate_counts(start_time, end_time, interval,
                              stoptime_subset)

    return counts


def read_data():
    """ Converts data from text files to Pandas DataFrames. Converts data to
    DateTime objects, where appropriate. Discards stop_times greater than
    24:00:00.

    Return:
        tuple:                Formatted DataFrames created from text files.
    """

    trips = pd.read_csv("trips.txt")
    stops = pd.read_csv("stops.txt")
    stop_times = pd.read_csv("stop_times.txt")
    calendar = pd.read_csv("calendar.txt")

    # Converts appropriate data to Datetime. Times greater than 24:00:00 are
    # converted to NaT and discarded.
    stop_times['arrival_time'] = pd.to_datetime(stop_times['arrival_time'],
                                                errors='coerce')
    stop_times['departure_time'] = pd.to_datetime(stop_times[
                                                      'departure_time'],
                                                  errors='coerce')
    stop_times = stop_times.dropna(how='any')

    calendar['start_date'] = pd.to_datetime(calendar['start_date'],
                                            format='%Y%m%d')
    calendar['end_date'] = pd.to_datetime(calendar['end_date'],
                                          format='%Y%m%d')

    return trips, stops, stop_times, calendar


def find_service(calendar, date):
    """ Returns a list containing all services operating on a given date.

    Parameters:
        calendar            (pd.DataFrame): DataFrame created in read_data.
        date                (string): Date checked for operational services.

    Return:
        list:               IDs for services which operate on given date.
    """

    date = pd.to_datetime(date, format='%Y%m%d')
    day = date.dayofweek

    # Creates subset of calendar where the trips operate around given date.
    calendar_subset = calendar[(calendar['start_date'] <= date) & (calendar[
                                                        'end_date'] >= date)]

    # Adds service_id to service_ids <=> date falls on correct day of the week.
    service_ids = []
    for i in range(len(calendar_subset)):
        if calendar_subset.iloc[i, day + 1] == 1:
            service_ids.append(calendar_subset.iloc[i, 0])

    return service_ids


def create_subsets(stops, stop_times, trips, calendar, stop_name, date):
    """ Creates subsets of DataFrames related to given stop_name and date.

    Parameters:
        stops               (pd.DataFrame): DataFrame created in read_data.
        stop_times          (pd.DataFrame): DataFrame created in read_data.
        trips               (pd.DataFrame): DataFrame created in read_data.
        calendar            (pd.DataFrame): DataFrame created in read_data.
        stop_name           (str): Stop name which DataFrames will relate to.
        date                (str): Date which DataFrames will relate to.

    Return:
        tuple:              Subsets of DataFrames related to stop_name and date.
    """

    # Creates subset of stops related to given stop_name.
    if not stops[stops['stop_name'] == stop_name].empty:
        stops_subset = stops[stops['stop_name'] == stop_name]
    # If given stop_name is not in stops['stop_name'], checks 'parent_station'.
    elif stops[stops['stop_name'] == stop_name].empty:
        stops_subset = stops[stops['parent_station'] == stop_name]

    # Creates subset of stop_times related to stop_ids in stops_subset.
    stoptime_subset = stop_times[stop_times['stop_id'].isin(stops_subset[
                                                                'stop_id'])]

    trip_subset = trips[trips['trip_id'].isin(stoptime_subset['trip_id'])]

    service_ids = find_service(calendar, date)

    # Creates further subset of trip_subset related to service_ids.
    trip_subset = trip_subset[trip_subset['service_id'].isin(service_ids)]

    stoptime_subset = stoptime_subset[stoptime_subset['trip_id'].isin(
        trip_subset['trip_id'])]

    return stoptime_subset, trip_subset


def calculate_counts(start_time, end_time, interval, stoptime_subset):
    """ Creates a list of the number of trips in each time interval.

    Parameters:
        start_time          (str): Start of the period checked (HH:MM format).
        end_time            (str): End of the period checked (HH:MM format).
        interval            (int): The length of each time interval (minutes).
        stoptime_subset     (pd.DataFrame): DataFrame created in create_subsets.

    Return:
        list:               Number of trips in each interval.
    """

    start_time = pd.to_datetime(start_time, format='%H:%M')
    end_time = pd.to_datetime(end_time, format='%H:%M')
    interval = pd.to_timedelta(int(interval), unit='m')

    counts = []
    current_time = start_time
    while current_time < end_time:
        current_count = 0
        for row in stoptime_subset.index:
            if (current_time.time() <= stoptime_subset.loc[row,
                                                'arrival_time'].time()) and (
                    stoptime_subset.loc[row,
                                        'arrival_time'].time() < (
                            current_time + interval).time()):
                current_count += 1
        counts.append(current_count)
        current_time += interval

    return counts
