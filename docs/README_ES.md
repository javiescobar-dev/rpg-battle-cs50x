# RPG Battle - Proyecto Final CS50x

#### Video Demo: <URL del vídeo (pendiente de grabar)>

#### Repositorio: <https://github.com/javiescobar-dev/rpg-battle-cs50x>

#### Descripción

RPG Battle es un juego de combates por turnos al estilo Suikoden II construido
con Python y Pygame, acompañado de un launcher de escritorio en customTkinter
que descarga, actualiza y lanza el juego a partir de los *releases* de GitHub.
La idea nace de emular el primer ejercicio de CS50x, el proyecto de la Semana 0
en Scratch, que fue precisamente una batalla RPG, y para complementarlo, decidí
incorporar un launcher que facilita su distribución, lo mantiene actualizado y
muestra noticias y nuevas versiones. El proyecto también sirve para practicar el
diseño de un programa completo en Python: lógica de juego desacoplada de la
parte gráfica, una máquina de estados, animaciones por eventos, persistencia de
datos y un ciclo de distribución (compilación con PyInstaller y CI con GitHub
Actions).

Al abrir el juego aparece un menú principal con las opciones Play, Statistics y
Quit. Cada batalla se desarrolla por turnos: el héroe elige atacar, usar una
habilidad (Fireball, Guard o Heal), tomar una poción o huir, y el enemigo actúa
con una IA ponderada. Cada combate elige aleatoriamente un héroe, un enemigo y
un escenario, y su resultado queda guardado en un archivo JSON (`scores.json`)
que luego se carga en las pantallas de fin de batalla y de estadísticas. El
launcher muestra las noticias del proyecto en un carrusel de imágenes, y permite
instalar, actualizar o desinstalar el juego con un clic.

## El juego

**El combate.** En cada turno el héroe elige entre atacar físicamente, lanzar
una de las tres habilidades que consumen maná (Fireball, Guard y Heal), tomar
una poción para recuperar vida o intentar huir; la huida se resuelve según la
velocidad relativa. El enemigo decide su acción con una IA ponderada entre
ataque, hechizo y guardia, que vuelve al ataque cuando se queda sin maná. El
daño se calcula con una fórmula que reduce la defensa del objetivo, aplica un
rango aleatorio y tiene un 10% de probabilidad de crítico; la guardia reduce la
siguiente acción recibida y se consume en el contacto, y el registro del combate
informa del daño real ya mitigado.

**La escena de batalla.** El combate se presenta en un campo con profundidad al
estilo Suikoden II: el enemigo se sitúa arriba a la izquierda con una escala
ligeramente menor (0.95, algo más lejos) y el héroe abajo a la derecha más cerca
de la cámara (1.1), con un cambio de escala dinámico que vende la profundidad
durante los movimientos. La tarjeta fija del héroe (retrato, nombre y barras de
HP/MP) ocupa la esquina superior derecha; los valores del enemigo se mantienen
ocultos para conservar la tensión, mostrando solo su nombre sobre él. Un panel
de log con las últimas líneas del combate recorre los eventos con ajuste de
línea.

**Navegación.** El menú principal (Play, Statistics, Quit) y el menú de batalla
de dos niveles (Attack / Skill / Potion / Flee, con el submenú de habilidades
Fireball / Guard / Heal / Back) comparten un único cursor: se mueve con teclado
(flechas + Enter, con atajos numéricos) o con el ratón (el hover lo desplaza y
el clic confirma).

**Animaciones.** El motor no dibuja nada: genera eventos que un `EventPlayer`
reproduce uno a uno. El ataque físico es una arremetida diagonal que se detiene
antes del objetivo, con un destello de impacto, un retroceso del defensor y el
número de daño que asciende y se desvanece; al volver, el atacante salta hacia
atrás manteniendo la vista en el objetivo mientras su escala cambia para
reforzar la profundidad. Los hechizos lanzan un proyectil brillante con estela,
pulso y anillos de explosión al impactar (naranja para el héroe, púrpura para
el enemigo). La curación levanta un tornado de partículas verdes que envuelve al
personaje, la guardia dibuja un escudo de arco con tres capas inclinado en
diagonal hacia el rival y la poción hace flotar el sprite animado de una botella
sobre la cabeza. Los números y mensajes se colorean por tipo: amarillo para el
daño, rojo y grande con "!" para los críticos, verde para curaciones y pociones,
azul claro para la guardia y blanquecino para los fallos. El log del combate
avanza en vivo, una línea por evento, y el juego solo vuelve al menú o termina
cuando termina la última animación.

