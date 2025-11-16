from reactpy import component, html, use_state
from ..Button.Button import Button
from typing import Dict, Any
import json


@component
def Hero(auth: Dict[str, Any]):
    is_authenticated = auth.get("is_authenticated", False)
    login_fn = auth.get("login")
    loading = auth.get("loading", False)
    auth_url, set_auth_url = use_state("")

    async def handle_cta(event):
        if not is_authenticated and login_fn:
            try:
                result = await login_fn()
                if result and result.get("redirect"):
                    redirect_url = result["redirect"]
                    set_auth_url(redirect_url)
            except Exception as e:
                print(f"Erro no login: {e}")


    if auth_url and auth_url != "":
        script_content = (
            "(function(){"
            f"var url = {json.dumps(auth_url)};"
            "window.location.href = url;"
            "})();"
        )

        return html.div(
            {"class_name": "auth-redirect"},
            html.p("Abrindo autenticação do Spotify..."),
            html.script(
                {"type": "text/javascript"},
                script_content,
            ),
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

