# SoundStream - Fase 7 Proyecto Integrador

Plataforma de streaming de musica sobre **MongoDB (NoSQL)**. Version NoSQL del
proyecto: los datos viven en colecciones de documentos en MongoDB Atlas. Backend
Django, frontend HTML/CSS/JS con animaciones de scroll, fotos y portadas reales
desde la API publica de Deezer, y preview de audio de 30s por cancion.

**Materia:** ITIZ-2201 Base de Datos II - Fase 7 (variante MongoDB).

---

## Stack

- **Backend**: Python 3.12, Django 5.2, django-mongodb-backend, pymongo
- **Base de datos**: MongoDB Atlas (colecciones de documentos, esquema NoSQL)
- **Frontend**: HTML, CSS y JavaScript vanilla (sin librerias externas)
- **API externa**: Deezer publica (sin API key) para fotos, portadas y previews

### Diseño NoSQL (documentos)

- `artistas` embebe su `discografica` (documento embebido).
- `canciones` embebe el arreglo `generos` y referencia `albumId` / `artistaId`.
- `playlists` embebe el arreglo `canciones` (ids), sin tabla puente.
- `usuarios` embebe arreglos (`cancionesGuardadas`, `albumesGuardados`,
  `artistasSeguidos`).
- Los `_id` son enteros; al insertar se calcula el siguiente id (max + 1).

---

## Requisitos previos

- **Python 3.12**.
- **MongoDB Atlas** (o un MongoDB accesible) con la base ya cargada.
- Internet (para Atlas y para fotos/portadas/audio desde Deezer).

---

## Instalacion

### 1. Clonar y crear el entorno

```powershell
git clone https://github.com/Sthefanoz/soundstream-fase7-mongo.git
cd soundstream-fase7-mongo
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r soundstream\requirements.txt
```

### 2. Configurar la conexion a MongoDB (JSON externo, sin credenciales en el codigo)

Por seguridad, la cadena de conexion **no** va en `settings.py`: se lee de un
archivo JSON externo que **no se versiona** (`db_config.json`, ignorado en
`.gitignore`). Copia la plantilla y coloca tu URI de Atlas:

```powershell
cd soundstream
copy db_config.example.json db_config.json   # luego edita db_config.json
```

Contenido de `db_config.json`:

```json
{
  "URI": "mongodb+srv://USUARIO:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority",
  "NAME": "SoundStreamDB_NoSQL"
}
```

El URI se obtiene en **Atlas > Connect > Drivers > Python**. `NAME` es el nombre
de la base dentro del cluster. La ruta del archivo se puede sobreescribir con la
variable de entorno `SOUNDSTREAM_DB_CONFIG`.

> **Objetos programables (NoSQL).** El equivalente a los stored procedures de SQL
> en MongoDB son los **aggregation pipelines**. El modulo de Reportes
> (`apps/reportes`) usa pipelines (`$group`, `$lookup`, `$sort`...) ejecutados del
> lado del servidor sobre las colecciones.

### 3. Migrar las colecciones internas de Django

```powershell
cd soundstream
python manage.py migrate    # crea la coleccion de sesiones de Django
```

Las colecciones del catalogo (`artistas`, `albumes`, `canciones`, `usuarios`,
`playlists`, `suscripciones`, `pagos`, `reproducciones`, `regalias`) ya existen
en tu base; los modelos las mapean con `managed = False`.

### 4. (Opcional) Rellenar/actualizar imagenes y audio desde Deezer

```powershell
python manage.py fotos_artistas         # fotos de artistas
python manage.py portadas_albumes       # portadas de albumes
python manage.py previews_canciones     # previews + duraciones
```

### 5. Arrancar

