# -*- coding: utf-8 -*-
"""
    Kodi helper functions for CHZZK addon
    SPDX-License-Identifier: GPL-3.0-only
"""

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_PATH = xbmcaddon.Addon().getAddonInfo('path')
ADDON_PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))


def get_setting(key, default=''):
    val = ADDON.getSetting(key)
    return val if val else default


def set_setting(key, value):
    ADDON.setSetting(key, str(value))


def get_string(string_id):
    return ADDON.getLocalizedString(string_id)


def log(message, level=xbmc.LOGDEBUG):
    xbmc.log(f'[{ADDON_ID}] {message}', level=level)


def notify(title, message, sound=True, icon=None):
    xbmcgui.Dialog().notification(title, message, icon or xbmcgui.NOTIFICATION_INFO, 5000, sound)


def show_ok_dialog(title, message):
    xbmcgui.Dialog().ok(title, message)


def show_yesno_dialog(title, message):
    return xbmcgui.Dialog().yesno(title, message)


def show_input_dialog(title, default='', hidden=False):
    return xbmcgui.Dialog().input(title, defaultt=default, option=xbmcgui.ALPHANUM_HIDE_INPUT if hidden else 0) or ''


def show_keyboard(default='', heading='', hidden=False):
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    return ''


def show_progress_dialog(title, message='', percent=0):
    dialog = xbmcgui.DialogProgress()
    dialog.create(title, message)
    if percent:
        dialog.update(percent)
    return dialog


def show_settings():
    ADDON.openSettings()


def get_handle():
    return int(sys.argv[1]) if len(sys.argv) > 1 else -1


def end_of_directory(handle, success=True, update_listing=False, cache_to_disc=True):
    xbmcplugin.endOfDirectory(handle, succeeded=success, updateListing=update_listing, cacheToDisc=cache_to_disc)


def add_directory_item(handle, item, is_folder=True, total_items=0):
    xbmcplugin.addDirectoryItem(handle=handle, url=item.getProperty('url') or '', listitem=item, isFolder=is_folder, totalItems=total_items)


def create_list_item(label, label2='', icon='', thumbnail='', fanart='', path='', is_playable=False, info=None, stream_info=None):
    li = xbmcgui.ListItem(label=label, label2=label2, path=path)
    li.setArt({
        'icon': icon or 'DefaultVideo.png',
        'thumb': thumbnail or 'DefaultVideo.png',
        'fanart': fanart or '',
    })
    if is_playable:
        li.setProperty('IsPlayable', 'true')
    if info:
        li.setInfo('video', info)
    if stream_info:
        for stream_type, stream_data in stream_info.items():
            li.addStreamInfo(stream_type, stream_data)
    return li


def add_video_item(handle, item_url, title, thumbnail='', icon='', fanart='', duration=0, info=None, is_playable=True, total_items=0):
    li = xbmcgui.ListItem(label=title, path=item_url)
    li.setArt({
        'icon': icon or 'DefaultVideo.png',
        'thumb': thumbnail or 'DefaultVideo.png',
        'fanart': fanart or '',
    })
    if is_playable:
        li.setProperty('IsPlayable', 'true')
    if info:
        li.setInfo('video', info)
    if duration:
        li.addStreamInfo('video', {'duration': duration})
    xbmcplugin.addDirectoryItem(handle=handle, url=item_url, listitem=li, isFolder=False, totalItems=total_items)


def add_folder_item(handle, title, url, thumbnail='', icon='', fanart='', info=None, total_items=0):
    li = xbmcgui.ListItem(label=title)
    li.setArt({
        'icon': icon or 'DefaultFolder.png',
        'thumb': thumbnail or 'DefaultFolder.png',
        'fanart': fanart or '',
    })
    if info:
        li.setInfo('video', info)
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True, totalItems=total_items)


def build_url(query, base_url=None):
    """Build a plugin URL with query parameters"""
    import sys
    if base_url is None:
        base_url = sys.argv[0]
    from urllib.parse import urlencode
    return f'{base_url}?{urlencode(query)}'


def parse_query(query_string):
    """Parse URL query parameters"""
    from urllib.parse import parse_qs
    return {k: v[0] if isinstance(v, list) and v else v for k, v in parse_qs(query_string.lstrip('?')).items()}


def set_content_type(handle, content='videos'):
    """Set the content type for the directory"""
    xbmcplugin.setContent(handle, content)


def add_sort_methods(handle):
    """Add common sort methods"""
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_PROGRAMMING)
