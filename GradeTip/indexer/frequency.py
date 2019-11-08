from GradeTip.content.identifier import IDGenerator
from GradeTip.redis.hash import RedisHash


class FrequencyStore:
    def __init__(self, redis_manager):
        self.redis = redis_manager
        self.id_generator = IDGenerator()

    def _tf_key(self, term):
        return "{}{}".format(self.id_generator.prefixes.tf, term)

    def _df_key(self, term):
        return "{}{}".format(self.id_generator.prefixes.df, term)

    def increment_doc_count(self):
        """
        Increments the total number of documents indexed
        """
        self.redis.increment(self.id_generator.value_names.doc_count)

    def increment_doc_frequency(self, term):
        key = self._df_key(term)
        self.redis.increment(key)

    def get_term_frequency(self, term, doc_id):
        key = self._tf_key(term)
        return RedisHash(key).get(doc_id)

    def set_term_frequency(self, term, doc_id, frequency):
        key = self._tf_key(term)
        term_data = RedisHash(key)
        term_data.set(doc_id, frequency)
