from reactpy import component, html, use_state
from ..Button.Button import Button
from ...services.api import api_client
from typing import Dict, Any, Optional, Callable


MOODS = [
    {"id": "happy", "label": "Feliz", "emoji": "😊", "description": "Músicas alegres e dançantes"},
    {"id": "sad", "label": "Triste", "emoji": "😢", "description": "Músicas melancólicas e emotivas"},
    {"id": "angry", "label": "Raiva", "emoji": "😠", "description": "Músicas com alta energia"},
    {"id": "neutral", "label": "Neutro", "emoji": "😐", "description": "Músicas equilibradas"},
    {"id": "surprise", "label": "Surpresa", "emoji": "😲", "description": "Músicas energéticas e variadas"},
    {"id": "fear", "label": "Medo", "emoji": "😨", "description": "Músicas tensas e atmosféricas"},
    {"id": "disgust", "label": "Nojo", "emoji": "🤢", "description": "Músicas calmas e melancólicas"},
]


@component
def MoodSelector(auth: Dict[str, Any], on_playlist_created: Callable):
    selected_mood, set_selected_mood = use_state("")
    creating, set_creating = use_state(False)
    error, set_error = use_state("")
    state_token = auth.get("state_token")

    async def handle_create_playlist(event):
        if not selected_mood or not state_token:
            set_error("Selecione um mood primeiro")
            return

        set_creating(True)
        set_error("")

        try:
            response = await api_client.create_playlist(selected_mood, state_token)
            if response.get("success"):
                on_playlist_created(response["data"])
            else:
                set_error("Erro ao criar playlist")
        except Exception as e:
            set_error(f"Erro: {str(e)}")
        finally:
            set_creating(False)

    def handle_mood_select(mood_id: str):
        set_selected_mood(mood_id)
        set_error("")

    return html.section(
        {"class_name": "mood-selector"},
        html.div(
            {"class_name": "mood-selector-container"},
            html.h2(
                {"class_name": "mood-selector-title"},
                "Como você está se sentindo?",
            ),
            html.div(
                {"class_name": "moods-grid"},
                *[
                    html.button(
                        {
                            "key": mood["id"],
                            "class_name": f"mood-card {'mood-selected' if selected_mood == mood['id'] else ''}",
                            "on_click": lambda e, mid=mood["id"]: handle_mood_select(mid),
                        },
                        html.span({"class_name": "mood-emoji"}, mood["emoji"]),
                        html.span({"class_name": "mood-label"}, mood["label"]),
                        html.span({"class_name": "mood-description"}, mood["description"]),
                    )
                    for mood in MOODS
                ],
            ),
            html.div(
                {"class_name": "mood-actions"},
                (
                    html.div({"class_name": "error-message"}, error)
                    if error and error != ""
                    else None
                ),
                Button(
                    on_click=handle_create_playlist,
                    disabled=not selected_mood or creating or not state_token,
                    variant="primary",
                    children="Criar Playlist" if not creating else "Criando...",
                ),
            ),
        ),
    )

