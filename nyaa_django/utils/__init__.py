from operator import and_
from datetime import datetime
import hashlib
import posixpath
import string
import math
from django.db.models import Q, F
from django.core import exceptions
from django.http import response
import bencode

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

def int_or_none(st):
    if st.isdigit():
        return int(st)

def parse_cats(cstr):
    '''And no, I don't mean the furry kind (=^..^=)'''
    try:
        ct, sc = cstr.split('_',1)
    except ValueError:
        return (None, None)
    return (int_or_none(ct), int_or_none(sc))

class HttpResponseSeeOther(response.HttpResponseRedirectBase):
    '''Implement these redirects properly according to IETF standards'''
    status_code = 303

class SearchQuery(object):
    def __init__(self, qd):
        self.category, self.subcategory = parse_cats(qd.get('category', ''))
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
    
class TorrentInfo(object):
    '''There's *supposed* to be a library for this, but it's in C++/Boost,
    its Python bindings are poorly documented, and it's painful to use.
    Why no one seems to have developed a better library is beyond me.'''
    def __init__(torrent, data):
        '''Odd variable name choice to ease porting'''
        torrent_data = bencode.bdecode(data)
        bencoded_info = bencode.bencode(torrent_data['info'])
        info_hash = hashlib.sha1(bencoded_info).hexdigest()

        # two types of torrents:
        # single file:
        #   length, name, piece length, pieces

        # multiple files:
        #   files, name, piece length, pieces

        # info keys: length, name, piece length, pieces
        info = torrent_data['info']

        torrent.name = info['name']
        torrent.hash = info_hash

        torrent.t_announce = torrent_data['announce']
        torrent.t_comment = torrent_data['comment']
        torrent.t_created_by = torrent_data['created by']
        torrent.t_creation_date = datetime.utcfromtimestamp(
            torrent_data['creation date'])
        if 'files' in info:
            torrent.file_data = info['files']
            torrent.filesize = sum((
                f['length'] for f in torrent.file_data))
        else:
            torrent.file_data = []
            torrent.filesize = info['length']
    @property
    def file_paths(self):
        return [posixpath.join(ifo) for ifo in (
            fd['path'] for fd in self.file_data)]
    @property
    def file_sizes(self):
        return [fd['length'] for fd in self.file_data]
    def get_model(self, model, **kwargs):
        dct = {fn:getattr(self, fn) for fn in (field.name.encode(
                        'UTF-8') for field in model._meta.fields
                        ) if hasattr(self,fn)}
        dct.update(kwargs)
        return model(**dct)