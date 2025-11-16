from reactpy import component, html, use_state
from .hooks.useAuth import use_auth
from .components.Header.Header import Header
from .components.Hero.Hero import Hero
from .components.PlaylistResult.PlaylistResult import PlaylistResult
from .components.MoodPage.MoodPage import MoodPage
from typing import Dict, Any


@component
def App():
    auth = use_auth()
    playlist_result, set_playlist_result = use_state({})
    processed_state, set_processed_state = use_state("")

    def handle_playlist_created(data: Dict[str, Any]):
        set_playlist_result(data)

    def handle_close_result():
        set_playlist_result({})


    is_authenticated = auth.get("is_authenticated", False)
    loading = auth.get("loading", False)

    async def handle_state_input(event):
        target = event.get("target", {}) if isinstance(event, dict) else {}
        state_value = target.get("value") if isinstance(target, dict) else None
        if not state_value or state_value == processed_state:
            return

        handle_callback_fn = auth.get("handle_callback")
        if not handle_callback_fn:
            return

        set_processed_state(state_value)
        try:
            await handle_callback_fn(state_value)
        except Exception as err:
            print(f"Erro ao processar callback de autenticação: {err}")

    auth_script = (
        "(function(){"
        "const params = new URLSearchParams(window.location.search);"
        "const state = params.get('state');"
        "const status = params.get('auth_status');"
        "if(state && status === 'success'){"
        "const input = document.getElementById('auth-state-input');"
        "if(input){"
        "input.value = state;"
        "input.dispatchEvent(new Event('input', { bubbles: true }));"
        "}"
        "const url = window.location.origin + window.location.pathname;"
        "window.history.replaceState({}, document.title, url);"
        "}"
        "})();"
    )

    main_content = (
        MoodPage(auth, handle_playlist_created)
        if is_authenticated
        else Hero(auth)
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
        html.input(
            {
                "type": "hidden",
                "id": "auth-state-input",
                "on_change": handle_state_input,
            }
        ),
        html.script({"type": "text/javascript"}, auth_script),
        html.div(
            {"class_name": "app-content"},
            (
                html.div({"class_name": "app-loading"}, html.p("Carregando..."))
                if loading and not is_authenticated
                else None
            ),
            main_content,
            (
                PlaylistResult(playlist_result, handle_close_result)
                if playlist_result and playlist_result.get("playlist_url")
                else None
            ),
        ),
    )

