import simplejson
import urllib2
from datetime import datetime

API_URL = 'http://www.hardwareclips.com/api/xbmc/'

USER_AGENT = 'XBMC Addon: plugin.video.hwclips'

DEBUG = True

API_RESPONSE_TYPE_FOLDERS = u'folders'
API_RESPONSE_TYPE_VIDEOS = u'videos'
API_RESPONSE_TYPE_VIDEO = u'videoDetail'
API_RESPONSE_TYPE_ERROR = u'error'


def get_list(path=None):
    if not path:
        path = 'root'
    log('get_list started with path: %s' % path)
    type, items = __api_request(path)
    if type == API_RESPONSE_TYPE_FOLDERS:
        entries = __format_folders(items)
    elif type == API_RESPONSE_TYPE_VIDEOS:
        entries = __format_videos(items)
    else:
        raise
    log('get_list finished with %d entries' % len(entries))
    return type, entries


def get_video(video_id):
    log('get_list started with video_id: %s' % video_id)
    path = 'video/%d' % int(video_id)
    type, items = __api_request(path)
    if type == API_RESPONSE_TYPE_VIDEO:
        entry = __format_video(items)
    elif type == API_RESPONSE_TYPE_ERROR:
        raise
    else:
        raise
    log('get_list finished')
    return entry


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
    data = json[type]
    if DEBUG:
        log('DEBUG: type: %s' % type)
        if isinstance(data, list):
            log('DEBUG: list: %s' % simplejson.dumps(data[0], indent=1))
        else:
            log('DEBUG: item: %s' % simplejson.dumps(data, indent=1))
    log('__api_request finished with type: %s' % type)
    return type, data


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
             'views': i.get('views', '0'),
             'votes': i.get('ratingCount', '0'),
             'rating': i.get('averageRating', '0.0'),
             'is_hd': i.get('isHD', False),
             'duration': __format_duration(i.get('duration', '0.0')),
            } for i in items]


def __format_video(item):
    return {'full_path': item['filePath']}


def __format_date(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y')


def __format_duration(duration):
    seconds = int(float(duration))
    minutes = seconds // 60
    seconds %= 60
    return '%02i:%02i' % (minutes, seconds)


def log(msg):
    print 'HWCLIPS.com scraper: %s' % msg
