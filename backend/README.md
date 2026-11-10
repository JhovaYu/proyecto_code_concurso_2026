# Backend

Base inicial para Django y Django REST Framework. El MVP abarca solicitudes hasta su aprobación o rechazo. La ONG crea y autoriza las cuentas; solo los representantes autorizados crean solicitudes. Para enviar una solicitud se requieren título, descripción, categoría y población beneficiaria estimada. La ONG podrá solicitar información adicional.

La configuración de PostgreSQL, los modelos, las migraciones, la autenticación y las rutas aún no están implementados. El flujo en `solicitudes/flujo.py` funciona únicamente en memoria: los datos de autorización del actor deben provenir de una futura capa de autenticación confiable, nunca directamente del cliente. Aún no existe historial de eventos persistente. No usar esta configuración en producción.

Instalación local desde la raíz del repositorio: `python -m venv .venv` y `.venv\Scripts\python -m pip install -r backend\requirements.txt`. Para ejecutar las pruebas de reglas sin base de datos: `cd backend` y `..\.venv\Scripts\python -m unittest discover`.
