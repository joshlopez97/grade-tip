from GradeTip.content.identifier import NameProvider
from GradeTip.redis.hash import RedisHash


class FrequencyStore:
    def __init__(self, redis_manager):
        self.redis = redis_manager
        self.name_provider = NameProvider()

    def _tf_key(self, term):
        """
        Redis key for getting term frequencies
        :param term: term to get Redis key for
        :return: string containing Redis key
        """
        return "{}{}".format(self.name_provider.prefixes.tf, term)

    def _df_key(self, term):
        """
        Redis key for getting document frequencies
        :param term: term to get Redis key for
        :return: string containing Redis key
        """
        return "{}{}".format(self.name_provider.prefixes.df, term)

    def increment_doc_count(self):
        """
        Increments the total number of documents indexed
        """
        self.redis.increment(self.name_provider.value_names.doc_count)

    def increment_df(self, term):
        """
        Increment document frequency for a given term
        :param term: term to increase df value for
        """
        key = self._df_key(term)
        self.redis.increment(key)

    def get_tf(self, term, doc_id=None):
        """
        Get term frequency data for term
        :param term: term to get tf data for
        :param doc_id: (optional) provide doc_id to only get tf data for the associated document
        :return: dict containing tf_data
        """
        key = self._tf_key(term)
        if doc_id is None:
            return RedisHash(key).to_dict()
        return RedisHash(key).get(doc_id)

    def set_tf(self, term, doc_id, frequency):
        """
        Set tf data for (term, doc_id) pair
        :param term: term to set tf data for
        :param doc_id: document to set tf data for
        :param frequency: data to put in the hash for the (term, doc_id) pair
        """
        key = self._tf_key(term)
        term_data = RedisHash(key)
        term_data.set(doc_id, frequency)
