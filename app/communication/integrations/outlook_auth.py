from pathlib import Path

import msal


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CLIENT_ID_FILE = (
    PROJECT_ROOT
    / ".secrets"
    / "microsoft"
    / "client_id.txt"
)

TOKEN_CACHE_FILE = (
    PROJECT_ROOT
    / ".secrets"
    / "microsoft"
    / "token_cache.json"
)

AUTHORITY = "https://login.microsoftonline.com/common"

SCOPES = [
    "Mail.ReadWrite",
]


def _load_client_id() -> str:
    if not CLIENT_ID_FILE.exists():
        raise FileNotFoundError(
            f"Microsoft client ID not found: {CLIENT_ID_FILE}"
        )

    client_id = CLIENT_ID_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not client_id:
        raise ValueError("Microsoft client ID is empty.")

    return client_id


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()

    if TOKEN_CACHE_FILE.exists():
        cache.deserialize(
            TOKEN_CACHE_FILE.read_text(
                encoding="utf-8"
            )
        )

    return cache


def _save_cache(
    cache: msal.SerializableTokenCache,
) -> None:
    if not cache.has_state_changed:
        return

    TOKEN_CACHE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    TOKEN_CACHE_FILE.write_text(
        cache.serialize(),
        encoding="utf-8",
    )


def get_outlook_access_token() -> str:
    cache = _load_cache()

    app = msal.PublicClientApplication(
        client_id=_load_client_id(),
        authority=AUTHORITY,
        token_cache=cache,
    )

    result = None

    accounts = app.get_accounts()

    if accounts:
        result = app.acquire_token_silent(
            SCOPES,
            account=accounts[0],
        )

    if not result:
        flow = app.initiate_device_flow(
            scopes=SCOPES,
        )

        if "user_code" not in flow:
            raise RuntimeError(
                f"Could not start Microsoft login: {flow}"
            )

        print()
        print(flow["message"])
        print()

        result = app.acquire_token_by_device_flow(
            flow
        )

    _save_cache(cache)

    if "access_token" not in result:
        error = result.get(
            "error_description",
            result.get("error", "Unknown Microsoft login error"),
        )
        raise RuntimeError(error)

    return result["access_token"]