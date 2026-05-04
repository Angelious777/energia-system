from flask import Blueprint

from application.use_cases.obtener_dashboard import (
    obtener_resumen_dashboard
)

from application.use_cases.obtener_consumo_zona import (
    obtener_consumo_zona
)


dashboard_bp = Blueprint(
    'dashboard',
    __name__
)


@dashboard_bp.route(
    '/dashboard/resumen/<fecha>'
)
def resumen_dashboard(fecha):

    resultado = (
        obtener_resumen_dashboard(
            fecha
        )
    )

    return resultado


@dashboard_bp.route(
    '/zona/<zona>/consumo-actual'
)
def consumo_actual_zona(zona):

    resultado = (
        obtener_consumo_zona(
            zona
        )
    )

    return resultado