**Recursos.** Los personajes usan hojas de sprites de pixel art (Pixel
Champions II) de 864×576 píxeles. Al cargarse, cada hoja se recorta en celdas
de 96×96 y se almacena en un diccionario por pose con 3 frames cada una (18
poses, más una pose `run` derivada de `flee` al voltearla horizontalmente); al
lanzar una acción se reproduce la animación guardada para esa pose. Hay 8
héroes y 5 enemigos, y cada batalla elige además al azar uno de 4 fondos de
pixel art (castillo, bosque, cueva, puerto). Varios efectos de sonido WAV se
asocian a las acciones y suenan en las fases concretas
(arremetida, lanzamiento, impacto), con blips de cursor en los menús; se
obtuvieron con licencia de itch.io (Leohpaz), igual que las hojas de sprites
(Pixel Champions II). Las
pantallas de título y fin usan fondos con un overlay oscuro para dar contraste
al texto y una transición de fade a negro entre pantallas; el título del fin se
pinta a 64 px con un color que refleja el resultado (dorado en victoria, rojo en
derrota), y las estadísticas se muestran en una tabla alineada con valores en
color de acento dentro de un panel semi-transparente cuyo layout se define en
`config.py`.

## El launcher

**Rol.** Es el punto de entrada del usuario: descarga, actualiza, lanza y
desinstala el juego directamente desde los *Releases* de GitHub y muestra las
noticias del proyecto en un carrusel.

**Ventana.** Es una ventana sin marco nativo (la barra de título se oculta con
una técnica de *hidden titlebar* que conserva la sombra y las animaciones
nativas de Windows), organizada en tres bandas horizontales: cabecera con el
título renderizado con la misma fuente del juego y su barra de subrayado, una
zona central con el carrusel y un pie con la versión instalada, los botones
(Play, Download/Update, Uninstall) y la barra de progreso. Minimizar y cerrar
son botones propios con iconos de Flaticon (cerrar, minimizar y cambio de tema),
y la cabecera se puede arrastrar. El icono del ejecutable lo comparten el juego y
el launcher y se generó con IA.

**Temas.** Dispone de tema claro y oscuro, cambiables desde el botón con icono
de sol/luna de la esquina superior izquierda. El tema claro usa fondo blanco
con acentos en cyan y el oscuro un fondo color carbón con acentos dorados;
ambos remarcan la ventana principal y el carrusel con bordes negros para dar un
toque de estilo. El cambio es una recoloración en caliente de los widgets, sin
reconstruir la interfaz ni parpadear, y el tema seleccionado se guarda en un
archivo JSON (`settings.json`), de modo que al abrir el launcher, se mantiene el
último tema elegido.

**Carrusel de noticias.** Carga `news.json` desde GitHub (tanto la descripción
como la ruta de las imágenes) con un caché local de una hora (y la última copia
conocida si no hay conexión). De cada noticia lee su título, su cuerpo y la ruta
de su imagen, y lo dibuja todo junto (imagen recortada sin deformar para llenar
el marco, overlay, texto, flechas y puntos de navegación) en una única imagen
compuesta. La interacción es, por tanto, un gestor de clics sobre esa imagen:
según la zona en la que se pulse se ejecuta una acción u otra, como pasar a la
noticia anterior o siguiente con las flechas o saltar a la noticia de un punto
concreto. Se eligió este diseño porque customTkinter no permite superponer
widgets con transparencia sobre imágenes; todo se resuelve pintando. El cambio
de slide se anima con una transición deslizante.

**Descarga y versionado.** Al arrancar consulta la última release de GitHub y la
compara con la versión instalada en local para configurar el botón: "Download"
si no hay nada instalado, "Update" si existe una versión más nueva y "Up to
date" (deshabilitado) si ya está al día. Del release selecciona el zip del
sistema operativo en el que se ejecuta (`rpg-battle-<plataforma>-<versión>.zip`),
lo descarga a una carpeta temporal y lo extrae en el directorio de datos del
usuario que corresponde a ese sistema operativo. Durante la descarga muestra una barra
de progreso sobre la que corre un sprite del héroe con la misma animación y
técnica que el juego (en concreto la pose Flee, corriendo hacia la derecha en la
misma dirección que avanza la barra), con un héroe aleatorio en cada descarga;
mientras descarga o desinstala, los botones del pie se deshabilitan y al
terminar se vuelven a habilitar según el resultado (Play y Uninstall cuando hay
juego instalado, y el botón de descarga se actualiza). Al finalizar guarda la
versión instalada y habilita Play. "Uninstall" limpia en
una sola acción el juego, las versiones, los cachés, el log y los ajustes, con
confirmación previa.

