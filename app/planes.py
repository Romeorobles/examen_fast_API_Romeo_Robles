from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import PLANES
from app.esquemas import PlanActualizar, PlanCrear, PlanSalida

router = APIRouter(prefix="/membresias", tags=["Planes de membresía"])


def obtener_plan(codigo: str) -> dict:
    codigo = codigo.upper()
    for plan in PLANES:
        if plan["codigo"] == codigo:
            return plan
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe un plan con el código {codigo}",
    )


PlanDep = Annotated[dict, Depends(obtener_plan)]

