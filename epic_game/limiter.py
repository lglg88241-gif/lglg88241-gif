import contextvars

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

user_role_ctx = contextvars.ContextVar("user_role", default=None)

limiter = Limiter(key_func=get_remote_address)

# def is_internal_admin(request: Request) -> bool:
#     client_ip = request.client.host
#     internal_admin_ips = {"127.0.0.1", "192.168.1.100"}
#     return client_ip in internal_admin_ips


def get_dynamic_limit(request: Request) -> str:
    user_role = getattr(request.state, "user_role", None)
    if user_role == "admin":
        return "100000/minute"
    return "10/minute"


def is_admin_exempt() -> bool:
    return user_role_ctx.get() == "admin"
