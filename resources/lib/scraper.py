import simplejson
import urllib2
from datetime import datetime

API_URL = 'http://www.hardwareclips.com/api/xbmc/'

USER_AGENT = 'XBMC Addon: plugin.video.hwclips'

DEBUG = True


def get_root():
    log('get_root started')
    type, items = __api_request('root')
    entries = [{'name': i['name'],
                'path': i['apiPath'],
               } for i in items]
    log('get_root finished with %d entries' % len(entries))
    return entries


def get_folder(path):
    log('get_folder started with path: %s' % path)
    type, items = __api_request(path)
    if type == 'folders':
        entries = __format_folders(items)
    elif type == 'videos':
        entries = __format_videos(items)
    log('get_folder finished with %d entries' % len(entries))
    return type, entries


def __api_request(path):
    log('__api_request started with path: %s' % path)
    url = API_URL + path
    log('__api_request using url: %s' % url)
    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    response = urllib2.urlopen(req).read()
    log('__api_request got response with %d bytes' % len(response))
    json = simplejson.loads(response)
    type = json.keys()[0]
    items = json[type]
    if DEBUG and items:
        log('DEBUG: %s' % simplejson.dumps(items[0], indent=1))
    log('__api_request finished with type: %s' % type)
    return type, items


def __format_folders(items):
    return [{'name': i['name'],
             'id': i.get('ID', ''),
             'description': i.get('description', ''),
             'image': i.get('logo', ''),
             'website': i.get('www', ''),
             'gurl': i.get('gurl', ''),
             'path': i['apiPath'],
             'count': i.get('videoCount', '0'),
            } for i in items]


def __format_videos(items):
    return [{'name': i['title'],
             'id': i['ID'],
             'image': i.get('previewImage', ''),
             'keywords': i['keyword'].split(),
             'username': i['username'],
             'date': __format_date(i['addtime']),
             'description': i.get('description', ''),
             'gurl': i.get('gurl', ''),
            } for i in items]


def __format_date(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y')


def log(msg):
    print 'HWCLIPS.com scraper: %s' % msg
