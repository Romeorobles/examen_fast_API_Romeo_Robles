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


@router.get("/", response_model=list[PlanSalida])
def listar_planes(
    nivel: Annotated[int | None, Query(ge=1, le=5)] = None,
    con_entrenador: bool | None = None,
):
    resultado = PLANES
    if nivel is not None:
        resultado = [p for p in resultado if p["nivel"] == nivel]
    if con_entrenador is not None:
        resultado = [p for p in resultado if p["incluye_entrenador"] == con_entrenador]
    return resultado


@router.post("/", response_model=PlanSalida, status_code=status.HTTP_201_CREATED)
def crear_plan(plan: PlanCrear):
    for existente in PLANES:
        if existente["codigo"] == plan.codigo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un plan con el código {plan.codigo}",
            )
    nuevo = plan.model_dump()
    PLANES.append(nuevo)
    return nuevo


@router.get("/{codigo}", response_model=PlanSalida)
def ver_plan(plan: PlanDep):
    return plan


@router.patch("/{codigo}", response_model=PlanSalida)
def actualizar_plan(plan: PlanDep, cambios: PlanActualizar):
    plan.update(cambios.model_dump(exclude_unset=True))
    return plan


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_plan(plan: PlanDep) -> None:
    PLANES.remove(plan)
