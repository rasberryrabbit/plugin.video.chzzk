# -*- coding: utf-8 -*-
"""
    CHZZK API Client
    Handles all API calls to chzzk.naver.com
    Based on streamlink chzzk plugin API endpoints.

    SPDX-License-Identifier: GPL-3.0-only
"""

import json
import requests
from urllib.parse import urlparse, parse_qsl

# API endpoints (discovered from streamlink chzzk plugin)
API_BASE = 'https://api.chzzk.naver.com/service'
API_VOD_PLAYBACK = 'https://apis.naver.com/neonplayer/vodplay/v2/playback'

CHANNELS_LIVE_DETAIL = API_BASE + '/v2/channels/{channel_id}/live-detail'
CHANNELS_LIVE_PLAYBACK = API_BASE + '/v1/channels/{channel_id}/live-playback-json'
VIDEOS_URL = API_BASE + '/v2/videos/{video_id}'
CLIP_URL = API_BASE + '/v1/play-info/clip/{clip_id}'

# Search and category endpoints
SEARCH_LIVES = API_BASE + '/v1/search/lives?q={query}&offset=0&size=20'
SEARCH_CHANNELS = API_BASE + '/v1/search/channels?q={query}&offset=0&size=20'
SEARCH_VIDEOS = API_BASE + '/v1/search/videos?q={query}&offset=0&size=20'

# Recommend / categories
RECOMMEND_LIVES = API_BASE + '/v1/recommendations/LIVE'
CATEGORIES_URL = API_BASE + '/v1/categories'
CATEGORY_LIVES = API_BASE + '/v1/categories/{category_id}/lives?offset=0&size=20'

# Following (requires auth)
FOLLOWING_LIVES = API_BASE + '/v2/followings/lives'

# Default headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Origin': 'https://chzzk.naver.com',
    'Referer': 'https://chzzk.naver.com/',
}

TIMEOUT = 15


class ChzzkAPI:
    """CHZZK API client"""

    def __init__(self, nid_aut='', nid_ses=''):
        self.nid_aut = nid_aut
        self.nid_ses = nid_ses

    @property
    def cookies(self):
        """Build cookies dict from credentials"""
        cookies = {}
        if self.nid_aut:
            cookies['NID_AUT'] = self.nid_aut
        if self.nid_ses:
            cookies['NID_SES'] = self.nid_ses
        return cookies

    @property
    def headers(self):
        h = DEFAULT_HEADERS.copy()
        return h

    def _get(self, url, params=None):
        """Make a GET request to the API"""
        try:
            r = requests.get(
                url,
                headers=self.headers,
                cookies=self.cookies,
                params=params,
                timeout=TIMEOUT
            )
            if r.status_code == 200:
                return r.json() if r.content else None
            return None
        except Exception:
            return None

    def get_live_detail(self, channel_id):
        """Get live stream details including playback info"""
        url = CHANNELS_LIVE_DETAIL.format(channel_id=channel_id)
        data = self._get(url)
        if not data or 'content' not in data:
            return None
        return data['content']

    def get_live_playback(self, channel_id):
        """Get live playback JSON (alternative endpoint)"""
        url = CHANNELS_LIVE_PLAYBACK.format(channel_id=channel_id)
        return self._get(url)

    def get_video(self, video_id):
        """Get VOD video info"""
        url = VIDEOS_URL.format(video_id=video_id)
        data = self._get(url)
        if not data or 'content' not in data:
            return None
        return data['content']

    def get_clip(self, clip_id):
        """Get clip info"""
        url = CLIP_URL.format(clip_id=clip_id)
        data = self._get(url)
        if not data or 'content' not in data:
            return None
        return data['content']

    def search_lives(self, query, size=20):
        """Search for live streams"""
        url = SEARCH_LIVES.format(query=query)
        url = url.replace('size=20', f'size={size}')
        data = self._get(url)
        if not data or 'content' not in data:
            return []
        return data['content'].get('data', []) or []

    def search_channels(self, query, size=20):
        """Search for channels"""
        url = SEARCH_CHANNELS.format(query=query)
        url = url.replace('size=20', f'size={size}')
        data = self._get(url)
        if not data or 'content' not in data:
            return []
        return data['content'].get('data', []) or []

    def search_videos(self, query, size=20):
        """Search for VODs"""
        url = SEARCH_VIDEOS.format(query=query)
        url = url.replace('size=20', f'size={size}')
        data = self._get(url)
        if not data or 'content' not in data:
            return []
        return data['content'].get('data', []) or []

    def get_recommend_lives(self):
        """Get recommended live streams"""
        data = self._get(RECOMMEND_LIVES)
        if not data or 'content' not in data:
            return []
        return data['content'] or []

    def get_categories(self):
        """Get category list"""
        data = self._get(CATEGORIES_URL)
        if not data or 'content' not in data:
            return []
        return data['content'] or []

    def get_category_lives(self, category_id):
        """Get live streams by category"""
        url = CATEGORY_LIVES.format(category_id=category_id)
        data = self._get(url)
        if not data or 'content' not in data:
            return []
        return data['content'].get('data', []) or []

    def get_following_lives(self):
        """Get followed channels' live streams (requires auth)"""
        if not self.nid_aut or not self.nid_ses:
            return []
        data = self._get(FOLLOWING_LIVES)
        if not data or 'content' not in data:
            return []
        return data['content'] or []


