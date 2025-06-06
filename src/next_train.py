import pandas as pd
from datetime import datetime

stops = pd.read_csv("src\\gtfs_files\\stops.txt")
routes = pd.read_csv("src\\gtfs_files\\routes.txt")
trips = pd.read_csv("src\\gtfs_files\\trips.txt")
stop_times = pd.read_csv("src\\gtfs_files\\stop_times.txt")
calendar = pd.read_csv("src\\gtfs_files\\calendar.txt")

def parse_time(t):
    try:
        h, m, s = map(int, t.split(":"))
        h = h % 24  # Para evitar erros com horas acima de 24
        return datetime.strptime(f"{h:02}:{m:02}:{s:02}", "%H:%M:%S").time()
    except:
        return None

def next_train_time(line, station, hour):
    # 1. Descobre o dia da semana atual
    day_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    toda_index = datetime.now().weekday()  # 0 = segunda, 6 = domingo
    today = day_week[toda_index]

    # 2. Filtra os service_ids ativos hoje
    active_services = calendar[calendar[today] == 1]['service_id'].tolist()

    # 3. Filtra trips da linha A e com service_id válido hoje
    line_id = routes[routes['route_short_name'] == line[0]]['route_id'].values[0]
    valid_trips = trips[(trips['route_id'] == line_id) & (trips['service_id'].isin(active_services))]

    # 4. Filtra horários dessas trips
    schedules = stop_times[stop_times['trip_id'].isin(valid_trips['trip_id'])]
    schedules = schedules.merge(stops, on='stop_id')
    station_schedules = schedules[schedules['stop_name'] == station]

    # 5. Converte os horários e filtra pelo tempo atual
    station_schedules = station_schedules.copy()
    station_schedules['arrival_time_parsed'] = station_schedules['arrival_time'].apply(parse_time)
    # agora = datetime.now().time()

    # 6. Filtra os horários futuros
    nexts = station_schedules[station_schedules['arrival_time_parsed'] > parse_time(hour)]
    next = nexts.sort_values(by='arrival_time_parsed').head(1)

    # 7. Exibe o próximo trem válido
    if next.empty:
        return hour
    
    return next['arrival_time_parsed'].iloc[0].strftime("%H:%M:%S")
