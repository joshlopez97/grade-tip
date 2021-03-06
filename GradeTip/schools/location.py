import ipaddress
import json
from bisect import insort
from datetime import datetime, timedelta
from math import pow

import requests
from flask import current_app as app

from GradeTip.content.utility import get_time
from GradeTip.redis.hash import RedisHash
from GradeTip.redis.list import RedisList
from GradeTip.schools import school_store


class GeolocationClient:
    def __init__(self, redis, user_cache):
        """
        Makes request to geolocation api to approximate user location based on
        ip address.
        :param redis: RedisManager
        """
        self.requests = RedisList("ipreq")
        self.redis = redis
        self.cache = user_cache

    def locate_using_ip(self, user_ip):
        """
        Approximate latitude and longitude of user by using IP address and making
        call to geolocation API.
        :param user_ip: string containing user's ip address
        :return: tuple containing (latitude, longitude) of user
        """

        if not self.too_many_requests() and user_ip and not ipaddress.ip_address(str(user_ip)).is_private:
            ip_string = str(user_ip)
            if self.cache.is_cached(ip_string):
                ip_data = self.cache.get(ip_string)
                lon = ip_data.get("lon")
                lat = ip_data.get("lat")
                location = ip_data.get("location")
            else:
                time = get_time()
                self.requests.push(time)
                self.requests.trim(0, 99)
                georeq = requests.get('http://ip-api.com/json/{}'.format(str(user_ip)))
                resp = json.loads(georeq.content.decode('utf-8'))
                lon = float(resp['lon'])
                lat = float(resp['lat'])
                location = "{}, {}".format(resp['city'], resp['region'])
                self.cache.set(ip_string, {
                    "lon": lon,
                    "lat": lat,
                    "location": location
                })
            return lat, lon, location
        else:
            app.logger.info("Using default coordinates 37.8719, 122.2585")
            # default coordinates to return on failure
            return 37.8719, 122.2585, "Mountain View, CA"

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
        self.data = school_store.get_college_data()
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
                del self.data[school]

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
        for college in self.data.keys():
            # if school has geolocation data
            if 'lon' in self.data[college]:
                distance = self.distance_from(self.data[college]['lat'], self.data[college]['lon'])
                if len(shortest) < quantity:
                    insort(shortest, (distance, college))
                elif distance < shortest[quantity - 1][0]:
                    shortest.pop(quantity - 1)
                    insort(shortest, (distance, college))
        to_return = {'schools': []}
        for school in shortest:
            to_return['schools'] += [{"name": school[1], "id": self.data[school[1]]['sid']}]
        return to_return
