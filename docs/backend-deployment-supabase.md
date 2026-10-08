# Guía de Despliegue del Backend: Supabase (PostgreSQL) + Render / Railway

Esta guía explica paso a paso cómo desplegar el backend de **Tracker UP (FastAPI)** en la nube conectándolo a una base de datos **PostgreSQL en Supabase**, cumpliendo con la propuesta de migración técnica acordada con el equipo.

---

## 1. Paso 1: Configurar la Base de Datos en Supabase (Gratis)

1. Ingresa a [https://supabase.com](https://supabase.com) e inicia sesión con GitHub.
2. Haz clic en **"New Project"**.
3. Completa los datos:
   * **Name:** `tracker-up-db`
   * **Database Password:** Elige una contraseña segura (¡guárdala, la necesitarás en la URL!).
   * **Region:** Selecciona la más cercana (ej. *South America - São Paulo* o *US East - N. Virginia*).
4. Una vez creado el proyecto (tarda unos 2 minutos):
   * Ve a **Project Settings** (ícono de engranaje abajo a la izquierda) -> **Database**.
   * Baja a la sección **"Connection string"**.
   * Selecciona la pestaña **URI** y modo **Transaction Pooler** (puerto `6543`) o **Session** (puerto `5432`).
   * La URL tendrá un formato como este:
     ```text
     postgresql://postgres.[project-ref]:[TU-CONTRASEÑA]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
     ```
   * Reemplaza `[TU-CONTRASEÑA]` con la clave que pusiste en el paso 3.

---

## 2. Paso 2: Desplegar el Backend en Render (Opción Recomendada)

1. Ingresa a [https://render.com](https://render.com) e inicia sesión con GitHub.
2. Haz clic en **New +** -> **Web Service**.
3. Selecciona tu repositorio: `Tracker-UP-PlataformaDigitalWeb`.
4. Configura el servicio con estos valores exactos:
   * **Name:** `tracker-up-api`
   * **Region:** Misma región o cercana a Supabase (ej. *US East - Ohio*).
   * **Root Directory:** `backend`  <-- *(¡Muy importante!)*
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   * **Instance Type:** `Free`
5. En la sección **Environment Variables**, añade las siguientes variables:
   * `DATABASE_URL`: La URL de conexión de Supabase que obtuviste en el Paso 1.
   * `SECRET_KEY`: Una clave secreta alfanumérica segura (ej. `produccion-tracker-up-jwt-secret-2026-superkey`).
   * `CORS_ORIGINS`: `*` (o la URL de Netlify donde Gianela suba el frontend, ej: `https://tracker-up.netlify.app`).
   * `INSTITUTIONAL_DOMAIN`: `@alum.up.edu.pe`
6. Haz clic en **"Deploy Web Service"**.

---

## 3. ¿Cómo se cargan las tablas y las mallas en Supabase?

**¡Es 100% automático!**
Cuando Render inicie tu backend, el evento de arranque (`lifespan` en `app/main.py`) ejecutará automáticamente `init_database()`:
1. Creará todas las tablas en Supabase (`usuarios`, `carreras`, `asignaturas`, `prerrequisitos`, `historial_academico`, etc.).
2. Cargará las **12 carreras oficiales de la UP** con todos sus ciclos, prerrequisitos y concentraciones directamente desde los archivos JSON en `backend/data/curricula/`.
3. Tu API estará lista y podrás verificarla accediendo a:
   `https://tu-servicio-render.onrender.com/docs` (Swagger interactivo).

---

## 4. Paso 3: Entregar la URL a Gianela (Frontend)

Una vez que Render te dé tu URL pública (ejemplo: `https://tracker-up-api.onrender.com`), solo debes pasársela a Gianela para que la coloque en la configuración del frontend de Netlify/Vercel:

```env
# En el frontend (.env de Netlify)
VITE_API_URL=https://tracker-up-api.onrender.com/api/v1
```

