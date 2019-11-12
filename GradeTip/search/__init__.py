from GradeTip.content import listing_store
from GradeTip.redis import redis_values
from GradeTip.schools import school_store
from GradeTip.search.document_search import DocumentSearch
from GradeTip.search.school_search import SchoolSearch

document_search = DocumentSearch(redis_values, listing_store)
school_search = SchoolSearch(school_store)
