from xbmcswift import Plugin, xbmc, xbmcplugin
import resources.lib.scraper as scraper

__ADDON_NAME__ = 'HWCLIPS.com'
__ADDON_ID__ = 'plugin.video.hwclips'

STRINGS = {'videos': 30000,
           'groups': 30001,
           'categories': 30002,
           'mostRecent': 30010,
           'topRated': 30011,
           'mostViewed': 30012}


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
    entries = scraper.get_root()
    items = [{'label': __translate(e['name']),
              'url': plugin.url_for('show_folder',
                                    folder=e['path']),
             } for e in entries]
    return plugin.add_items(items)


@plugin.route('/<folder>/')
def show_folder(folder):
    log('show_folder started with folder: %s' % folder)
    type, entries = scraper.get_folder(folder)
    if type == 'folders':
        return __add_folders(entries)
    elif type == 'videos':
        return __add_videos(entries)


@plugin.route('/video/<id>/')
def watch_video(id):
    video_url = ''  # fixme
    return plugin.set_resolved_url(video_url)


def __add_folders(entries):
    items = [{'label': e['name'],
              'thumbnail': e.get('image', 'DefaultFolder.png'),
              'info': {'plot': e['description']},
              'url': plugin.url_for('show_folder',
                                    folder=e['path']),
             } for e in entries]
    return plugin.add_items(items)


def __add_videos(entries):
    items = [{'label': e['name'],
              'thumbnail': e.get('image', 'DefaultVideo.png'),
              'info': {'originaltitle': e['name'],
                       'credits': e['username'],
                       'date': e['date'],
                       'genre': ', '.join(e['keywords']),
                       'plot': e['description']},
              'url': plugin.url_for('watch_video',
                                    id=e['id']),
              'is_folder': False,
              'is_playable': True,
             } for e in entries]
    return plugin.add_items(items, sort_method_ids=(3, 1))


def __translate(name):
    string_id = STRINGS.get(name)
    if string_id:
        return plugin.get_string(string_id)
    else:
        log('No translation for string: %s' % name)
        return name


def log(msg):
    xbmc.log('%s addon: %s' % (__ADDON_NAME__, msg))


if __name__ == '__main__':
    plugin.run()