**Fiabilidad.** Cada operación de red registra en `launcher.log` la fase exacta
que falla (consulta de release, búsqueda de asset, descarga, extracción) con un
timeout de 20 segundos. La verificación TLS usa `truststore` para validar contra
el almacén de certificados del sistema, lo que evita los fallos típicos en
redes corporativas o máquinas virtuales donde el antivirus intercepta HTTPS;
esta verificación se añadió precisamente porque, al probar el launcher en una
máquina virtual con Windows 11, fallaba al intentar validar los certificados del
sistema. Las rutas de datos usan `platformdirs` (el directorio de datos del
usuario de cada sistema operativo), nunca la carpeta del ejecutable.

## Estructura de archivos

El código fuente del juego está en `game/`:

- `game/config.py` - todas las constantes y el equilibrio del juego: tamaño de
  pantalla, colores, fuentes, valores de HP/MP, daños, lista de héroes,
  enemigos y fondos, rutas de assets y layout de las pantallas.
- `game/entities.py` - la clase `Entity` (nombre, stats, HP/MP, defensa, etc.),
  los personajes `Hero` y `Enemy`, y la lógica de decisión de la IA enemiga.
- `game/battle.py` - el motor de combate por turnos, puro Python sin Pygame:
  la fórmula de daño (defensa, rango aleatorio y crítico), las acciones
  (ataque, hechizo, guard, poción, huida) y la generación de eventos que
  alimentan el log.
- `game/score.py` - historial de resultados: guarda cada batalla en
  `scores.json` (fecha, resultado, turnos) y calcula el resumen de
  estadísticas.
- `game/ui.py` - toda la parte visual del juego: sprites de personajes,
  paneles de batalla, el log, los menús, y las animaciones por eventos
  (ataque, hechizos, hechizo de vida, guard y poción).
- `game/assets.py` - carga de recursos: hojas de sprites, fondos, efectos de
  sonido, fuentes y el icono.
- `game/main.py` - el bucle principal y la máquina de estados
  (MENU / STATS / BATTLE / ANIM / END), junto con los dibujos de cada pantalla.

El launcher está en `launcher/`:

- `launcher/config.py` - constantes de la aplicación (nombre, URL canónicas de
  los releases y las noticias).
- `launcher/paths.py` - rutas de datos multiplataforma, gestión de versiones,
  la comprobación de instalación y el arranque del juego.
- `launcher/updater.py` - consulta el último *release* de GitHub, descarga el
  zip de la plataforma con barra de progreso y lo instala.
- `launcher/news.py` - obtiene, cachea y procesa el feed de noticias `news.json`.
- `launcher/ui_styles.py` - paletas de colores de los temas claro y oscuro.
- `launcher/settings.py` - persistencia de ajustes locales (`settings.json`).
- `launcher/diag.py` - registro de diagnóstico y verificación TLS con
  `truststore`.
- `launcher/main.py` - la ventana principal (fondo, carrusel, temas, botones).

Otros archivos:

- `build/game.spec` y `build/launcher.spec` - configuraciones de PyInstaller
  para empaquetar ambos programas.
- `.github/workflows/build.yml` - CI que compila el juego y el launcher en
  Windows, macOS y Linux y publica un *release* de GitHub por cada etiqueta.
- `news/news.json` - el feed de noticias que consume el launcher.

## Decisiones de diseño

- **Motor separado de la interfaz.** `battle.py` no importa Pygame: la lógica
  de combate se puede ejecutar y probar en consola (de hecho la Fase 1 era
  jugable en el terminal). Esto mantiene la mecánica limpia y ajena a la
  presentación.
- **Eventos en vez de acoplar la simulación a la animación.** El motor no
  anima nada: genera una lista de eventos (ataque, daño, cura, huida…) que un
  `EventPlayer` va reproduciendo uno a uno como animaciones. La batalla solo
  avanza cuando la animación en curso termina, lo que da control del ritmo
  y evita estados inconsistentes.
