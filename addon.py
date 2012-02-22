from xbmcswift import Plugin, xbmc, xbmcplugin, xbmcgui
import resources.lib.scraper as scraper

__ADDON_NAME__ = 'HWCLIPS.com'
__ADDON_ID__ = 'plugin.video.hwclips'

STRINGS = {'videos': 30000,
           'groups': 30001,
           'categories': 30002,
           'mostRecent': 30010,
           'topRated': 30011,
           'mostViewed': 30012}

OVERLAYS = {'none': xbmcgui.ICON_OVERLAY_NONE,
            'hd': xbmcgui.ICON_OVERLAY_HD}


class Plugin_adv(Plugin):

    def add_items(self, iterable, sort_method_ids=[]):
        items = []
        urls = []
        for i, li_info in enumerate(iterable):
            items.append(self._make_listitem(**li_info))
            if self._mode in ['crawl', 'interactive', 'test']:
                print '[%d] %s%s%s (%s)' % (i + 1, '', li_info.get('label'),
                                            '', li_info.get('url'))
                urls.append(li_info.get('url'))
        if self._mode is 'xbmc':
            xbmcplugin.addDirectoryItems(self.handle, items, len(items))
            for id in sort_method_ids:
                xbmcplugin.addSortMethod(self.handle, id)
            xbmcplugin.endOfDirectory(self.handle)
        return urls


plugin = Plugin_adv(__ADDON_NAME__, __ADDON_ID__, __file__)


@plugin.route('/', default=True)
def show_root():
    log('show_root started')
    type, data = scraper.get_list()
    if type == scraper.API_RESPONSE_TYPE_FOLDERS:
        return __add_folders(data)
    else:
        raise


@plugin.route('/<path>/')
def show_folder(path):
    log('show_folder started with path: %s' % path)
    type, data = scraper.get_list(path)
    if type == scraper.API_RESPONSE_TYPE_FOLDERS:
        return __add_folders(data)
    elif type == scraper.API_RESPONSE_TYPE_VIDEOS:
        return __add_videos(data)
    else:
        raise


@plugin.route('/video/<id>/')
def watch_video(id):
    log('watch_video started with id: %s' % id)
    video = scraper.get_video(id)
    log('watch_video finished with video: %s' % video)
    return plugin.set_resolved_url(video['full_path'])


def __add_folders(entries):
    items = []
    for e in entries:
        title = __translate(e['name'])
        if int(e['count']):
            label = '%s (%d)' % (title, int(e['count']))
        else:
            label = title
        items.append({'label': label,
                      'thumbnail': e.get('image', 'DefaultFolder.png'),
                      'info': {'plot': e['description']},
                      'url': plugin.url_for('show_folder', path=e['path']),
                     })
    return plugin.add_items(items)


def __add_videos(entries):
    items = [{'label': e['name'],
              'thumbnail': e.get('image', 'DefaultVideo.png'),
              'info': {'originaltitle': e['name'],
                       'credits': e['username'],
                       'date': e['date'],
                       'genre': ', '.join(e['keywords']),
                       'plot': e['description'],
                       'rating': float(e['rating']),
                       'votes': e['votes'],
                       'views': e['views'],
                       'overlay': (OVERLAYS['hd'] if e['is_hd']
                                   else OVERLAYS['none']),
                       'duration': e['duration']},
              'url': plugin.url_for('watch_video',
                                    id=e['id']),
              'is_folder': False,
              'is_playable': True,
             } for e in entries]
    sort_methods = [xbmcplugin.SORT_METHOD_DATE,
                    xbmcplugin.SORT_METHOD_LABEL]
    return plugin.add_items(items, sort_method_ids=sort_methods)


def __translate(name):
    string_id = STRINGS.get(name)
    if string_id:
        return plugin.get_string(string_id)
    else:
        return name


def log(msg):
    xbmc.log(u'%s addon: %s' % (__ADDON_NAME__, msg))


if __name__ == '__main__':
    plugin.run()
