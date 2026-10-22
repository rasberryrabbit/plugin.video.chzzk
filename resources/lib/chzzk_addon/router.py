# -*- coding: utf-8 -*-
"""
    CHZZK addon main router
    SPDX-License-Identifier: GPL-3.0-only
"""

import sys
from .common.kodi import (
    log, get_setting, get_string, build_url, parse_query,
    set_content_type, add_sort_methods, end_of_directory,
    get_handle, show_ok_dialog, notify, get_string
)
from .api import ChzzkAPI

# Modes
MODE_MAIN = 'main'
MODE_RECOMMEND = 'recommend'
MODE_FOLLOWING = 'following'
MODE_SEARCH = 'search'
MODE_SEARCH_LIVES = 'search_lives'
MODE_SEARCH_CHANNELS = 'search_channels'
MODE_SEARCH_VIDEOS = 'search_videos'
MODE_CATEGORIES = 'categories'
MODE_CATEGORY_LIVES = 'category_lives'
MODE_CHANNEL = 'channel'
MODE_PLAY_LIVE = 'play_live'
MODE_PLAY_VIDEO = 'play_video'
MODE_PLAY_CLIP = 'play_clip'
MODE_SETTINGS = 'settings'


def get_api():
    """Get an authenticated ChzzkAPI instance"""
    nid_aut = get_setting('nid_aut', '')
    nid_ses = get_setting('nid_ses', '')
    return ChzzkAPI(nid_aut=nid_aut, nid_ses=nid_ses)


def main_route():
    """Main menu"""
    handle = get_handle()
    from .common.kodi import add_folder_item

    items = [
        (get_string(30201), MODE_RECOMMEND),  # 추천 라이브
        (get_string(30202), MODE_FOLLOWING),  # 팔로잉 라이브
        (get_string(30203), MODE_SEARCH),     # 검색
        (get_string(30204), MODE_CATEGORIES), # 카테고리
        (get_string(30205), MODE_SETTINGS),   # 설정
    ]

    for label, mode in items:
        url = build_url({'mode': mode})
        add_folder_item(handle, label, url)

    set_content_type(handle, 'videos')
    add_sort_methods(handle)
    end_of_directory(handle)


def recommend_route():
    """Show recommended live streams"""
    handle = get_handle()
    from .common.kodi import add_video_item, add_folder_item

    api = get_api()
    lives = api.get_recommend_lives()

    if not lives:
        # Some endpoints return dict with 'data' key
        if isinstance(lives, dict):
            lives = lives.get('data', [])
        else:
            lives = []

    for live in lives:
        live_info = live.get('live', live) if isinstance(live, dict) else {}
        channel = live.get('channel', {}) if isinstance(live, dict) else {}
        channel_id = channel.get('channelId', '')
        title = live_info.get('liveTitle', channel.get('channelName', 'Unknown'))
        thumbnail = live_info.get('liveImageUrl', '') or live.get('liveImageUrl', '')
        concurrent = live_info.get('concurrentUserCount', 0) or live.get('concurrentUserCount', 0)
        category = live_info.get('liveCategory', '') or live.get('liveCategory', '')

        info = {
            'title': title,
            'plot': f'카테고리: {category}\n시청자: {concurrent}명',
            'mediatype': 'video',
        }
        url = build_url({'mode': MODE_PLAY_LIVE, 'channel_id': channel_id})
        add_video_item(handle, url, title, thumbnail=thumbnail, info=info, is_playable=True)

    set_content_type(handle, 'videos')
    add_sort_methods(handle)
    end_of_directory(handle)


