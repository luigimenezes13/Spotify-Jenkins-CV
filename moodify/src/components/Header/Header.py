from reactpy import component, html, use_state
from ..Button.Button import Button
from typing import Dict, Any, Optional


@component
def Header(auth: Dict[str, Any]):
    is_authenticated = auth.get("is_authenticated", False)
    user_info = auth.get("user_info")
    loading = auth.get("loading", False)
    logout_fn = auth.get("logout")
    auth_url, set_auth_url = use_state("")

    async def handle_login(event):
        login_fn = auth.get("login")
        if login_fn:
            try:
                result = await login_fn()
                if result and result.get("redirect"):
                    redirect_url = result["redirect"]
                    set_auth_url(redirect_url)
            except Exception as e:
                print(f"Erro no login: {e}")


    if auth_url and auth_url != "":
        return html.div(
            html.script(
                {"type": "text/javascript"},
                f"(function(){{ setTimeout(function(){{ window.location.replace('{auth_url}'); }}, 100); }})();"
            ),
            html.p("Redirecionando para Spotify...")
        )

    def handle_logout(event):
        logout_fn = auth.get("logout")
        if logout_fn:
            logout_fn()

    return html.header(
        {"class_name": "header"},
        html.div(
            {"class_name": "header-container"},
            html.div(
                {"class_name": "header-logo"},
                html.h1("Moodify"),
            ),
            html.div(
                {"class_name": "header-actions"},
                (
                    html.div(
                        {"class_name": "user-info"},
                        html.span(f"Olá, {user_info.get('display_name', 'Usuário')}"),
                        Button(
                            on_click=handle_logout,
                            disabled=loading,
                            children="Logout",
                        ),
                    )
                    if is_authenticated
                    else Button(
                        on_click=handle_login,
                        disabled=loading,
                        children="Login com Spotify",
                    )
                ),
            ),
        ),
    )

