import json
import traceback

from flask import current_app as app, request

from GradeTip.redis import redis_values
from GradeTip.schools import school_store
from GradeTip.schools.location import GeolocationClient, LocationMapper
from GradeTip.user import user_cache


def nearest():
    """
    Endpoint for returning the N closest schools to a user's location. Location comes from
    browser (contingent on user providing location), and uses IP address geolocation as a
    fallback. There is also an offset feature used to get the next N closest schools.

    :return: JSON containing N closest school names and their ids
    """
    response = {'schools': [], 'sids': []}
    try:
        latitude, longitude = (request.form.get("lat"), request.form.get("lon"))
        if not latitude or not longitude:
            app.logger.debug("Location not provided, using IP address to determine location")
            client = GeolocationClient(redis_values, user_cache)
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            latitude, longitude, location_str = client.locate_using_ip(ip)
            if location_str is not None:
                response["approximate_location"] = location_str
        else:
            app.logger.debug("Location provided {}, {}".format(latitude, longitude))
            latitude, longitude = (float(latitude), float(longitude))
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            if ip is not None:
                ip_str = str(ip)
                user_cache.set(ip_str, {
                    "lon": longitude,
                    "lat": latitude
                })
                user_cache.delete(ip_str, "approximate_location")
        exclude = json.loads(request.form.get('last'))
        quantity = int(request.form.get('quantity', 5))
        app.logger.debug("exclude={}".format(exclude))
        app.logger.debug("quantity={}".format(quantity))
        mapper = LocationMapper(latitude, longitude)
        response.update(mapper.closest_schools(quantity, exclude))
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
    app.logger.debug("Returning data {}".format(response))
    return json.dumps(response)


def colleges():
    """
    Returns college data.
    :return: JSON containing college data
    """
    return json.dumps(school_store.get_college_data())
