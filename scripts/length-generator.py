import argparse
import json
import math
import sys

parser = argparse.ArgumentParser()
parser.add_argument('map_file', nargs='?', default='./static/map/data/mapData.json') 
parser.add_argument('planet_file', nargs='?', default='./content/docs/setting/hyperspace_planet_pairs.json')
parser.add_argument('template_file', nargs='?', default='./content/docs/setting/hyperspace_speeds.md.template')
parser.add_argument('result_file', nargs='?', default='./content/docs/setting/hyperspace_speeds.md')
args = parser.parse_args()

# Скорость световых лет за год
SPEED_PER_SHIP_TYPE = {'trader': [736.5, 1089.0],
                      'warship': [2153.4, 2576.4],
                      'courier': [2576.4, 3000.0]}

def load_map_data(map_filename):
    map_data = {}
    with open(map_filename, 'r', encoding='utf-8') as map_file:
        data = json.load(map_file)
        for item in data:
            map_data[item["id"]] = item

    return map_data

def load_planet_pairs(planet_filename):
    with open(planet_filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def calculate_distance(lhs, rhs, scale=12.5):
    '''Возвращает примерную дистанцию между звездами по прямой в световых годах'''
    x_distance = abs((lhs["position"]["x"] - rhs["position"]["x"]))
    y_distance = abs((lhs["position"]["x"] - rhs["position"]["y"]))

    return (math.sqrt(math.pow(x_distance, 2) + math.pow(y_distance, 2)))/scale

def get_speed(distance):
    '''За сколько дней корабли разного типа пройдут переданную дистанцию'''
    return {k: [round(365*distance/v[0]), round(365*distance/v[1])] for k, v in SPEED_PER_SHIP_TYPE.items()}

def format_speed(speed):
    left = speed[1]
    right = speed[0]
    return f"≈{left}&nbsp;дней" if left==right else  f"<nobr>≈{left}–{right}&nbsp;дней</nobr>"

def format_row(row):
    return f"|<nobr>{row['lhs_name']}</nobr>|<nobr>{row['rhs_name']}</nobr>|≈{row['distance']:.2f}&nbsp;св.&nbsp;лет|{format_speed(row['speed']['trader'])}|{format_speed(row['speed']['warship'])}|{format_speed(row['speed']['courier'])}|"

def get_row(map_data, left_idx, right_idx):
    lhs = map_data[left_idx]
    rhs = map_data[right_idx]
    distance = calculate_distance (lhs, rhs)
    speed = get_speed(distance)
    return  dict(lhs_name = lhs["name"], rhs_name = rhs["name"], distance = distance, speed = speed)

def calculate_rows(map_data, planet_pairs):
    rows = list()

    for i in planet_pairs:
        rows.append(get_row (map_data, i[0], i[1]))
    rows.sort(key = lambda x: (x["lhs_name"], x["rhs_name"]))

    return rows

def print_template(template_file_name):
    with open(template_file_name, 'r', encoding='utf-8') as file:
        text = file.read()

    print(text)

map_data = load_map_data(args.map_file)
planet_pairs = load_planet_pairs(args.planet_file)
rows = calculate_rows(map_data, planet_pairs)

with open(args.result_file, 'w', encoding='utf-8') as sys.stdout:
    print_template(args.template_file)
    for r in rows:
        print(format_row(r))
