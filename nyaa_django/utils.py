from operator import and_
import string
import math
from django.db.models import Q, F

LCHEX = string.hexdigits.translate(None,string.uppercase)

def is_hash(st):
    '''A bit of a hack. Remove all the hex chars and see what's left'''
    return len(st)==40 and st.isalnum() and st.translate(None,LCHEX) is not ''

def pretty_size(size):
    if not size:
        return '0 B'
    exp = min(4, int(math.log(size, 1024)))
    suffix = ['B', 'KiB', 'MiB', 'GiB', 'TiB'][exp]
    size = size / 1024**exp
    return '{size:.1f} {suffix}'.format(size=size,suffix=suffix)

class SearchQuery(object):
    def __init__(self, qd):
        cs = qd.get('category', '').split('_',1)
        if len(cs) == 2:
            ct, sc = cs
            if ct.isdigit():
                self.category = int(ct)
            else:
                self.category = None
            if sc.isdigit():
                self.subcategory = int(sc)
            else:
                self.subcategory = None
        else:
            self.category = self.subcategory = None
        st = qd.get('status', '')
        if st.isdigit():
            self.status = int(st)
        else:
            self.status = None
        self.sort = qd.get('sort', None)
        self.order = qd.get('order', None)
        mx = qd.get('max', '')
        if mx.isdigit():
            self.max = int(mx)
        else:
            self.max = 20
        self.query = qd.get('query', '').lower()
    def construct(self):
        qfs = list()
        if self.category:
            qfs.append(Q(category_id=self.category))
        if self.subcategory:
            qfs.append(Q(category_id=self.subcategory))
        if self.status:
            qfs.append(Q(category_id=self.status))
        if is_hash(self.query):
            qfs = [Q(hash=self.query)] # Having a hash overrides all else
        elif self.query.startswith('=~'):
            qr = self.query[2:].strip()
            qfs.append(Q(name__iregex=qr))
        else:
            words = self.query.split()
            for word in words:
                qfs.append(Q(name__icontains=word))
        if qfs: return reduce(and_, qfs)
        
class SortQuery(object):
    def __init__(self, qd):
        self.sort = qd.get('sort', '').lower()
        self.order = qd.get('order', '').lower()
    def construct(self):
        if self.sort:
            st = F(self.sort)
            if self.order == 'desc':
                srt = st.desc()
            else:
                srt = st.asc()
        else:
            srt = None
        return srt