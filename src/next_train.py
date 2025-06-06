import pandas as pd
from datetime import datetime, timedelta

stops = pd.read_csv("src\\gtfs_files\\stops.txt")
routes = pd.read_csv("src\\gtfs_files\\routes.txt")
trips = pd.read_csv("src\\gtfs_files\\trips.txt")
stop_times = pd.read_csv("src\\gtfs_files\\stop_times.txt")
calendar = pd.read_csv("src\\gtfs_files\\calendar.txt")
day_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def parse_time(t):
    try:
        h, m, s = map(int, t.split(":"))
        h = h % 24  # To avoid errors with hours above 24
        return datetime.strptime(f"{h:02}:{m:02}:{s:02}", "%H:%M:%S").time()
    except:
        return None
    
def sum_time_from_travel(time, add):
    dummy_date = datetime.combine(datetime.today(), time)
    return (dummy_date + timedelta(hours=add)).time()

def next_train_time(line, station, hour, time_travel):
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
    station_schedules = station_schedules.copy()
    station_schedules['arrival_time_parsed'] = station_schedules['arrival_time'].apply(parse_time)
    next_schedules = station_schedules[station_schedules['arrival_time_parsed'] > sum_time_from_travel(hour,time_travel)]

    # 6. Get the next time and convert it to a string
    next_train = next_schedules.sort_values(by='arrival_time_parsed').iloc[0]
    next_train_hour = next_train['arrival_time_parsed']
    
    return next_train_hour