def following_route():
    """Show following live streams (requires auth)"""
    handle = get_handle()
    from .common.kodi import add_video_item

    if not get_setting('nid_aut') or not get_setting('nid_ses'):
        show_ok_dialog(get_string(30100), get_string(30101))
        from .common.kodi import show_settings
        show_settings()
        return

    api = get_api()
    lives = api.get_following_lives()

    for live in lives:
        channel = live.get('channel', {})
        channel_id = channel.get('channelId', '')
        title = live.get('liveTitle', channel.get('channelName', 'Unknown'))
        thumbnail = live.get('liveImageUrl', '')
        concurrent = live.get('concurrentUserCount', 0)

        info = {
            'title': title,
            'plot': f'시청자: {concurrent}명',
            'mediatype': 'video',
        }
        url = build_url({'mode': MODE_PLAY_LIVE, 'channel_id': channel_id})
        add_video_item(handle, url, title, thumbnail=thumbnail, info=info, is_playable=True)

    set_content_type(handle, 'videos')
    add_sort_methods(handle)
    end_of_directory(handle)


def search_route():
    """Search sub-menu"""
    handle = get_handle()
    from .common.kodi import add_folder_item

    items = [
        (get_string(30301), MODE_SEARCH_LIVES),     # 라이브 검색
        (get_string(30302), MODE_SEARCH_CHANNELS),  # 채널 검색
        (get_string(30303), MODE_SEARCH_VIDEOS),    # 다시보기 검색
    ]

    for label, mode in items:
        url = build_url({'mode': mode})
        add_folder_item(handle, label, url)

    set_content_type(handle, 'videos')
    end_of_directory(handle)


def search_lives_route():
    """Search live streams"""
    handle = get_handle()
    from .common.kodi import show_input_dialog, add_video_item

    query = show_input_dialog(get_string(30301))
    if not query:
        return

    api = get_api()
    lives = api.search_lives(query)

    for live in lives:
        channel = live.get('channel', {})
        channel_id = channel.get('channelId', '')
        title = live.get('liveTitle', channel.get('channelName', 'Unknown'))
        thumbnail = live.get('liveImageUrl', '')
        concurrent = live.get('concurrentUserCount', 0)

        info = {
            'title': title,
            'plot': f'시청자: {concurrent}명',
            'mediatype': 'video',
        }
        url = build_url({'mode': MODE_PLAY_LIVE, 'channel_id': channel_id})
        add_video_item(handle, url, title, thumbnail=thumbnail, info=info, is_playable=True)

    set_content_type(handle, 'videos')
    add_sort_methods(handle)
    end_of_directory(handle)


def search_channels_route():
    """Search channels"""
    handle = get_handle()
    from .common.kodi import show_input_dialog, add_folder_item

    query = show_input_dialog(get_string(30302))
    if not query:
        return

    api = get_api()
    channels = api.search_channels(query)

    for ch in channels:
        channel = ch.get('channel', ch) if isinstance(ch, dict) else {}
        channel_id = channel.get('channelId', '')
        name = channel.get('channelName', 'Unknown')
        verify = channel.get('verifiedMark', False)
        title = f'{name} ✓' if verify else name

        info = {
            'title': title,
            'mediatype': 'video',
        }
        url = build_url({'mode': MODE_CHANNEL, 'channel_id': channel_id})
        add_folder_item(handle, title, url, info=info)

    set_content_type(handle, 'videos')
    end_of_directory(handle)


def search_videos_route():
    """Search VODs"""
    handle = get_handle()
    from .common.kodi import show_input_dialog, add_video_item

    query = show_input_dialog(get_string(30303))
    if not query:
        return

    api = get_api()
    videos = api.search_videos(query)

    for v in videos:
        video_id = v.get('videoId', '') or v.get('id', '')
        title = v.get('videoTitle', 'Unknown')
        thumbnail = v.get('thumbnailImageUrl', '')
        duration = v.get('duration', 0)

        info = {
            'title': title,
            'duration': duration,
            'mediatype': 'video',
        }
        url = build_url({'mode': MODE_PLAY_VIDEO, 'video_id': video_id})
        add_video_item(handle, url, title, thumbnail=thumbnail, info=info, duration=duration, is_playable=True)

    set_content_type(handle, 'videos')
    add_sort_methods(handle)
    end_of_directory(handle)


