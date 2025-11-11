from reactpy import use_state
from typing import Optional, Dict, Any
from ..services.api import api_client


def use_auth():
    state_token, set_state_token = use_state("")
    user_info, set_user_info = use_state({})
    is_authenticated, set_is_authenticated = use_state(False)
    loading, set_loading = use_state(False)
    error, set_error = use_state("")

    stored_state_value = None

    def get_stored_state() -> Optional[str]:
        return stored_state_value

    def store_state(state: str):
        nonlocal stored_state_value
        stored_state_value = state

    def clear_state():
        nonlocal stored_state_value
        stored_state_value = None

    async def check_auth_status():
        stored_state = get_stored_state()
        if not stored_state:
            set_is_authenticated(False)
            set_user_info({})
            return

        set_loading(True)
        set_error("")
        try:
            response = await api_client.get_auth_status(stored_state)
            if response.get("success") and response.get("data", {}).get("authenticated"):
                set_is_authenticated(True)
                set_user_info(response["data"])
                set_state_token(stored_state)
            else:
                set_is_authenticated(False)
                set_user_info({})
                clear_state()
        except Exception as e:
            set_error(str(e))
            set_is_authenticated(False)
            set_user_info({})
        finally:
            set_loading(False)

    async def login():
        set_loading(True)
        set_error("")
        try:
            response = await api_client.login()
            if response.get("success"):
                auth_url = response["data"]["auth_url"]
                state = response["data"]["state"]
                store_state(state)
                set_state_token(state)
                set_loading(False)
                return {"redirect": auth_url}
            else:
                set_error("Erro ao obter URL de login")
                set_loading(False)
        except Exception as e:
            set_error(str(e))
            set_loading(False)
            return None

    async def logout():
        if not state_token:
            return

        set_loading(True)
        set_error("")
        try:
            await api_client.logout(state_token)
            clear_state()
            set_state_token("")
            set_user_info({})
            set_is_authenticated(False)
        except Exception as e:
            set_error(str(e))
        finally:
            set_loading(False)

    def handle_callback(state: str):
        store_state(state)
        set_state_token(state)
        check_auth_status()

    return {
        "is_authenticated": is_authenticated,
        "user_info": user_info,
        "state_token": state_token,
        "loading": loading,
        "error": error,
        "login": login,
        "logout": logout,
        "check_auth_status": check_auth_status,
        "handle_callback": handle_callback,
    }

