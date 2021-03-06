# The contents of this file are subject to the BitTorrent Open Source License
# Version 1.1 (the License).  You may not copy or use this file, in either
# source code or executable form, except in compliance with the License.  You
# may obtain a copy of the License at http://www.bittorrent.com/license/.
#
# Software distributed under the License is distributed on an AS IS basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied.  See the License
# for the specific language governing rights and limitations under the
# License.

# Written by Petru Paler


class BTFailure(Exception):
    pass


def decode_int(data, f):
    f += 1
    newf = data.index(b'e', f)
    n = int(data[f:newf])
    if data[f:f+1] == b'-':
        if data[f+1:f+2] == b'0':
            raise ValueError
    elif data[f:f+1] == b'0' and newf != f + 1:
        raise ValueError
    return n, newf + 1


def decode_string(data, f):
    colon = data.index(b':', f)
    n = int(data[f:colon])
    if data[f:f+1] == b'0' and colon != f + 1:
        raise ValueError
    colon += 1
    return data[colon:colon + n], colon + n


def decode_list(data, f):
    r, f = [], f + 1
    while data[f:f+1] != b'e':
        v, f = decode_func[data[f:f+1]](data, f)
        r.append(v)
    return r, f + 1


def decode_dict(data, f):
    r, f = {}, f + 1
    while data[f:f+1] != b'e':
        k, f = decode_string(data, f)
        k = k.decode('utf-8')
        r[k], f = decode_func[data[f:f+1]](data, f)
    return r, f + 1


decode_func = {
    b'l': decode_list,
    b'd': decode_dict,
    b'i': decode_int,
    b'0': decode_string,
    b'1': decode_string,
    b'2': decode_string,
    b'3': decode_string,
    b'4': decode_string,
    b'5': decode_string,
    b'6': decode_string,
    b'7': decode_string,
    b'8': decode_string,
    b'9': decode_string,
}


def bdecode(data):
    try:
        r, l = decode_func[data[0:1]](data, 0)
    except (IndexError, KeyError, ValueError):
        raise BTFailure("not a valid bencoded string")
    if l != len(data):
        raise BTFailure("invalid bencoded value (data after valid prefix)")
    return r


class Bencached:
    __slots__ = ['bencoded']

    def __init__(self, s):
        self.bencoded = s


def encode_bencached(x, r):
    r.append(x.bencoded)


def encode_int(x, r):
    r.extend((b'i', str(x).encode('utf-8'), b'e'))


def encode_bool(x, r):
    if x:
        encode_int(1, r)
    else:
        encode_int(0, r)


def encode_string(x, r):
    if isinstance(x, str):
        x = x.encode('utf-8')
    r.extend((str(len(x)).encode('utf-8'), b':', x))


def encode_list(x, r):
    r.append(b'l')
    for i in x:
        encode_func[type(i)](i, r)
    r.append(b'e')


def encode_dict(x, r):
    r.append(b'd')
    ilist = list(x.items())
    ilist.sort()
    for k, v in ilist:
        r.extend((str(len(k)).encode('utf-8'), b':', k.encode('utf-8')))
        encode_func[type(v)](v, r)
    r.append(b'e')


encode_func = {
    Bencached: encode_bencached,
    int: encode_int,
    bytes: encode_string,
    str: encode_string,
    list: encode_list,
    tuple: encode_list,
    dict: encode_dict,
    bool: encode_bool,
}


def bencode(x):
    r = []
    encode_func[type(x)](x, r)
    return b''.join(r)
