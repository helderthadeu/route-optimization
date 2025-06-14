import pandas as pd
from datetime import datetime, timedelta

stops = pd.read_csv("src\\gtfs_files\\stops.txt")
routes = pd.read_csv("src\\gtfs_files\\routes.txt")
trips = pd.read_csv("src\\gtfs_files\\trips.txt")
stop_times = pd.read_csv("src\\gtfs_files\\stop_times.txt")
calendar = pd.read_csv("src\\gtfs_files\\calendar.txt")
day_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def parse_time(t):
    """
    Converts a string in the format HH:MM:SS to a datetime.time object,
    adjusting for hours greater than 24.

    Args:
        t (str): Time string in the format 'HH:MM:SS'. May exceed 24 hours.

    Returns:
        datetime.time or None: A time object, or None if parsing fails.
    """
    try:
        h, m, s = map(int, t.split(":"))
        h = h % 24  # To avoid errors with hours above 24
        return datetime.strptime(f"{h:02}:{m:02}:{s:02}", "%H:%M:%S").time()
    except:
        return None
    
def sum_time_from_travel(time, add):
    """
    Adds a number of hours to a datetime.time object.

    Args:
        time (datetime.time): Base time.
        add (int): Number of hours to add.

    Returns:
        datetime.time: Resulting time after addition.
    """
    dummy_date = datetime.combine(datetime.today(), time)
    return (dummy_date + timedelta(hours=add)).time()

def next_train_time(line, station, hour, time_travel):
    """
    Returns the time of the next available train for a given line and station,
    considering the current time and additional travel time.

    Args:
        line (str): Train line identifier (e.g., 'A', 'S', etc.).
        station (str): Name of the target station.
        hour (datetime.time): Current reference time.
        time_travel (int): Time (in hours) it takes to reach the station.

    Returns:
        datetime.time: Time of the next available train, or current time plus travel time if no trains remain.
    """
    # 1. Find out the current day of the week
    today_index = datetime.now().weekday()  # 0 = monday, 6 = sunday
    today = day_week[today_index]

    # 2. Filters the service_ids active today
    active_services = calendar[calendar[today] == 1]['service_id'].tolist()

    # 3. Filters trips from line and with service_id valid today
    line_prefix = line[0]
    if line_prefix == 'S':
        line_prefix = "SI"
    
    line_id = routes[routes['route_short_name'] == line_prefix]['route_id'].values[0]
    valid_trips = trips[(trips['route_id'] == line_id) & (trips['service_id'].isin(active_services))]

    # 4. Filter times for these trips
    schedules = stop_times[stop_times['trip_id'].isin(valid_trips['trip_id'])]
    schedules = schedules.merge(stops, on='stop_id')
    station_schedules = schedules[schedules['stop_name'] == station]

    # 5. Convert times and filter by current time
    now_plus_time_travel = sum_time_from_travel(hour,time_travel)
    station_schedules = station_schedules.copy()
    station_schedules['arrival_time_parsed'] = station_schedules['arrival_time'].apply(parse_time)
    next_schedules = station_schedules[station_schedules['arrival_time_parsed'] > now_plus_time_travel]

    # 6. Get the next time and convert it to a string
    if next_schedules.empty:
        return now_plus_time_travel
    
    next_train = next_schedules.sort_values(by='arrival_time_parsed').iloc[0]
    next_train_hour = next_train['arrival_time_parsed']
    
    return next_train_hour
