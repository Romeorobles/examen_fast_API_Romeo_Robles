from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.datos import PLANES
from app.esquemas import PlanActualizar, PlanCrear, PlanSalida

router = APIRouter(prefix="/membresias", tags=["Planes de membresia"])


def buscar_plan(codigo: str):
    for plan in PLANES:
        if plan["codigo"] == codigo.upper():
            return plan
    raise HTTPException(status_code=404, detail="Plan no encontrado")


PlanDep = Annotated[dict, Depends(buscar_plan)]


@router.get("/", response_model=list[PlanSalida])
def listar_planes(
    nivel: Annotated[int | None, Query(ge=1, le=5)] = None,
    con_entrenador: bool | None = None,
):
    lista = PLANES
    if nivel is not None:
        lista = [p for p in lista if p["nivel"] == nivel]
    if con_entrenador is not None:
        lista = [p for p in lista if p["incluye_entrenador"] == con_entrenador]
    return lista


@router.post("/", response_model=PlanSalida, status_code=201)
def crear_plan(plan: PlanCrear):
    for p in PLANES:
        if p["codigo"] == plan.codigo:
            raise HTTPException(status_code=409, detail=f"Ya existe un plan con el codigo {plan.codigo}")
    nuevo = plan.model_dump()
    PLANES.append(nuevo)
    return nuevo


@router.get("/facturacion")
def facturacion(
    meses: Annotated[int, Query(ge=1, le=24)],
    nivel: Annotated[int | None, Query(ge=1, le=5)] = None,
):
    cantidad = 0
    suma = 0
    con_entrenador = 0
    for p in PLANES:
        if nivel is None or p["nivel"] == nivel:
            cantidad += 1
            suma += p["precio_mensual"]
            if p["incluye_entrenador"]:
                con_entrenador += 1

    if cantidad == 0:
        raise HTTPException(status_code=404, detail="No hay planes para calcular la facturacion")

    base = suma * meses
    descuento = meses >= 12
    estimada = base * 0.85 if descuento else base

    return {
        "planes": cantidad,
        "meses": meses,
        "precio_promedio": round(suma / cantidad, 2),
        "facturacion_base": base,
        "descuento_aplicado": descuento,
        "facturacion_estimada": round(estimada, 2),
        "porcentaje_con_entrenador": round(con_entrenador * 100 / cantidad, 1),
    }


@router.get("/socio")
def planes_socio(contratados: Annotated[list[str] | None, Query()] = None):
    if len(PLANES) == 0:
        raise HTTPException(status_code=404, detail="No hay planes registrados")

    codigos = set()
    if contratados:
        for c in contratados:
            codigos.add(c.upper())

    total = len(PLANES)
    num_contratados = 0
    disponibles = 0
    ingreso = 0
    mas_caro = None
    for p in PLANES:
        if p["codigo"] in codigos:
            num_contratados += 1
        else:
            disponibles += 1
            ingreso += p["precio_mensual"]
            if mas_caro is None or p["precio_mensual"] > mas_caro["precio_mensual"]:
                mas_caro = p

    return {
        "total": total,
        "contratados": num_contratados,
        "disponibles": disponibles,
        "porcentaje_contratacion": round(num_contratados * 100 / total, 1),
        "ingreso_potencial_disponibles": ingreso,
        "plan_disponible_mas_caro": mas_caro["codigo"] if mas_caro else None,
    }


@router.get("/{codigo}", response_model=PlanSalida)
def ver_plan(plan: PlanDep):
    return plan


@router.patch("/{codigo}", response_model=PlanSalida)
def actualizar_plan(plan: PlanDep, datos: PlanActualizar):
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    plan.update(cambios)
    return plan


@router.delete("/{codigo}", status_code=204)
def eliminar_plan(plan: PlanDep):
    PLANES.remove(plan)
