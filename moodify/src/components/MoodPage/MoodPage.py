from reactpy import component, html, use_state
from typing import Dict, Any, Callable, Optional, List
from ...services.api import api_client
from ...services.MoodDetector import mood_detector

MOOD_OPTIONS: List[Dict[str, str]] = [
    {"value": "happy", "label": "Feliz", "description": "Energético, dançante e alto astral."},
    {"value": "sad", "label": "Triste", "description": "Melódico e introspectivo."},
    {"value": "angry", "label": "Bravo", "description": "Riffs pesados e muita energia."},
    {"value": "neutral", "label": "Neutro", "description": "Equilíbrio perfeito para o dia a dia."},
    {"value": "surprise", "label": "Surpreso", "description": "Mistura imprevisível de estilos."},
    {"value": "fear", "label": "Tenso", "description": "Atmosferas densas e misteriosas."},
    {"value": "disgust", "label": "Desgosto", "description": "Texturas experimentais e climáticas."},
]


@component
def MoodPage(
    auth: Dict[str, Any],
    on_playlist_created: Optional[Callable[[Dict[str, Any]], None]] = None,
):
    default_mood = MOOD_OPTIONS[0]["value"]
    selected_mood, set_selected_mood = use_state(default_mood)
    submitting, set_submitting = use_state(False)
    error_message, set_error_message = use_state("")
    success_message, set_success_message = use_state("")

    state_token = auth.get("state_token", "")
    user_info = auth.get("user_info", {})

    def handle_select_change(event):
        target = event.get("target", {}) if isinstance(event, dict) else {}
        value = target.get("value")
        if value:
            set_selected_mood(value)
            set_success_message("")
            set_error_message("")

    async def handle_detect_mood(event):
        set_error_message("")
        set_success_message("")
        
        try:
            detected = mood_detector.open_camera_and_detect()
            if detected:
                set_selected_mood(detected)
                set_success_message(f"Mood detectado com sucesso!")
        except Exception as e:
            set_error_message(f"Erro na câmera: {str(e)}")

    async def handle_submit(event):
        if not state_token:
            set_error_message("Sessão expirada. Faça login novamente.")
            return

        set_submitting(True)
        set_error_message("")
        set_success_message("")

        try:
            response = await api_client.create_playlist(selected_mood, state_token)
            if response.get("success") and response.get("data"):
                set_success_message("Playlist criada com sucesso! Confira abaixo.")
                if on_playlist_created:
                    on_playlist_created(response["data"])
            else:
                set_error_message(response.get("message", "Não foi possível criar a playlist."))
        except Exception as exc:
            set_error_message(f"Erro ao criar playlist: {exc}")
        finally:
            set_submitting(False)

    return html.section(
        {"class_name": "mood-page"},
        html.div(
            {"class_name": "mood-page__header"},
            html.h2(f"Olá, {user_info.get('display_name', 'Moodifier')}!"),
            html.p("Escolha o mood do momento para receber uma playlist feita sob medida."),
        ),
        html.div(
            {"class_name": "mood-page__selector"},
            html.button(
                {
                    "class_name": "btn btn-secondary",
                    "on_click": handle_detect_mood,
                    "disabled": submitting,
                    "style": {"margin-bottom": "1rem", "width": "100%"}
                },
                "📷 Detectar Emoção com Câmera"
            ),
            html.label({"for": "mood-selector"}, "Selecione um mood"),
            html.select(
                {
                    "id": "mood-selector",
                    "value": selected_mood,
                    "on_change": handle_select_change,
                    "disabled": submitting,
                },
                *[
                    html.option({"value": option["value"]}, option["label"])
                    for option in MOOD_OPTIONS
                ],
            ),
            html.button(
                {
                    "class_name": "btn btn-primary",
                    "on_click": handle_submit,
                    "disabled": submitting or not selected_mood,
                },
                "Criar playlist" if not submitting else "Criando...",
            ),
        ),
        html.ul(
            {"class_name": "mood-page__descriptions"},
            *[
                html.li(
                    {"class_name": "mood-page__description-item"},
                    html.strong(option["label"]),
                    html.span(f" — {option['description']}"),
                )
                for option in MOOD_OPTIONS
            ],
        ),
        (
            html.p({"class_name": "mood-page__success"}, success_message)
            if success_message
            else None
        ),
        (
            html.p({"class_name": "mood-page__error"}, error_message)
            if error_message
            else None
        ),
    )

