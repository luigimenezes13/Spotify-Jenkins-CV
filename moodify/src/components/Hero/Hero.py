from reactpy import component, html, use_state
from ..Button.Button import Button
from typing import Dict, Any
import asyncio


@component
def Hero(auth: Dict[str, Any]):
    is_authenticated = auth.get("is_authenticated", False)
    login_fn = auth.get("login")
    loading = auth.get("loading", False)
    auth_url, set_auth_url = use_state("")

    def handle_cta(event):
        if not is_authenticated and login_fn:
            async def do_login():
                try:
                    result = await login_fn()
                    if result and result.get("redirect"):
                        redirect_url = result["redirect"]
                        set_auth_url(redirect_url)
                except Exception as e:
                    print(f"Erro no login: {e}")
            
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(do_login())
                else:
                    loop.run_until_complete(do_login())
            except RuntimeError:
                asyncio.create_task(do_login())


    if auth_url and auth_url != "":
        return html.div(
            html.script(
                {"type": "text/javascript"},
                f"(function(){{ setTimeout(function(){{ window.location.replace('{auth_url}'); }}, 100); }})();"
            ),
            html.p("Redirecionando para Spotify...")
        )

    return html.section(
        {"class_name": "hero"},
        html.div(
            {"class_name": "hero-container"},
            html.h1(
                {"class_name": "hero-title"},
                "Crie playlists perfeitas baseadas no seu mood",
            ),
            html.p(
                {"class_name": "hero-description"},
                "Conecte-se com o Spotify e deixe que a música acompanhe suas emoções. "
                "Crie playlists personalizadas com apenas um clique.",
            ),
            (
                html.div(
                    {"class_name": "hero-cta"},
                    html.p(
                        {"class_name": "hero-subtitle"},
                        "Selecione um mood abaixo para começar",
                    ),
                )
                if is_authenticated
                else Button(
                    on_click=handle_cta,
                    disabled=loading,
                    variant="primary",
                    children="Começar agora",
                )
            ),
        ),
    )