def extract_hls_url(live_playback_json):
    """
    Extract HLS m3u8 URL from live playback JSON.
    Returns (m3u8_url, bgda_param) tuple.
    """
    if not live_playback_json:
        return None, None

    # Parse the JSON if it's a string
    if isinstance(live_playback_json, str):
        try:
            data = json.loads(live_playback_json)
        except json.JSONDecodeError:
            return None, None
    else:
        data = live_playback_json

    # Find HLS media
    media_list = data.get('media', []) or []
    for media in media_list:
        if media.get('mediaId') == 'HLS' and media.get('protocol') == 'HLS':
            media_path = media.get('path', '')
            if not media_path:
                continue
            # Extract bgnts (hdnts) parameter for __bgda__ signing
            parsed = urlparse(media_path)
            params = dict(parse_qsl(parsed.query))
            bgda_param = params.get('hdnts', '')
            return media_path, bgda_param

    return None, None


def add_bgda_to_segments(m3u8_content, bgda_param):
    """
    Modify m3u8 content to add __bgda__ parameter to segment URLs.
    This is required for the stream to play correctly.
    """
    if not bgda_param:
        return m3u8_content

    lines = m3u8_content.split('\n')
    new_lines = []
    for line in lines:
        # Add __bgda__ param to .m4v and .aac segment URLs
        if (line.endswith('.m4v') or line.endswith('.aac') or '.m4v?' in line or '.aac?' in line) and '__bgda__' not in line:
            if '?' in line:
                line = line + '&__bgda__=' + bgda_param
            else:
                line = line + '?__bgda__=' + bgda_param
        new_lines.append(line)
    return '\n'.join(new_lines)


def get_vod_playback(video_id, in_key, vod_id):
    """
    Get VOD playback URL.
    Returns the master m3u8 URL.
    """
    url = API_VOD_PLAYBACK + '/{video_id}?key={in_key}'.format(
        video_id=vod_id, in_key=in_key
    )
    try:
        r = requests.get(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def get_clip_playback(clip_data):
    """
    Get clip playback URL from clip info.
    """
    if not clip_data:
        return None
    # Clip data usually has playback info embedded
    playback = clip_data.get('playback', {}) or {}
    if not playback:
        # Try alternative field
        playback = clip_data.get('vodInfo', {}) or {}

    media_list = playback.get('media', []) or []
    for media in media_list:
        if media.get('mediaId') == 'HLS' or media.get('protocol') == 'HLS':
            return media.get('path', '')

    # Fallback: direct URL
    return clip_data.get('clipPlayUrl') or clip_data.get('playUrl')