- **Animaciones basadas en físicas simples.** Las estelas, los proyectiles y
  las partículas se calculan con vectores y phasing por frame en lugar de
  sprites predefinidos, lo que permite efectos suaves (estela, rebote,
  remolino de curación) sin depender de hojas de animación gigantes.
- **Pygame-ce en lugar de Pygame.** Se eligió el *community edition*, la
  bifurcación mantenida que sigue al día y funciona bien con Python moderno.
- **customTkinter para el launcher.** `tkinter` permite un programa ligero sin
  dependencias pesadas; `customtkinter` aporta temas claros/oscuros y
  widgets modernos. El tema elegido es un simple cambio de color en caliente,
  lo que evita reconstruir la interfaz y parpadeos.
- **Distribución por *Releases*.** El launcher no sabe de servidores propios:
  consume la API pública de GitHub (`latest release`) para descargar el
  binario correcto. Todo el ciclo es seguro y automatizado: se compila en
  GitHub Actions, la rama `release` está protegida (solo el dueño puede
  publicar), una etiqueta `v*` lanza el build y el release nace como *Draft*
  para revisarlo antes de publicarlo.
- **Fallos silenciosos que no lo son.** Cada red escribe un log con la fase
  exacta que falla y los tiempos de espera están limitados; los cachés de
  noticias e imágenes sobreviven a la desconexión. Así el launcher funciona
  sin conexión y los problemas se diagnostican sin adivinar.
- **Persistencia en el directorio de datos del usuario.** Partidas y cachés
  se guardan con `platformdirs` en la ruta del sistema operativo que
  corresponde, en lugar de junto al ejecutable (que puede ser de solo lectura).
- **Empaquetado `--onedir` con CI.** `PyInstaller` en modo carpeta reduce los
  falsos positivos de antivirus y arranca más rápido; GitHub Actions compila
  las tres plataformas y publica las release, y las rutas de assets se
  resuelven con `sys._MEIPASS`, de modo que el ejecutable funciona desde
  cualquier carpeta.
- **Sprites de pixel art reales.** En lugar de formas geométricas, los
  personajes usan hojas de sprites (Pixel Champions II) escaladas con
  `smoothscale` y con un factor dinámico para dar el efecto de profundidad. El
  resultado se ve mucho más atractivo que los placeholders sin complicar
  demasiado la carga de assets.
- **El launcher como aplicación separada.** El juego se empaqueta como un zip
  portable que el launcher descarga; el launcher es la única pieza que el
  usuario abre y se encarga de instalar, actualizar y lanzar el juego. Separar
  las dos aplicaciones permite distribuir actualizaciones del juego sin
  recompilar el launcher y mantiene cada binario pequeño.
- **Atribución de recursos.** Los sprites provienen de Pixel Champions II y los
  efectos de sonido de Leohpaz, ambos de itch.io con licencia; los iconos del
  header (cerrar, minimizar, tema) son de Flaticon; el icono del ejecutable y
  los fondos de pixel art se generaron con ayuda de IA. El uso de la herramienta
  de IA que acompañó el desarrollo se cita en la cabecera de cada archivo
  fuente, como pide la política del curso.

## Ejecución y compilación

En desarrollo:

```bash
python -m game.main
```

El launcher solo necesita ejecutarse en modo Python si existe carpeta `game/`
(usa `python -m game.main` automáticamente); en producción se compila con
PyInstaller desde `build/game.spec` y `build/launcher.spec`.

El juego y el launcher están diseñados para compilar y funcionar en
multiplataforma (Windows, Linux y macOS). GitHub Actions compila por cada
sistema operativo un ejecutable del juego y otro del launcher, 6 ejecutables en
total, y cada uno se comprime en un zip por separado para facilitar su
distribución. El proceso es el siguiente: primero paso los cambios de la rama
`dev` a la rama `release` mediante un pull request de forma segura; después subo
una etiqueta `v*` con la nueva versión, lo que dispara el workflow. Cuando
termina de compilar y comprimir, genera un nuevo release en estado *Draft*, que
reviso manualmente y publico de forma segura.

## Nota

El README en inglés que se entrega a CS50x se ha redactado con la ayuda de un
asistente de IA para la traducción, ya que el inglés no es mi lengua materna y
aún no está al nivel que me gustaría; el aviso de uso de IA también se cita en
la cabecera de cada archivo fuente, como pide la política del curso.