def categories_route():
    """Show category list"""
    handle = get_handle()
    from .common.kodi import add_folder_item

    api = get_api()
    categories = api.get_categories()

    for cat in categories:
        cat_id = cat.get('categoryId', '')
        name = cat.get('categoryName', 'Unknown')
        icon = cat.get('categoryImageUrl', '')

        info = {'title': name, 'mediatype': 'video'}
        url = build_url({'mode': MODE_CATEGORY_LIVES, 'category_id': cat_id})
        add_folder_item(handle, name, url, thumbnail=icon, info=info)

    set_content_type(handle, 'videos')
    end_of_directory(handle)


def category_lives_route(category_id):
    """Show live streams in a category"""
    handle = get_handle()
    from .common.kodi import add_video_item

    api = get_api()
    lives = api.get_category_lives(category_id)

    for live in lives:
        channel = live.get('channel', {})
        channel_id = channel.get('channelId', '')
        title = live.get('liveTitle', channel.get('channelName', 'Unknown'))
        thumbnail = live.get('liveImageUrl', '')
        concurrent = live.get('concurrentUserCount', 0)

        info = {
            'title': title,
            'plot': f'시청자: {concurrent}명',
            'mediatype': 'video',
        }
        url = build_url({'mode': MODE_PLAY_LIVE, 'channel_id': channel_id})
        add_video_item(handle, url, title, thumbnail=thumbnail, info=info, is_playable=True)

    set_content_type(handle, 'videos')
    add_sort_methods(handle)
    end_of_directory(handle)


def channel_route(channel_id):
    """Show channel info and recent VODs"""
    handle = get_handle()
    from .common.kodi import add_video_item, add_folder_item

    api = get_api()
    # Check if live
    live_detail = api.get_live_detail(channel_id)

    if live_detail:
        live_id = live_detail.get('liveId', '')
        title = live_detail.get('liveTitle', 'Live')
        is_live = live_detail.get('status', '') == 'OPEN'
        thumbnail = live_detail.get('liveImageUrl', '')
        concurrent = live_detail.get('concurrentUserCount', 0)

        if is_live:
            info = {
                'title': f'[LIVE] {title}',
                'plot': f'시청자: {concurrent}명',
                'mediatype': 'video',
            }
            url = build_url({'mode': MODE_PLAY_LIVE, 'channel_id': channel_id})
            add_video_item(handle, url, f'[LIVE] {title}', thumbnail=thumbnail, info=info, is_playable=True)

    # TODO: Fetch channel VODs when API endpoint is confirmed
    # For now, just show live status
    set_content_type(handle, 'videos')
    end_of_directory(handle)


def play_live_route(channel_id):
    """Play a live stream"""
    handle = get_handle()
    import xbmcgui
    import requests
    from .api import extract_hls_url, add_bgda_to_segments

    api = get_api()
    live_detail = api.get_live_detail(channel_id)

    if not live_detail:
        show_ok_dialog(get_string(30401), get_string(30402))
        return

    status = live_detail.get('status', '')
    if status != 'OPEN':
        show_ok_dialog(get_string(30401), get_string(30403))
        return

    adult = live_detail.get('adult', False)
    if adult and not (get_setting('nid_aut') and get_setting('nid_ses')):
        show_ok_dialog(get_string(30401), get_string(30404))
        return

    # Get live playback JSON
    playback_json = live_detail.get('livePlaybackJson', '')
    m3u8_url, bgda_param = extract_hls_url(playback_json)

    if not m3u8_url:
        show_ok_dialog(get_string(30401), get_string(30405))
        return

    # Resolve the playlist
    resolved_url = m3u8_url

    # If we have bgda_param, we need to fetch and modify the m3u8 content
    # For HLS playback in Kodi, we can pass the master URL directly
    # The __bgda__ parameter is needed for segments, which Kodi's inputstream.adaptive may handle

    log(f'CHZZK: Playing live URL: {resolved_url}', level=xbmc.LOGINFO)

    item = xbmcgui.ListItem(path=resolved_url)
    item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    item.setProperty('inputstream.adaptive.use_session_id', 'true')

    # Try with inputstream.adaptive
    try:
        ia_addon = xbmcaddon.Addon('inputstream.adaptive')
        if ia_addon:
            item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    except RuntimeError:
        # inputstream.adaptive not available, use default HLS player
        pass

    xbmcplugin.setResolvedUrl(handle, True, item)


