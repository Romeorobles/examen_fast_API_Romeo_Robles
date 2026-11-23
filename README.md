# Gimnasio — Planes de Membresía

API REST con FastAPI sobre un arreglo en memoria (Programación IV · Variante 1).

## Ejecutar

```bash
uv sync
uv run fastapi dev app/main.py
```

Documentación: http://127.0.0.1:8000/docs

## Estructura

```
app/
├── main.py      # aplicación y include_router
├── datos.py     # arreglo PLANES
├── esquemas.py  # PlanCrear, PlanActualizar, PlanSalida
└── planes.py    # router, dependencia y endpoints
```

## Rutas

| Método | Ruta | Éxito | Errores |
|---|---|---|---|
| GET | `/membresias/?nivel=&con_entrenador=` | 200 | 422 |
| POST | `/membresias/` | 201 | 409, 422 |
| GET | `/membresias/facturacion?meses=&nivel=` | 200 | 404, 422 |
| GET | `/membresias/socio?contratados=A&contratados=B` | 200 | 404 |
| GET | `/membresias/{codigo}` | 200 | 404 |
| PATCH | `/membresias/{codigo}` | 200 | 404, 422 |
| DELETE | `/membresias/{codigo}` | 204 | 404 |
