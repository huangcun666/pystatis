#coding=utf8
from __future__ import division
from math import ceil
import math
import urlparse
import urllib
import tornado.web



class Pagination(object):
  def __init__(self, page, per_page, total_count,request):
      self.page = page
      self.per_page = per_page
      self.total_count = total_count
      self.request = request

  @property
  def pages(self):
      return int(ceil(self.total_count / float(self.per_page)))

  @property
  def has_prev(self):
      return self.page > 1

  @property
  def has_next(self):
      return self.page < self.pages

  def iter_pages(self, left_edge=2, left_current=2,
                 right_current=5, right_edge=2):
      last = 0
      for num in xrange(1, self.pages + 1):
          if num <= left_edge or\
             (num > self.page - left_current - 1 and\
              num < self.page + right_current) or\
             num > self.pages - right_edge:
              if last + 1 != num:
                  yield None
              yield num
              last = num

  def update_querystring(self,url, **kwargs):
        base_url = urlparse.urlsplit(url)
        query_args = urlparse.parse_qs(base_url.query)
        query_args.update(kwargs)
        for arg_name, arg_value in kwargs.iteritems():
            if arg_value is None:
                if query_args.has_key(arg_name):
                    del query_args[arg_name]

        query_string = urllib.urlencode(query_args, True)
        return urlparse.urlunsplit((base_url.scheme, base_url.netloc,
            base_url.path, query_string, base_url.fragment))

  def get_page_url(self,page):
            # don't allow ?page=1
            if page <= 1:
                page = None
            return self.update_querystring(self.request.uri, page=page)


# try:
#     import psyco
#     psyco.full()
# except:pass
# from math import ceil

# class Pagination(object):
#     def __init__(self, query, page, per_page=20):
#         #: pagination object.
#         self.query = query
#         #: the current page number (1 indexed)
#         self.page = page
#         #: the number of items to be displayed on a page.
#         self.per_page = per_page
#         #: the total number of items matching the query
#         self.total = self.query.count()
#         self.items = self.query.paginate(page,per_page)

#     @property
#     def pages(self):
#         """The total number of pages"""
#         return int(ceil(self.total / float(self.per_page)))

#     @property
#     def has_prev(self):
#         """True if a previous page exists"""
#         return self.page > 1

#     @property
#     def has_next(self):
#         """True if a next page exists."""
#         return self.page < self.pages

#     def prev(self):
#         assert self.query is not None
#         return self.query.paginate(self.page - 1, self.per_page)

#     def next(self):
#         assert self.query is not None
#         return self.query.paginate(self.page + 1, self.per_page)

#     def iter_pages(self, left_edge=2, left_current=2,
#                    right_current=5, right_edge=2):
#         """Iterates over the page numbers in the pagination.  The four
#         parameters control the thresholds how many numbers should be produced
#         from the sides.  Skipped page numbers are represented as `None`.
#         This is how you could render such a pagination in the templates:

#         .. sourcecode:: html+jinja

#             {% macro render_pagination(pagination, endpoint) %}
#               <div class=pagination>
#               {%- for page in pagination.iter_pages() %}
#                 {% if page %}
#                   {% if page != pagination.page %}
#                     <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
#                   {% else %}
#                     <strong>{{ page }}</strong>
#                   {% endif %}
#                 {% else %}
#                   <span class=ellipsis>…</span>
#                 {% endif %}
#               {%- endfor %}
#               </div>
#             {% endmacro %}
#         """
#         last = 0
#         for num in xrange(1, self.pages + 1):
#             if num <= left_edge or \
#                (num > self.page - left_current - 1 and \
#                 num < self.page + right_current) or \
#                num > self.pages - right_edge:
#                 if last + 1 != num:
#                     yield None
#                 yield num
#                 last = num