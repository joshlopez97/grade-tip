import ipaddress
import json
from bisect import insort
from datetime import datetime, timedelta
from math import pow

import requests
from flask import current_app as app

from GradeTip import college_data
from GradeTip.content.utility import get_time
from GradeTip.redis.list import RedisList


class GeolocationClient:
    def __init__(self, redis):
        """
        Makes request to geolocation api to approximate user location based on
        ip address.
        :param redis: RedisManager
        """
        self.requests = RedisList("ipreq")
        self.redis = redis

    def locate_using_ip(self, user_ip):
        """
        Approximate latitude and longitude of user by using IP address and making
        call to geolocation API.
        :param user_ip: string containing user's ip address
        :return: tuple containing (latitude, longitude) of user
        """

        if not self.too_many_requests() and user_ip and not ipaddress.ip_address(str(user_ip)).is_private:
            if self.redis.exists_in_hash('cached_ips', str(user_ip)):
                geoloc = self.redis.get_from_hash('cached_ips', user_ip).split(",")
                lon = float(geoloc[0])
                lat = float(geoloc[1])
            else:
                time = get_time()
                self.requests.push(time)
                self.requests.trim(0, 99)
                georeq = requests.get('http://ip-api.com/json/{}'.format(str(user_ip)))
                resp = json.loads(georeq.content.decode('utf-8'))
                lon = float(resp['lon'])
                lat = float(resp['lat'])
                self.redis.set_hash_value('cached_ips', str(user_ip), "{},{}".format(lat, lon))
            return lat, lon
        else:
            # default coordinates to return on failure
            return 37.8719, 122.2585

    def too_many_requests(self, allowed=100, minutes=1):
        """
        Determines if too many requests have been made to the geolocation API
        :param allowed: number of request allowed in specified timeframe
        :param minutes: timeframe given in number of minutes
        :return: boolean indicating if too many requests have been made
        """
        result = (self.requests.length() >= allowed and
                  datetime.now() - datetime.strptime(
                    self.requests.slice(-1, -1)[0], '%y%m%d%H%M%S') < timedelta(minutes=minutes))
        if result:
            app.logger.info("Too many requests made to location API")
        return result


class LocationMapper:
    def __init__(self, latitude, longitude):
        """
        Creates LocationMapper to find the closest N schools to a specified
        latitude and longitude pair.

        :param latitude: latitude of user location
        :param longitude: longitude of user location
        """
        self.data = college_data
        self.latitude = latitude
        self.longitude = longitude

    def distance_from(self, from_latitude, from_longitude):
        """
        Returns distance from another location (a college's longitude and latitude).

        :param from_latitude: latitude of college
        :param from_longitude: longitude of college
        :return: distance between user and college in degrees
        """
        return pow(self.latitude - from_latitude, 2) + pow(self.longitude - from_longitude, 2)

    def exclude_schools(self, exclude):
        """
        Removes list of schools from schools used in closest_schools algorithm.
        :param exclude: list of schools to exclude
        """
        for school in exclude:
            if school in self.data:
                del college_data[school]

    def closest_schools(self, quantity, exclude=None):
        """
        Calculates the closest N schools from user's location.
        :param quantity: N value
        :param exclude: list of schools to exclude (or None)
        :return: dictionary containing N closest school names and their ids
        """
        if isinstance(exclude, list) and len(exclude) > 0:
            self.exclude_schools(exclude)
        shortest = []
        for college in college_data.keys():
            # if school has geolocation data
            if 'lon' in college_data[college]:
                distance = self.distance_from(college_data[college]['lat'], college_data[college]['lon'])
                if len(shortest) < quantity:
                    insort(shortest, (distance, college))
                elif distance < shortest[quantity - 1][0]:
                    shortest.pop(quantity - 1)
                    insort(shortest, (distance, college))
        to_return = {'schools': [], 'sids': []}
        for school in shortest:
            to_return['schools'] += [school[1]]
            to_return['sids'] += [college_data[school[1]]['sid']]
        return to_return



