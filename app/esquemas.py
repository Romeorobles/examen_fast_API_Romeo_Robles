from pydantic import BaseModel, Field


class PlanCrear(BaseModel):
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$")
    nombre: str = Field(min_length=3, max_length=60)
    precio_mensual: int = Field(ge=10, le=500)
    nivel: int = Field(ge=1, le=5)
    incluye_entrenador: bool = False


class PlanActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    precio_mensual: int | None = Field(default=None, ge=10, le=500)
    nivel: int | None = Field(default=None, ge=1, le=5)
    incluye_entrenador: bool | None = None


class PlanSalida(BaseModel):
    codigo: str
    nombre: str
    precio_mensual: int
    nivel: int
    incluye_entrenador: bool