def play_video_route(video_id):
    """Play a VOD (replay)"""
    handle = get_handle()
    import xbmcgui
    from .api import get_vod_playback

    api = get_api()
    video = api.get_video(video_id)

    if not video:
        show_ok_dialog(get_string(30401), get_string(30406))
        return

    # Get VOD playback info
    in_key = video.get('inKey', '')
    vod_id = video.get('videoId', '') or video_id

    if not in_key:
        show_ok_dialog(get_string(30401), get_string(30407))
        return

    playback = get_vod_playback(vod_id, in_key, vod_id)
    if not playback:
        show_ok_dialog(get_string(30401), get_string(30408))
        return

    # Extract HLS URL from playback
    api_obj = api
    from .api import extract_hls_url
    m3u8_url, _ = extract_hls_url(playback)

    if not m3u8_url:
        show_ok_dialog(get_string(30401), get_string(30408))
        return

    item = xbmcgui.ListItem(path=m3u8_url)
    item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    try:
        xbmcaddon.Addon('inputstream.adaptive')
        item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    except RuntimeError:
        pass

    xbmcplugin.setResolvedUrl(handle, True, item)


def play_clip_route(clip_id):
    """Play a clip"""
    handle = get_handle()
    import xbmcgui
    from .api import get_clip_playback

    api = get_api()
    clip = api.get_clip(clip_id)

    if not clip:
        show_ok_dialog(get_string(30401), get_string(30409))
        return

    url = get_clip_playback(clip)

    if not url:
        show_ok_dialog(get_string(30401), get_string(30410))
        return

    item = xbmcgui.ListItem(path=url)
    item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    try:
        xbmcaddon.Addon('inputstream.adaptive')
        item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    except RuntimeError:
        pass

    xbmcplugin.setResolvedUrl(handle, True, item)


def settings_route():
    """Open settings"""
    from .common.kodi import show_settings
    show_settings()


def run(argv):
    """Main entry point"""
    handle = int(argv[1]) if len(argv) > 1 else -1
    query_string = argv[2] if len(argv) > 2 else ''
    queries = parse_query(query_string)

    mode = queries.get('mode', MODE_MAIN)
    log(f'CHZZK router: mode={mode}, queries={queries}', level=xbmc.LOGDEBUG)

    import xbmcaddon  # for play routes

    if mode == MODE_MAIN:
        main_route()
    elif mode == MODE_RECOMMEND:
        recommend_route()
    elif mode == MODE_FOLLOWING:
        following_route()
    elif mode == MODE_SEARCH:
        search_route()
    elif mode == MODE_SEARCH_LIVES:
        search_lives_route()
    elif mode == MODE_SEARCH_CHANNELS:
        search_channels_route()
    elif mode == MODE_SEARCH_VIDEOS:
        search_videos_route()
    elif mode == MODE_CATEGORIES:
        categories_route()
    elif mode == MODE_CATEGORY_LIVES:
        category_lives_route(queries.get('category_id', ''))
    elif mode == MODE_CHANNEL:
        channel_route(queries.get('channel_id', ''))
    elif mode == MODE_PLAY_LIVE:
        play_live_route(queries.get('channel_id', ''))
    elif mode == MODE_PLAY_VIDEO:
        play_video_route(queries.get('video_id', ''))
    elif mode == MODE_PLAY_CLIP:
        play_clip_route(queries.get('clip_id', ''))
    elif mode == MODE_SETTINGS:
        settings_route()
    else:
        main_route()
