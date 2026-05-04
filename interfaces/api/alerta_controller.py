from flask import Blueprint

from application.use_cases.obtener_alertas_historicas import (
    obtener_alertas_historicas
)

from application.use_cases.obtener_alertas_recientes import (
    obtener_alertas_recientes
)


alerta_bp = Blueprint(
    'alerta',
    __name__
)


@alerta_bp.route(
    '/alertas/historico/<fecha>'
)
def alertas_historicas(fecha):

    resultado = (
        obtener_alertas_historicas(
            fecha
        )
    )

    return {

        "total":
            len(resultado),

        "alertas":
            resultado
    }


@alerta_bp.route(
    '/alertas/recientes'
)
def alertas_recientes():

    resultado = (
        obtener_alertas_recientes()
    )

    return {

        "total":
            len(resultado),

        "alertas":
            resultado
    }