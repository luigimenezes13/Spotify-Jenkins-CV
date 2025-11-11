from reactpy import component, html, use_state, use_effect
from .hooks.useAuth import use_auth
from .components.Header.Header import Header
from .components.Hero.Hero import Hero
from .components.MoodSelector.MoodSelector import MoodSelector
from .components.PlaylistResult.PlaylistResult import PlaylistResult
from typing import Optional, Dict, Any


@component
def App():
    auth = use_auth()
    playlist_result, set_playlist_result = use_state({})

    def handle_playlist_created(data: Dict[str, Any]):
        set_playlist_result(data)

    def handle_close_result():
        set_playlist_result({})


    is_authenticated = auth.get("is_authenticated", False)
    loading = auth.get("loading", False)

    if loading and not is_authenticated:
        return html.div(
            {"class_name": "app-loading"},
            html.p("Carregando..."),
        )

    return html.div(
        {"class_name": "app"},
        html.link(
            {
                "rel": "stylesheet",
                "href": "/static/css/styles.css",
            }
        ),
        Header(auth),
        (
            html.div(
                {"class_name": "app-content"},
                Hero(auth),
                (
                    MoodSelector(auth, handle_playlist_created)
                    if is_authenticated
                    else None
                ),
                (
                    PlaylistResult(playlist_result, handle_close_result)
                    if playlist_result and playlist_result.get("playlist_url")
                    else None
                ),
            )
        ),
    )

