from reactpy import component, html
from ..Button.Button import Button
from typing import Dict, Any, Optional


@component
def PlaylistResult(playlist_data: Optional[Dict[str, Any]], on_close):
    if not playlist_data or not playlist_data.get("playlist_url"):
        return None

    playlist_url = playlist_data.get("playlist_url", "")
    tracks = playlist_data.get("tracks", [])


    def handle_close(event):
        if on_close:
            on_close()

    return html.section(
        {"class_name": "playlist-result"},
        html.div(
            {"class_name": "playlist-result-container"},
            html.div(
                {"class_name": "playlist-result-header"},
                html.h2("Playlist criada com sucesso!"),
                Button(
                    on_click=handle_close,
                    variant="secondary",
                    children="Fechar",
                ),
            ),
            html.div(
                {"class_name": "playlist-result-content"},
                html.p(
                    {"class_name": "playlist-url"},
                    html.a(
                        {"href": playlist_url, "target": "_blank"},
                        playlist_url,
                    ),
                ),
                html.div(
                    {"class_name": "playlist-tracks"},
                    html.h3("Músicas adicionadas:"),
                    html.ul(
                        *[
                            html.li(
                                {"key": track.get("id", idx)},
                                html.span(
                                    {"class_name": "track-name"},
                                    track.get("name", "Unknown"),
                                ),
                                html.span(
                                    {"class_name": "track-artists"},
                                    ", ".join(track.get("artists", [])),
                                ),
                            )
                            for idx, track in enumerate(tracks[:10])
                        ],
                    ),
                    (
                        html.p(
                            {"class_name": "tracks-more"},
                            f"E mais {len(tracks) - 10} músicas...",
                        )
                        if len(tracks) > 10
                        else None
                    ),
                ),
                html.a(
                    {
                        "href": playlist_url,
                        "target": "_blank",
                        "rel": "noopener noreferrer",
                        "class_name": "btn btn-primary",
                    },
                    "Abrir no Spotify",
                ),
            ),
        ),
    )

