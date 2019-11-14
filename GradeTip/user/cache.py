from GradeTip.content.identifier import NameProvider
from GradeTip.redis.hash import RedisHash
from GradeTip.redis.set import RedisSet


class UserCache:
    def __init__(self):
        self.name_provider = NameProvider()
        self.cached = RedisSet(self.name_provider.set_names.cached_ips)

    def is_cached(self, ip_address):
        """
        Returns whether or not IP address is cached
        :param ip_address: IP address to check
        :return: boolean indicating if IP is cached
        """
        return self.cached.exists(ip_address)

    def get(self, ip_address):
        """
        Returns cached data for IP address
        :param ip_address: IP address to get cached data for
        :return: dict containing cached data
        """
        key = self._get_key_for(ip_address)
        return RedisHash(key).to_dict()

    def set(self, ip_address, data):
        """
        Sets cached data for given IP address
        :param ip_address: IP address to set cached data for
        :param data: data to set in cache
        """
        key = self._get_key_for(ip_address)
        return RedisHash(key).update(data)

    def _get_key_for(self, ip_address):
        """
        Returns redis key for ip address cached data
        """
        return "{}{}".format(self.name_provider.prefixes.ip, ip_address)
