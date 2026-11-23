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


@router.get("/facturacion")
def facturacion_periodo(
    meses: Annotated[int, Query(ge=1, le=24)],
    nivel: Annotated[int | None, Query(ge=1, le=5)] = None,
):
    seleccion = []
    for plan in PLANES:
        if nivel is None or plan["nivel"] == nivel:
            seleccion.append(plan)

    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay planes para calcular la facturación",
        )

    suma_precios = 0
    con_entrenador = 0
    for plan in seleccion:
        suma_precios += plan["precio_mensual"]
        if plan["incluye_entrenador"]:
            con_entrenador += 1

    cantidad = len(seleccion)
    facturacion_base = suma_precios * meses
    descuento_aplicado = meses >= 12
    facturacion_estimada = facturacion_base * 0.85 if descuento_aplicado else facturacion_base

    return {
        "planes": cantidad,
        "meses": meses,
        "precio_promedio": round(suma_precios / cantidad, 2),
        "facturacion_base": facturacion_base,
        "descuento_aplicado": descuento_aplicado,
        "facturacion_estimada": round(facturacion_estimada, 2),
        "porcentaje_con_entrenador": round(con_entrenador / cantidad * 100, 1),
    }


@router.get("/socio")
def planes_del_socio(
    contratados: Annotated[list[str] | None, Query()] = None,
):
    if not PLANES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay planes registrados",
        )

    codigos = set()
    for codigo in contratados or []:
        codigos.add(codigo.upper())

    total = 0
    cantidad_contratados = 0
    disponibles = 0
    ingreso_potencial = 0
    mas_caro = None
    for plan in PLANES:
        total += 1
        if plan["codigo"] in codigos:
            cantidad_contratados += 1
        else:
            disponibles += 1
            ingreso_potencial += plan["precio_mensual"]
            if mas_caro is None or plan["precio_mensual"] > mas_caro["precio_mensual"]:
                mas_caro = plan

    return {
        "total": total,
        "contratados": cantidad_contratados,
        "disponibles": disponibles,
        "porcentaje_contratacion": round(cantidad_contratados / total * 100, 1),
        "ingreso_potencial_disponibles": ingreso_potencial,
        "plan_disponible_mas_caro": mas_caro["codigo"] if mas_caro else None,
    }


@router.get("/{codigo}", response_model=PlanSalida)
def ver_plan(plan: PlanDep):
    return plan


@router.patch("/{codigo}", response_model=PlanSalida)
def actualizar_plan(plan: PlanDep, cambios: PlanActualizar):
    plan.update(cambios.model_dump(exclude_unset=True, exclude_none=True))
    return plan


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_plan(plan: PlanDep) -> None:
    PLANES.remove(plan)
