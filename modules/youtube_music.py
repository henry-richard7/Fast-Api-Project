from typing import Union
import requests


class YoutubeMusicApi:
    """
    A python class that makes use of Youtube's InnerTube API (Google's Internal API)
    to fetch songs from Youtube Music.
    """

    @classmethod
    def _parse_lyrics(cls, lyrics_id):
        """
        This fuction parses Lyrics form YouTube Music by its lyrics ID.

        params:
        @lyrics_id: The lyrics id of the song to parse lyrics.

        Note: This function is used for internal purpose only.
        """

        url = "https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        payload = {
            "context": {
                "client": {
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20220607.03.01",
                    "newVisitorCookie": True,
                },
                "user": {"lockedSafetyMode": False},
            },
            "browseId": lyrics_id,
        }
        response = requests.post(url, json=payload).json()

        try:
            parsed_lyrics = response["contents"]["sectionListRenderer"]["contents"][0][
                "musicDescriptionShelfRenderer"
            ]["description"]["runs"][0]["text"]
            return parsed_lyrics
        except:
            return None

    @classmethod
    def fetch_lyrics(cls, video_id):
        """
        This fuction fetches Lyrics for a song by its lyrics ID.

        params:
        @video_id: The video id of the song to fetch lyrics.
        """
        url = "https://www.youtube.com/youtubei/v1/next?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        payload = {
            "videoId": video_id,
            "context": {
                "user": {"lockedSafetyMode": False},
                "request": {"internalExperimentFlags": [], "useSsl": True},
                "client": {
                    "platform": "DESKTOP",
                    "hl": "en-GB",
                    "clientName": "WEB_REMIX",
                    "gl": "US",
                    "originalUrl": "https://music.youtube.com/",
                    "clientVersion": "1.20220607.03.01",
                },
            },
        }
        response = requests.post(url, json=payload).json()

        try:
            lyrics_id = response["contents"][
                "singleColumnMusicWatchNextResultsRenderer"
            ]["tabbedRenderer"]["watchNextTabbedResultsRenderer"]["tabs"][-2][
                "tabRenderer"
            ][
                "endpoint"
            ][
                "browseEndpoint"
            ][
                "browseId"
            ]

            parsed_lyrics = cls._parse_lyrics(lyrics_id)

            if parsed_lyrics:
                return {"success": True, "results": parsed_lyrics}
            else:
                return {"success": False, "results": "No results found."}
        except:
            return {"success": False, "results": "No results found."}

    def get_direct_link(self, video_id):
        """
        This function returns direct link for the provided video_id of a song.

        params:
        @video_id: The video id of the song to get direct link.
        """
        url = "https://www.youtube.com/youtubei/v1/player?key=AIzaSyBAETezhkwP0ZWA02RsqT1zu78Fpt0bC_s&prettyPrint=false"

        payload = {
            "videoId": video_id,
            "context": {
                "user": {"lockedSafetyMode": False},
                "request": {"internalExperimentFlags": [], "useSsl": True},
                "client": {
                    "platform": "MOBILE",
                    "hl": "en-GB",
                    "clientName": "ANDROID_MUSIC",
                    "gl": "US",
                    "originalUrl": "https://m.youtube.com/",
                    "clientVersion": "5.01",
                },
            },
        }
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, json=payload)

        try:
            result = response.json()["streamingData"]["adaptiveFormats"][-1]
            return {
                "success": True,
                "results": {
                    "url": result["url"],
                    "mimeType": result["mimeType"],
                    "bitrate": result["bitrate"],
                    "approxDurationMs": result["approxDurationMs"],
                },
            }

        except:
            return {"success": False, "results": "No results found."}

    def search_suggestions(self, query):
        url = "https://music.youtube.com/youtubei/v1/music/get_search_suggestions"
        params = {
            "key": "AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs",
        }

        body = {
            "context": {
                "client": {
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20230731.00.00",
                    "gl": "US",
                    "hl": "en-US",
                }
            },
            "input": query,
        }

        response = requests.post(url, json=body, params=params).json()
        suggestions = [
            x["searchSuggestionRenderer"]["navigationEndpoint"]["searchEndpoint"][
                "query"
            ]
            for x in response["contents"][0]["searchSuggestionsSectionRenderer"][
                "contents"
            ]
        ]
        return suggestions

    def search(self, query):
        """
        This function searchs the given song in YouTube Music.

        params:
        @query: The song name to search.
        """

        url = "https://www.youtube.com/youtubei/v1/search?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        payload = {
            "context": {
                "client": {
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20220607.03.01",
                    "newVisitorCookie": True,
                },
                "user": {"lockedSafetyMode": False},
            },
            "query": query,
            "params": "EgWKAQIIAWoIEAMQBRAKEAk=",
        }
        response = requests.post(url, json=payload).json()
        try:
            result = list()
            items = response["contents"]["tabbedSearchResultsRenderer"]["tabs"][0][
                "tabRenderer"
            ]["content"]["sectionListRenderer"]["contents"][0]["musicShelfRenderer"][
                "contents"
            ]

            for item in items:
                item = item["musicResponsiveListItemRenderer"]
                item_dict = dict()
                video_id = item["flexColumns"][0][
                    "musicResponsiveListItemFlexColumnRenderer"
                ]["text"]["runs"][0]["navigationEndpoint"]["watchEndpoint"]["videoId"]

                item_dict["video_id"] = video_id

                item_dict["song_name"] = item["flexColumns"][0][
                    "musicResponsiveListItemFlexColumnRenderer"
                ]["text"]["runs"][0]["text"]

                item_dict["artist_name"] = item["flexColumns"][1][
                    "musicResponsiveListItemFlexColumnRenderer"
                ]["text"]["runs"][0]["text"]

                item_dict["album_name"] = item["flexColumns"][1][
                    "musicResponsiveListItemFlexColumnRenderer"
                ]["text"]["runs"][-3]["text"]

                item_dict["art"] = item["thumbnail"]["musicThumbnailRenderer"][
                    "thumbnail"
                ]["thumbnails"][-1]["url"].replace("w120-h120", "w512-h512")

                result.append(item_dict)
            return {"success": True, "results": result}
        except:
            return {"success": False, "msg": "No results found."}

    def _process_meta_data(self, meta_data):
        result = dict()

        for datum in meta_data:
            if datum["musicResponsiveListItemFlexColumnRenderer"]["text"].get("runs"):
                runs = datum["musicResponsiveListItemFlexColumnRenderer"]["text"][
                    "runs"
                ][0]

                text_ = runs.get("text", {})
                navigation_endpoint = runs.get("navigationEndpoint", {})

                if navigation_endpoint.get("watchEndpoint"):
                    watch_endpoint = navigation_endpoint.get("watchEndpoint", {})

                    result["title"] = text_
                    result["song_id"] = watch_endpoint.get("videoId")
                    result["playlist_id"] = watch_endpoint.get("playlistId")
                    result["type"] = "song"

                else:
                    browse_endpoint = navigation_endpoint.get("browseEndpoint", {})

                    id_ = browse_endpoint.get("browseId", None)

                    page_type = (
                        browse_endpoint.get("browseEndpointContextSupportedConfigs", {})
                        .get("browseEndpointContextMusicConfig", {})
                        .get("pageType", None)
                    )
                    page_type = page_type.split("_")[-1].lower() if page_type else None

                    result[f"{page_type}_name"] = text_
                    result[f"{page_type}_id"] = id_

        return result

    def song(self, video_id):
        """
        This fuction fetches metadata for a song by its video ID.

        params:
        @video_id: The video id of the song to metadata.
        """
        url = "https://www.youtube.com/youtubei/v1/next?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        payload = {
            "videoId": video_id,
            "context": {
                "user": {"lockedSafetyMode": False},
                "request": {"internalExperimentFlags": [], "useSsl": True},
                "client": {
                    "platform": "DESKTOP",
                    "hl": "en-GB",
                    "clientName": "WEB_REMIX",
                    "gl": "US",
                    "originalUrl": "https://music.youtube.com/",
                    "clientVersion": "1.20220607.03.01",
                },
            },
        }
        response = requests.post(url, json=payload).json()

        playlistPanelVideoRenderer = response["contents"][
            "singleColumnMusicWatchNextResultsRenderer"
        ]["tabbedRenderer"]["watchNextTabbedResultsRenderer"]["tabs"][0]["tabRenderer"][
            "content"
        ][
            "musicQueueRenderer"
        ][
            "content"
        ][
            "playlistPanelRenderer"
        ][
            "contents"
        ][
            0
        ][
            "playlistPanelVideoRenderer"
        ]

        song_meta = {
            x["navigationEndpoint"]["browseEndpoint"][
                "browseEndpointContextSupportedConfigs"
            ]["browseEndpointContextMusicConfig"]["pageType"]
            .replace("MUSIC_PAGE_TYPE_", "")
            .lower()
            + "_name": x["text"]
            for x in playlistPanelVideoRenderer["longBylineText"]["runs"]
            if x.get("navigationEndpoint")
        }

        song_name = playlistPanelVideoRenderer["title"]["runs"][0]["text"]
        song_meta["song_name"] = song_name

        art = playlistPanelVideoRenderer["thumbnail"]["thumbnails"][-1]["url"]
        song_meta["art"] = art
        return song_meta

    def home(self, continuation=None, page="home", param_id=None) -> Union[list, dict]:
        """
        This returs a list of dict from YouTube Music Home if page = Home else it parsed data for given moods and genres param_id
        """
        url = "https://music.youtube.com/youtubei/v1/browse"
        params = {
            "key": "AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30",
            "alt": "json",
        }

        body = {
            "context": {
                "client": {
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20230731.00.00",
                    "gl": "US",
                    "hl": "en-US",
                }
            },
            "browseId": (
                "FEmusic_home"
                if page == "home "
                else "FEmusic_moods_and_genres_category"
            ),
            "visitorData": "Cgt6SUNYVzB2VkJDbyjGrrSmBg%3D%3D",
            "continuation": continuation,
            "params": param_id,
        }

        headers = {
            "x-goog-api-format-version": "1",
            "x-youtube-client-name": "WEB_REMIX",
            "x-youtube-client-version": "1.20230731.00.00",
            "x-origin": "https://music.youtube.com",
            "x-goog-visitor-id": "Cgt6SUNYVzB2VkJDbyjGrrSmBg%3D%3D",
            "referer": "https://music.youtube.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "accept": "application/json",
            "accept-charset": "UTF-8",
            "content-type": "application/json",
        }

        response = requests.post(url, json=body, params=params, headers=headers).json()
        continuation_token = None

        if page == "home":
            if continuation is None:
                continuation_token = (
                    response["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][
                        0
                    ]["tabRenderer"]["content"]["sectionListRenderer"]["continuations"][
                        0
                    ]
                    .get("nextContinuationData", {})
                    .get("continuation")
                )

            else:
                continuation_token = (
                    response["continuationContents"]["sectionListContinuation"]
                    .get("continuations", [{}])[0]
                    .get("nextContinuationData", {})
                    .get("continuation")
                )

        if continuation is None:
            tab_contents = response["contents"]["singleColumnBrowseResultsRenderer"][
                "tabs"
            ][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
        else:
            tab_contents = response["continuationContents"]["sectionListContinuation"][
                "contents"
            ]

        results = list()

        for tab in tab_contents:
            result_dict = dict()

            if tab.get("musicCarouselShelfRenderer"):
                header_name = tab["musicCarouselShelfRenderer"]["header"][
                    "musicCarouselShelfBasicHeaderRenderer"
                ]["title"]["runs"][0]["text"]
                result_dict[header_name] = list()
                for item in tab["musicCarouselShelfRenderer"]["contents"]:
                    item_dict = dict()

                    if item.get("musicResponsiveListItemRenderer"):
                        item_dict["thumbnail"] = item[
                            "musicResponsiveListItemRenderer"
                        ]["thumbnail"]["musicThumbnailRenderer"]["thumbnail"][
                            "thumbnails"
                        ][
                            -1
                        ][
                            "url"
                        ].replace(
                            "w120-h120", "w500-h500"
                        )

                        meta_data = item["musicResponsiveListItemRenderer"][
                            "flexColumns"
                        ]

                        item_dict.update(self._process_meta_data(meta_data))
                        result_dict[header_name].append(item_dict)

                    elif item.get("musicTwoRowItemRenderer"):
                        two_column_data = item["musicTwoRowItemRenderer"]

                        # Processing Thumbnail
                        two_column_thumbnail = (
                            two_column_data.get("thumbnailRenderer", {})
                            .get("musicThumbnailRenderer", {})
                            .get("thumbnail", {})
                            .get("thumbnails", [{}])[-1]
                            .get("url", None)
                        )

                        # Processing Title
                        two_column_song_name = (
                            two_column_data.get("title", {})
                            .get("runs", [{}])[0]
                            .get("text", None)
                        )

                        # Processing Artist Names
                        subtitle = two_column_data.get("subtitle", {}).get(
                            "runs", [{}]
                        )[0]
                        two_column_artist_name = subtitle["text"]

                        item_dict["thumbnail"] = two_column_thumbnail
                        item_dict["song_name"] = two_column_song_name
                        item_dict["artist_name"] = two_column_artist_name

                        # Processing Navigation Endpoint
                        two_column_navigation_endpoint = two_column_data.get(
                            "navigationEndpoint", {}
                        )

                        if two_column_navigation_endpoint.get("watchEndpoint"):
                            two_column_watch_endpoint = (
                                two_column_navigation_endpoint.get("watchEndpoint", {})
                            )

                            is_music_video = (
                                two_column_watch_endpoint.get(
                                    "watchEndpointMusicSupportedConfigs", {}
                                )
                                .get("watchEndpointMusicConfig")
                                .get("musicVideoType", False)
                            )

                            two_column_song_id = two_column_watch_endpoint.get(
                                "videoId", {}
                            )

                            item_dict["song_id"] = two_column_song_id
                            item_dict["is_music_video"] = (
                                True if is_music_video else False
                            )
                            item_dict["type"] = "song"

                        else:
                            two_column_browse_endpoint = (
                                two_column_navigation_endpoint.get("browseEndpoint", {})
                            )

                            two_column_id = two_column_browse_endpoint.get(
                                "browseId", None
                            )

                            two_column_page_type = (
                                two_column_browse_endpoint.get(
                                    "browseEndpointContextSupportedConfigs", {}
                                )
                                .get("browseEndpointContextMusicConfig", {})
                                .get("pageType", None)
                            )
                            two_column_page_type = two_column_page_type.split("_")[
                                -1
                            ].lower()

                            item_dict[f"{two_column_page_type}_id"] = two_column_id
                            item_dict["type"] = two_column_page_type

                        result_dict[header_name].append(item_dict)

                results.append(result_dict)

        if page == "home":
            return {"results": results, "continuation": continuation_token}
        else:
            return results

    def available_countries(self):
        countries = {
            "AR": "Argentina",
            "AT": "Austria",
            "AU": "Australia",
            "AZ": "Azerbaijan",
            "BA": "Bosnia and Herzegovina",
            "BD": "Bangladesh",
            "BE": "Belgium",
            "BG": "Bulgaria",
            "BH": "Bahrain",
            "BO": "Bolivia",
            "BR": "Brazil",
            "BY": "Belarus",
            "CA": "Canada",
            "CH": "Switzerland",
            "CL": "Chile",
            "CO": "Colombia",
            "CR": "Costa Rica",
            "CY": "Cyprus",
            "CZ": "Czech Republic",
            "DE": "Germany",
            "DK": "Denmark",
            "DO": "Dominican Republic",
            "DZ": "Algeria",
            "EC": "Ecuador",
            "EE": "Estonia",
            "EG": "Egypt",
            "ES": "Spain",
            "FI": "Finland",
            "FR": "France",
            "GB": "United Kingdom",
            "GE": "Georgia",
            "GH": "Ghana",
            "GR": "Greece",
            "GT": "Guatemala",
            "HK": "Hong Kong",
            "HN": "Honduras",
            "HR": "Croatia",
            "HU": "Hungary",
            "ID": "Indonesia",
            "IE": "Ireland",
            "IL": "Israel",
            "IN": "India",
            "IQ": "Iraq",
            "IS": "Iceland",
            "IT": "Italy",
            "JM": "Jamaica",
            "JO": "Jordan",
            "JP": "Japan",
            "KE": "Kenya",
            "KH": "Cambodia",
            "KR": "South Korea",
            "KW": "Kuwait",
            "KZ": "Kazakhstan",
            "LB": "Lebanon",
            "LI": "Liechtenstein",
            "LK": "Sri Lanka",
            "LT": "Lithuania",
            "LU": "Luxembourg",
            "LV": "Latvia",
            "LY": "Libyan Arab Jamahiriya",
            "MA": "Morocco",
            "MK": "Macedonia",
            "MT": "Malta",
            "MX": "Mexico",
            "MY": "Malaysia",
            "NG": "Nigeria",
            "NI": "Nicaragua",
            "NL": "Netherlands",
            "NO": "Norway",
            "NP": "Nepal",
            "NZ": "New Zealand",
            "OM": "Oman",
            "PA": "Panama",
            "PE": "Peru",
            "PG": "Papua New Guinea",
            "PH": "Philippines",
            "PK": "Pakistan",
            "PL": "Poland",
            "PR": "Puerto Rico",
            "PT": "Portugal",
            "PY": "Paraguay",
            "QA": "Qatar",
            "RO": "Romania",
            "RU": "Russian Federation",
            "SA": "Saudi Arabia",
            "AE": "United Arab Emirates",
            "SE": "Sweden",
            "SG": "Singapore",
            "SI": "Slovenia",
            "SK": "Slovakia",
            "SN": "Senegal",
            "SV": "El Salvador",
            "TH": "Thailand",
            "TN": "Tunisia",
            "TR": "Turkey",
            "TW": "Taiwan",
            "TZ": "Tanzania",
            "UA": "Ukraine",
            "UG": "Uganda",
            "US": "United States",
            "UY": "Uruguay",
            "VE": "Venezuela",
            "VN": "Viet Nam",
            "YE": "Yemen",
            "ZA": "South Africa",
        }

        return countries

    def charts(self, country_code="ZZ"):
        url = "https://music.youtube.com/youtubei/v1/browse"
        params = {
            "key": "AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30",
            "alt": "json",
        }
        body = {
            "context": {
                "client": {
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20230731.00.00",
                    "gl": "US",
                    "hl": "en-US",
                }
            },
            "browseId": "FEmusic_charts",
            "formData": {"selectedValues": [country_code]},
        }

        response = requests.post(url, json=body, params=params).json()

        top_songs = response["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][
            0
        ]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][1][
            "musicCarouselShelfRenderer"
        ][
            "contents"
        ]

        top_artists = response["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][
            0
        ]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][2][
            "musicCarouselShelfRenderer"
        ][
            "contents"
        ]

        top_songs_list = list()
        top_artists_list = list()

        for item in top_songs:
            thumbnail_music_video = item["musicTwoRowItemRenderer"][
                "thumbnailRenderer"
            ]["musicThumbnailRenderer"]["thumbnail"]["thumbnails"][-1]["url"]
            title_music_video = item["musicTwoRowItemRenderer"]["title"]["runs"][0][
                "text"
            ]
            artist_music_video = item["musicTwoRowItemRenderer"]["subtitle"]["runs"][0][
                "text"
            ]
            video_id_music_video = item["musicTwoRowItemRenderer"][
                "navigationEndpoint"
            ]["watchEndpoint"]["videoId"]
            playlist_id_music_video = item["musicTwoRowItemRenderer"][
                "navigationEndpoint"
            ]["watchEndpoint"]["playlistId"]
            music_video_type = item["musicTwoRowItemRenderer"]["navigationEndpoint"][
                "watchEndpoint"
            ]["watchEndpointMusicSupportedConfigs"]["watchEndpointMusicConfig"][
                "musicVideoType"
            ]

            top_songs_list.append(
                {
                    "thumbnail": thumbnail_music_video,
                    "title": title_music_video,
                    "artist": artist_music_video,
                    "video_id": video_id_music_video,
                    "playlist_id": playlist_id_music_video,
                    "music_video_type": music_video_type,
                }
            )

        for item in top_artists:
            artist = item["musicResponsiveListItemRenderer"]["flexColumns"][0][
                "musicResponsiveListItemFlexColumnRenderer"
            ]["text"]["runs"][0]["text"]
            thumbnail_artist = item["musicResponsiveListItemRenderer"]["thumbnail"][
                "musicThumbnailRenderer"
            ]["thumbnail"]["thumbnails"][-1]["url"].split("=")[0]
            total_subscribers = item["musicResponsiveListItemRenderer"]["flexColumns"][
                1
            ]["musicResponsiveListItemFlexColumnRenderer"]["text"]["runs"][0]["text"]
            artist_id = item["musicResponsiveListItemRenderer"]["navigationEndpoint"][
                "browseEndpoint"
            ]["browseId"]

            top_artists_list.append(
                {
                    "artist": artist,
                    "thumbnail": thumbnail_artist,
                    "total_subscribers": total_subscribers,
                    "artist_id": artist_id,
                }
            )

        return {"top_songs": top_songs_list, "top_artists": top_artists_list}

    def moods_and_genres(self):
        url = "https://music.youtube.com/youtubei/v1/browse"
        params = {
            "key": "AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30",
            "alt": "json",
        }
        headers = {
            "x-goog-api-format-version": "1",
            "x-youtube-client-name": "WEB_REMIX",
            "x-youtube-client-version": "1.20230731.00.00",
            "x-origin": "https://music.youtube.com",
            "x-goog-visitor-id": "Cgt6SUNYVzB2VkJDbyjGrrSmBg%3D%3D",
            "referer": "https://music.youtube.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "accept": "application/json",
            "accept-charset": "UTF-8",
            "content-type": "application/json",
        }
        body = {
            "context": {
                "client": {
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20230731.00.00",
                    "gl": "US",
                    "hl": "en-US",
                }
            },
            "browseId": "FEmusic_moods_and_genres",
        }

        response = requests.post(url, json=body, params=params, headers=headers).json()

        moods_list = list()
        languages_list = list()

        moods = response["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][0][
            "tabRenderer"
        ]["content"]["sectionListRenderer"]["contents"][0]["gridRenderer"]["items"]

        languages = response["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][
            0
        ]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][1][
            "gridRenderer"
        ][
            "items"
        ]

        for mood in moods:
            playlist_name_moods = mood["musicNavigationButtonRenderer"]["buttonText"][
                "runs"
            ][0]["text"]

            playlist_color_moods = int(
                mood["musicNavigationButtonRenderer"]["solid"]["leftStripeColor"]
            )
            playlist_color_moods = hex(playlist_color_moods)[4:]

            playlist_moods_params = mood["musicNavigationButtonRenderer"][
                "clickCommand"
            ]["browseEndpoint"]["params"]

            moods_list.append(
                {
                    "playlist_name": playlist_name_moods,
                    "playlist_color": playlist_color_moods,
                    "playlist_params": playlist_moods_params,
                }
            )

        for language in languages:
            playlist_name_languages = language["musicNavigationButtonRenderer"][
                "buttonText"
            ]["runs"][0]["text"]

            playlist_color_languages = int(
                language["musicNavigationButtonRenderer"]["solid"]["leftStripeColor"]
            )
            playlist_color_languages = hex(playlist_color_languages)[4:]

            playlist_languages_params = language["musicNavigationButtonRenderer"][
                "clickCommand"
            ]["browseEndpoint"]["params"]

            languages_list.append(
                {
                    "playlist_name": playlist_name_languages,
                    "playlist_color": playlist_color_languages,
                    "playlist_params": playlist_languages_params,
                }
            )

        return {"Moods and Moments": moods_list, "Genres": languages_list}
