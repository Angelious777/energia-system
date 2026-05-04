from flask import Blueprint

from application.use_cases.verificar_health import (
    verificar_health
)

health_bp = Blueprint(
    'health',
    __name__
)

@health_bp.route(
    '/health'
)
def health():
    return verificar_health()