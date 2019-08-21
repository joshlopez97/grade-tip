import ipaddress
import json
import requests
import traceback
from GradeTip.models.entries import (get_time, too_many_requests)
from GradeTip.models import redis_server
from bisect import insort
from math import pow
from flask import request

from GradeTip import college_data, hsdata


def distance_between(coord1, coord2):
    return pow(coord1[0] - coord2[0], 2) + pow(coord1[1] - coord2[1], 2)


def nearest():
    to_return = {'schools': [], 'sids': []}
    if too_many_requests(redis_server):
        return json.dumps(to_return)
    else:
        try:
            lat, lon = (request.form.get("lat"), request.form.get("lon"))
            if not lat or not lon:
                print("using ip")
                lat, lon = locate(request)
            else:
                lat, lon = (float(lat), float(lon))
            last = json.loads(request.form.get('last'))
            shortest = []
            quantity = int(request.form.get('quantity', 5))
            for college in college_data.keys():
                if college not in last and 'lon' in college_data[college]:
                    dist = distance_between((college_data[college]['lon'], college_data[college]['lat']),
                                            (lon, lat))
                    if len(shortest) < quantity:
                        insort(shortest, (dist, college))
                    elif dist < shortest[quantity - 1][0]:
                        shortest.pop(quantity - 1)
                        insort(shortest, (dist, college))
            for school in shortest:
                to_return['schools'] += [school[1]]
                to_return['sids'] += [college_data[school[1]]['sid']]
        except Exception:
            print(traceback.format_exc())
        print(to_return)
        return json.dumps(to_return)




def locate(request):
    """
    Tries to determine geolocation of user based on IP address.
    On failure raises exception.
    """
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if ip and not ipaddress.ip_address(str(ip)).is_private:
        if redis_server.hexists('cached_ips', str(ip)):
            geoloc = redis_server.hget('cached_ips', ip).split(",")
            lon = float(geoloc[0])
            lat = float(geoloc[1])
        else:
            time = get_time()
            redis_server.lpush('ipreq', time)
            redis_server.ltrim('ipreq', 0, 99)
            georeq = requests.get('http://ip-api.com/json/{}'.format(str(ip)))
            resp = json.loads(georeq.content.decode('utf-8'))
            lon = float(resp['lon'])
            lat = float(resp['lat'])
            redis_server.hset('cached_ips', str(ip), "{},{}".format(lon, lat))
        return lat, lon
    else:
        return 37.8719, 122.2585
