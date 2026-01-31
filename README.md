<!DOCTYPE html>
<html>
<body>

<h1>soundcloud downloader</h1>
<p> jaja cree un downloader de soundcloud </p>

<h2>Requisitos</h2>
<ul>
    <li>Python 3.7+</li>
    <li>yt-dlp</li>
    <li>FFmpeg</li>
    <li>rich (es opcioanl igual esto)</li>
</ul>

<h2>Instalacion</h2>
<pre>
pip install yt-dlp rich
</pre>

<p>Instalar FFmpeg:</p>
<pre>
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Descargar desde https://ffmpeg.org/download.html
</pre>

<h2>Uso Basico</h2>
<pre>
python soundcloud_dl.py [opciones] [url]
</pre>

<h2>Opciones</h2>
<table border="1" cellpadding="8">
    <tr>
        <th>Opcion</th>
        <th>Descripcion</th>
        <th>Valor por defecto</th>
    </tr>
    <tr>
        <td><code>-o, --output DIR</code></td>
        <td>Directorio de salida</td>
        <td>descargas</td>
    </tr>
    <tr>
        <td><code>-f, --format FORMATO</code></td>
        <td>Formato de audio (mp3, flac, opus, wav, m4a, aac)</td>
        <td>mp3</td>
    </tr>
    <tr>
        <td><code>-q, --quality KBPS</code></td>
        <td>Calidad de audio en kbps</td>
        <td>320</td>
    </tr>
    <tr>
        <td><code>-i, --info</code></td>
        <td>Mostrar informacion sin descargar</td>
        <td>-</td>
    </tr>
    <tr>
        <td><code>-s, --search QUERY</code></td>
        <td>Buscar en SoundCloud</td>
        <td>-</td>
    </tr>
    <tr>
        <td><code>--search-limit N</code></td>
        <td>Limite de resultados de busqueda</td>
        <td>10</td>
    </tr>
    <tr>
        <td><code>-d, --download-search N</code></td>
        <td>Descargar resultado numero N de la busqueda</td>
        <td>-</td>
    </tr>
    <tr>
        <td><code>--no-metadata</code></td>
        <td>No agregar metadatos al archivo</td>
        <td>-</td>
    </tr>
    <tr>
        <td><code>--no-thumbnail</code></td>
        <td>No agregar caratula al archivo</td>
        <td>-</td>
    </tr>
    <tr>
        <td><code>--keep-original</code></td>
        <td>Mantener archivo original despues de conversion</td>
        <td>-</td>
    </tr>
    <tr>
        <td><code>-v, --version</code></td>
        <td>Mostrar version del programa</td>
        <td>-</td>
    </tr>
</table>

<h2>Ejemplos</h2>

<h3>Descargar un track</h3>
<pre>
python soundcloud_dl.py https://soundcloud.com/artista/cancion
</pre>

<h3>Descargar una playlist</h3>
<pre>
python soundcloud_dl.py https://soundcloud.com/artista/sets/mi-playlist
</pre>

<h3>Descargar en formato FLAC</h3>
<pre>
python soundcloud_dl.py -f flac https://soundcloud.com/artista/cancion
</pre>

<h3>Descargar con calidad especifica</h3>
<pre>
python soundcloud_dl.py -q 192 https://soundcloud.com/artista/cancion
</pre>

<h3>Especificar directorio de salida</h3>
<pre>
python soundcloud_dl.py -o ~/Musica https://soundcloud.com/artista/cancion
</pre>

<h3>Ver informacion sin descargar</h3>
<pre>
python soundcloud_dl.py --info https://soundcloud.com/artista/cancion
</pre>

<h3>Buscar en SoundCloud</h3>
<pre>
python soundcloud_dl.py --search "lofi beats"
</pre>

<h3>Buscar y descargar resultado especifico</h3>
<pre>
python soundcloud_dl.py --search "lofi beats" -d 3
</pre>

<h3>Descargar sin metadatos ni caratula</h3>
<pre>
python soundcloud_dl.py --no-metadata --no-thumbnail https://soundcloud.com/artista/cancion
</pre>

<h3>Modo interactivo</h3>
<pre>
python soundcloud_dl.py
</pre>

<h2>Comandos del Modo Interactivo</h2>
<table border="1" cellpadding="8">
    <tr>
        <th>Comando</th>
        <th>Descripcion</th>
    </tr>
    <tr>
        <td><code>download URL</code></td>
        <td>Descargar track o playlist</td>
    </tr>
    <tr>
        <td><code>info URL</code></td>
        <td>Mostrar informacion de URL</td>
    </tr>
    <tr>
        <td><code>search QUERY</code></td>
        <td>Buscar en SoundCloud</td>
    </tr>
    <tr>
        <td><code>get N</code></td>
        <td>Descargar resultado numero N de la ultima busqueda</td>
    </tr>
    <tr>
        <td><code>format FORMATO</code></td>
        <td>Cambiar formato de audio</td>
    </tr>
    <tr>
        <td><code>output DIR</code></td>
        <td>Cambiar directorio de salida</td>
    </tr>
    <tr>
        <td><code>config</code></td>
        <td>Ver configuracion actual</td>
    </tr>
    <tr>
        <td><code>help</code></td>
        <td>Mostrar ayuda</td>
    </tr>
    <tr>
        <td><code>exit</code></td>
        <td>Salir del programa</td>
    </tr>
</table>

<h2>Formatos de Audio Soportados</h2>
<ul>
    <li>mp3</li>
    <li>flac</li>
    <li>opus</li>
    <li>wav</li>
    <li>m4a</li>
    <li>aac</li>
</ul>

<h2>Notas</h2>
<ul>
    <li>Se requiere FFmpeg para la conversion de audio :V</li>
    <li>La calidad maxima depende de la fuente original en SoundCloud</li>
    <li>Algunos tracks pueden no estar disponibles para descarga debido a restricciones del uploader</li>
</ul>

</body>
</html>