```powershell
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

---

## Login de prueba

- **Administrador** (acceso al panel de gestion del catalogo):
  - email: `sthefanozambrano1@gmail.com`
  - password: `1706895503Sm.`

- **Usuarios normales** (datos reales de Fase 3 con contrasena demo):
  - email: `michelle.altamirano1@email.com` / password `pass001`
  - email: `josue.chiriboga2@email.com` / password `pass002`
  - email: `camila.simbana3@email.com` / password `pass003`
  - ...y asi el resto: cada usuario `i` usa la contrasena `passNNN` con su
    `idUsuario`.

Si vas a ser admin en tu propia base, marca el rol del usuario en Mongo:

```js
db.usuarios.updateOne({ email: "tu_correo@email.com" }, { $set: { rol: "admin" } })
```

---

## Funcionalidades

| Pagina                       | Descripcion |
|------------------------------|-------------|
| `/`                          | Hero animado, top canciones (con play) y top artistas |
| `/catalogo/`                 | Buscador de canciones (titulo / artista / album) |
| `/artistas/`                 | Grilla con buscador en vivo |
| `/albumes/`                  | Grilla con buscador en vivo |
| `/usuarios/playlists/publicas/` | Playlists publicas con buscador en vivo |
| `/usuarios/playlists/mias/`  | Mis playlists (requiere login) - CRUD completo |
| `/usuarios/playlists/<id>/`  | Detalle: agregar/quitar canciones con buscador |
| `/suscripciones/`            | Planes (Free, Premium, Familiar) |
| `/suscripciones/contratar/X/`| Pago simulado con validacion de tarjeta (Luhn + MM/AA + CVV) |
| `/operacion/historial/`      | Historial de reproducciones y pagos |
| `/operacion/regalias/`       | Reporte de regalias por artista |
| `/catalogo/gestion/`         | Panel admin: CRUD de Artistas, Albumes y Canciones |
| `/reportes/`                 | Modulo de reportes (admin): top canciones/artistas, ingresos por plan, regalias, reproducciones por pais, suscripciones |

---

## Tarjeta de prueba para el pago

- Numero: `4242 4242 4242 4242`
- Vence: `12/30`
- CVV: `123`

---

## Comandos utiles

Dentro de `soundstream/` con el venv activado:

```powershell
python manage.py check                  # valida la configuracion
python manage.py runserver              # arranca el servidor
python manage.py migrate                # aplica migraciones de Django
python manage.py fotos_artistas         # baja/actualiza fotos
python manage.py portadas_albumes       # baja/actualiza portadas
python manage.py previews_canciones     # baja/actualiza previews + duracion
```

Cada comando acepta `--solo-vacias` para procesar solo los registros que aun
no tienen dato.

---

## Arquitectura y seguridad (Fase 7 - MongoDB)

- **Conexion via JSON externo** (`db_config.json`): el URI de Atlas no esta en el
  codigo ni en el control de versiones.
- **Objetos programables (NoSQL)**: el modulo de Reportes (`apps/reportes`) usa
  **aggregation pipelines** de MongoDB (`$group`, `$lookup`, `$sort`), el
  equivalente NoSQL a los stored procedures, ejecutados del lado del servidor.
- **Modelado de documentos**: discografica embebida en artista, generos como
  arreglo en cancion, canciones de playlist como arreglo de ids; los `_id` son
  enteros y al insertar se calcula el siguiente (`apps/common/ids.py`).
- **Reproductor persistente**: barra inferior con la cancion en curso, control
  de play/pausa, barra de progreso y preview de Deezer siempre fresca.

## Notas

- Las **fotos, portadas y audio** se sirven desde el CDN de Deezer; sin
  internet se ven los emojis de respaldo y los botones de play no suenan.
- La **preview de audio** se resuelve en vivo contra Deezer al dar play (las
  URLs caducan), de modo que las canciones siempre se puedan reproducir.
- El **pago es simulado**: los datos de tarjeta solo se validan, **no se
  guardan** (se crea el documento en `pagos` con el metodo de pago).
- Las contrasenas de `usuarios` estan en **texto plano** (asi vienen en los
  datos); la app respeta ese formato.
