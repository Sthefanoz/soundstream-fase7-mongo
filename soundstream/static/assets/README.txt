ASSETS - SoundStream
====================

Coloca aqui tus archivos visuales:

- hero.mp4           Video de fondo para el efecto "Apple scroll" del Inicio.
                     Recomendado 1080p, 10-20 segundos, H.264 MP4.
                     Activa el efecto cambiando {% if False %} por {% if True %}
                     en templates/web/inicio.html.

- hero-poster.jpg    Imagen estatica que se muestra mientras carga el video.

- logo.png           Logo de SoundStream para el navbar (opcional).

- artistas/          Subcarpeta con fotos de artistas:
    aurora-vega.jpg
    lumen-collective.jpg
    diego-solar.jpg
    ...

- albumes/           Subcarpeta con portadas:
    velocidad-de-la-luz.jpg
    ruido-blanco.jpg
    ...

Despues actualiza los campos 'foto' y 'portada' en SQL Server o edita
fixtures/sample_data.json con las rutas (por ejemplo: /static/assets/artistas/aurora-vega.jpg).
