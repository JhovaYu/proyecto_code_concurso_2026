# Backend

Base inicial para Django y Django REST Framework. El MVP abarca solicitudes hasta su aprobación o rechazo. La ONG crea y autoriza las cuentas; solo los representantes autorizados crean solicitudes. Para enviar una solicitud se requieren título, descripción, categoría y población beneficiaria estimada. La ONG podrá solicitar información adicional.

La configuración de PostgreSQL, los modelos, las migraciones, la autenticación y las rutas aún no están implementados. Se acordó usar sesiones de Django con cookies para el acceso futuro y texto libre para la categoría. Los contratos DRF en `solicitudes/serializadores.py` aún no están conectados a una API. El flujo en `solicitudes/flujo.py` funciona únicamente en memoria: los datos de autorización del actor deben provenir de una futura capa de autenticación confiable, nunca directamente del cliente. Aún no existe historial de eventos persistente. No usar esta configuración en producción.

El motor en `evaluaciones/motor.py` calcula un promedio ponderado exacto con urgencia (40 %), impacto social (30 %) y severidad (30 %) como pesos iniciales configurables. La ONG captura las tres calificaciones de 0 a 10. `solicitudes/evaluacion.py` restringe la evaluación a la ONG autorizada durante la revisión; modificar una solicitud evaluada exige evaluarla de nuevo y conserva el historial solo en memoria. El resultado no aprueba ni rechaza automáticamente.

Instalación local desde la raíz del repositorio: `python -m venv .venv` y `.venv\Scripts\python -m pip install -r backend\requirements.txt`. Para ejecutar las pruebas de reglas sin base de datos: `cd backend` y `..\.venv\Scripts\python -m unittest discover`.
