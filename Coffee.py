import json
import os
import requests
from flask import Flask
from geopy import distance
import folium
from dotenv import load_dotenv


def json_reader():
    with open('coffee.json', 'r', encoding='CP1251') as coffee_data:
        coffee = coffee_data.read()
    return json.loads(coffee)


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def where_are_you():
    load_dotenv("LoginData.env")
    apikey = os.getenv('apikey')
    address = str(input('Где вы находитесь? '))
    return fetch_coordinates(apikey, address)


def new_coffee_list_maker(coffee_list, lon, lat):
    new_coffee_list = []
    for content in coffee_list:
        name = str(content['Name'])
        lattitude = content['Latitude_WGS84']
        longtitude = content['Longitude_WGS84']
        coffee_distance = str(distance.distance(
            (lat, lon), (lattitude, longtitude)).km)
        new_coffee_list.append({'title': name, 'distance': coffee_distance,
                               'lattitude': lattitude, 'longtitude': longtitude})
    return new_coffee_list


def min_distance(shop_massive):
    return shop_massive['distance']


def map_maker(user_lat, user_lon, coffee_list):
    new_map = folium.Map((user_lat, user_lon), zoom_start=15)
    folium.Marker(location=[user_lat, user_lon],
                  tooltip="Это Вы",
                  popup=f'''Ваши координаты:
                  Широта {user_lat},
                  Долгота {user_lon}''',
                  icon=folium.Icon(
                      color='red',
                      prefix='fa',
                      icon='user'),
                  ).add_to(new_map)

    for content in coffee_list:
        lat = content['lattitude']
        lon = content['longtitude']
        name = content['title']
        dist = content['distance']
        folium.Marker(
            location=[lat, lon],
            tooltip=name,
            popup=f'''До "{name}"
            {str(round(float(dist)*1000))} метров''',
            icon=folium.Icon(color='black', prefix='fa', icon='coffee'),
        ).add_to(new_map)

    new_map.save('Coffee_map.html')


def hello_world():
    with open('Coffee_map.html', encoding="utf-8") as file:
        return file.read()


def main():
    coffee_list = json_reader()
    user_lon, user_lat = where_are_you()
    print('Рисуем карту')
    new_coffee_list = new_coffee_list_maker(coffee_list, user_lon, user_lat)
    sorted_coffee_list = sorted(new_coffee_list, key=min_distance)[:5]
    map_maker(user_lat, user_lon, sorted_coffee_list)
    print('Готово!')
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
