#!/usr/bin/env python3
"""
SoundCloud Downloader CLI
Descarga música de SoundCloud usando yt-dlp
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional
import yt_dlp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

AUDIO_FORMATS = ['mp3', 'opus', 'flac', 'wav', 'm4a', 'aac']

class SoundCloudDownloader:
    """Clase principal para descargar música de SoundCloud."""
    
    def __init__(
        self,
        output_dir: str = "descargas",
        audio_format: str = "mp3",
        audio_quality: str = "320",
        keep_original: bool = False,
        add_metadata: bool = True,
        add_thumbnail: bool = True
    ):
        self.output_dir = Path(output_dir)
        self.audio_format = audio_format
        self.audio_quality = audio_quality
        self.keep_original = keep_original
        self.add_metadata = add_metadata
        self.add_thumbnail = add_thumbnail
        self.progress = None
        self.task_id = None
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_ydl_opts(self, info_only: bool = False) -> dict:
        """Genera las opciones para yt-dlp."""
        
        output_template = str(self.output_dir / "%(uploader)s - %(title)s.%(ext)s")
        
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        if info_only:
            opts['skip_download'] = True
            return opts
        
        postprocessors = []
        
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': self.audio_format,
            'preferredquality': self.audio_quality,
        })
        
        if self.add_metadata:
            postprocessors.append({
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            })
        
        if self.add_thumbnail:
            postprocessors.append({
                'key': 'EmbedThumbnail',
            })
            opts['writethumbnail'] = True
        
        opts['postprocessors'] = postprocessors
        opts['keepvideo'] = self.keep_original
        opts['progress_hooks'] = [self._progress_hook]
        
        return opts
    
    def _progress_hook(self, d: dict):
        """Hook para mostrar progreso de descarga."""
        if d['status'] == 'downloading':
            if self.progress and self.task_id is not None:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    self.progress.update(self.task_id, completed=downloaded, total=total)
        
        elif d['status'] == 'finished':
            if self.progress and self.task_id is not None:
                self.progress.update(self.task_id, completed=100, total=100)
    
    def get_info(self, url: str) -> Optional[dict]:
        """Obtiene información de una URL sin descargar."""
        opts = self._get_ydl_opts(info_only=True)
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            console.print(f"[red]Error obteniendo información: {e}[/red]")
            return None
    
    def show_info(self, url: str):
        """Muestra información detallada de una URL."""
        with console.status("[bold green]Obteniendo información..."):
            info = self.get_info(url)
        
        if not info:
            return
        
        if '_type' in info and info['_type'] == 'playlist':
            self._show_playlist_info(info)
        else:
            self._show_track_info(info)
    
    def _show_track_info(self, info: dict):
        """Muestra información de un track individual."""
        table = Table(title="🎵 Información del Track", show_header=False, border_style="cyan")
        table.add_column("Campo", style="bold cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("Título", info.get('title', 'N/A'))
        table.add_row("Artista", info.get('uploader', 'N/A'))
        table.add_row("Duración", self._format_duration(info.get('duration', 0)))
        table.add_row("Género", info.get('genre', 'N/A'))
        table.add_row("Reproducciones", f"{info.get('view_count', 0):,}")
        table.add_row("Likes", f"{info.get('like_count', 0):,}")
        table.add_row("Fecha", info.get('upload_date', 'N/A'))
        table.add_row("URL", info.get('webpage_url', 'N/A'))
        
        console.print(table)
    
    def _show_playlist_info(self, info: dict):
        """Muestra información de una playlist."""
        panel_content = f"""
[bold cyan]Título:[/bold cyan] {info.get('title', 'N/A')}
[bold cyan]Autor:[/bold cyan] {info.get('uploader', 'N/A')}
[bold cyan]Cantidad de tracks:[/bold cyan] {len(info.get('entries', []))}
        """
        console.print(Panel(panel_content, title="🎶 Información de la Playlist", border_style="cyan"))
        
        entries = info.get('entries', [])
        if entries:
            table = Table(title="Tracks en la Playlist", border_style="green")
            table.add_column("#", style="dim", width=4)
            table.add_column("Título", style="white")
            table.add_column("Artista", style="cyan")
            table.add_column("Duración", style="green")
            
            for i, entry in enumerate(entries[:20], 1):
                if entry:
                    table.add_row(
                        str(i),
                        entry.get('title', 'N/A')[:50],
                        entry.get('uploader', 'N/A')[:30],
                        self._format_duration(entry.get('duration', 0))
                    )
            
            if len(entries) > 20:
                table.add_row("...", f"... y {len(entries) - 20} más", "", "")
            
            console.print(table)
    
    def _format_duration(self, seconds: int) -> str:
        """Formatea duración en segundos a MM:SS."""
        if not seconds:
            return "N/A"
        minutes, secs = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    def download(self, url: str) -> bool:
        """Descarga una URL (track o playlist)."""
        opts = self._get_ydl_opts()
        
        with console.status("[bold green]Analizando URL..."):
            info = self.get_info(url)
        
        if not info:
            return False
        
        is_playlist = '_type' in info and info['_type'] == 'playlist'
        entries = info.get('entries', [info]) if is_playlist else [info]
        total_tracks = len(entries)
        
        console.print(f"\n[bold green]📥 Descargando {'playlist' if is_playlist else 'track'}...[/bold green]")
        console.print(f"[dim]Destino: {self.output_dir.absolute()}[/dim]\n")
        
        success_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            self.progress = progress
            
            for i, entry in enumerate(entries, 1):
                if entry is None:
                    continue
                    
                title = entry.get('title', 'Unknown')[:40]
                track_url = entry.get('url') or entry.get('webpage_url') or url
                
                self.task_id = progress.add_task(
                    f"[cyan][{i}/{total_tracks}][/cyan] {title}...",
                    total=100
                )
                
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        ydl.download([track_url])
                    success_count += 1
                    progress.update(self.task_id, completed=100)
                except Exception as e:
                    progress.update(self.task_id, description=f"[red]✗ {title}[/red]")
                    console.print(f"[red]   Error: {e}[/red]")
                
                progress.remove_task(self.task_id)
        
        self.progress = None
        
        console.print(f"\n[bold green]✓ Descarga completada: {success_count}/{total_tracks} tracks[/bold green]")
        console.print(f"[dim]Archivos guardados en: {self.output_dir.absolute()}[/dim]")
        
        return success_count > 0
    
    def search(self, query: str, limit: int = 10) -> list:
        """Busca en SoundCloud y muestra resultados."""
        search_url = f"scsearch{limit}:{query}"
        
        with console.status("[bold green]Buscando en SoundCloud..."):
            info = self.get_info(search_url)
        
        if not info or 'entries' not in info:
            console.print("[yellow]No se encontraron resultados.[/yellow]")
            return []
        
        results = [e for e in info['entries'] if e is not None]
        
        if not results:
            console.print("[yellow]No se encontraron resultados.[/yellow]")
            return []
        
        table = Table(title=f"🔍 Resultados de búsqueda: '{query}'", border_style="magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Título", style="white", max_width=40)
        table.add_column("Artista", style="cyan", max_width=25)
        table.add_column("Duración", style="green", width=10)
        table.add_column("URL", style="dim", max_width=50)
        
        for i, entry in enumerate(results, 1):
            table.add_row(
                str(i),
                entry.get('title', 'N/A')[:40],
                entry.get('uploader', 'N/A')[:25],
                self._format_duration(entry.get('duration', 0)),
                entry.get('webpage_url', 'N/A')
            )
        
        console.print(table)
        return results


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos."""
    parser = argparse.ArgumentParser(
        prog='soundcloud-dl',
        description='🎵 Descarga música de SoundCloud usando yt-dlp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s https://soundcloud.com/artist/track
  %(prog)s -o musica -f flac https://soundcloud.com/artist/playlist
  %(prog)s --search "lofi hip hop"
  %(prog)s --info https://soundcloud.com/artist
        """
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='URL de SoundCloud (track, playlist o perfil)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='descargas',
        help='Directorio de salida (default: descargas)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=AUDIO_FORMATS,
        default='mp3',
        help='Formato de audio (default: mp3)'
    )
    
    parser.add_argument(
        '-q', '--quality',
        default='320',
        help='Calidad de audio en kbps (default: 320)'
    )
    
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='No agregar metadatos al archivo'
    )
    
    parser.add_argument(
        '--no-thumbnail',
        action='store_true',
        help='No agregar carátula al archivo'
    )
    
    parser.add_argument(
        '--keep-original',
        action='store_true',
        help='Mantener archivo original después de conversión'
    )
    
    parser.add_argument(
        '-i', '--info',
        action='store_true',
        help='Solo mostrar información, no descargar'
    )
    
    parser.add_argument(
        '-s', '--search',
        metavar='QUERY',
        help='Buscar en SoundCloud'
    )
    
    parser.add_argument(
        '--search-limit',
        type=int,
        default=10,
        help='Límite de resultados de búsqueda (default: 10)'
    )
    
    parser.add_argument(
        '-d', '--download-search',
        type=int,
        metavar='N',
        help='Descargar resultado #N de la última búsqueda'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def show_banner():
    """Muestra el banner del programa."""
    banner = """
[bold orange1]╔═══════════════════════════════════════════════╗
║     🎵 SoundCloud Downloader CLI 🎵           ║
║         Powered by yt-dlp                      ║
╚═══════════════════════════════════════════════╝[/bold orange1]
    """
    console.print(banner)


def interactive_mode(downloader: SoundCloudDownloader):
    """Modo interactivo del programa."""
    show_banner()
    console.print("[dim]Escribe 'help' para ver comandos disponibles, 'exit' para salir[/dim]\n")
    
    last_search_results = []
    
    while True:
        try:
            user_input = console.input("[bold cyan]soundcloud-dl>[/bold cyan] ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command in ('exit', 'quit', 'q'):
                console.print("[yellow]¡Hasta luego! 👋[/yellow]")
                break
            
            elif command == 'help':
                help_text = """
[bold cyan]Comandos disponibles:[/bold cyan]
  [green]download <url>[/green]    - Descargar track/playlist
  [green]info <url>[/green]        - Mostrar información
  [green]search <query>[/green]    - Buscar en SoundCloud
  [green]get <número>[/green]      - Descargar resultado de búsqueda
  [green]format <formato>[/green]  - Cambiar formato (mp3, flac, etc.)
  [green]output <ruta>[/green]     - Cambiar directorio de salida
  [green]config[/green]            - Ver configuración actual
  [green]help[/green]              - Mostrar esta ayuda
  [green]exit[/green]              - Salir
                """
                console.print(help_text)
            
            elif command in ('download', 'dl', 'd'):
                if args:
                    downloader.download(args)
                else:
                    console.print("[red]Uso: download <url>[/red]")
            
            elif command == 'info':
                if args:
                    downloader.show_info(args)
                else:
                    console.print("[red]Uso: info <url>[/red]")
            
            elif command == 'search':
                if args:
                    last_search_results = downloader.search(args)
                else:
                    console.print("[red]Uso: search <query>[/red]")
            
            elif command == 'get':
                if args.isdigit():
                    idx = int(args) - 1
                    if 0 <= idx < len(last_search_results):
                        url = last_search_results[idx].get('webpage_url')
                        if url:
                            downloader.download(url)
                    else:
                        console.print("[red]Número de resultado inválido[/red]")
                else:
                    console.print("[red]Uso: get <número>[/red]")
            
            elif command == 'format':
                if args in AUDIO_FORMATS:
                    downloader.audio_format = args
                    console.print(f"[green]Formato cambiado a: {args}[/green]")
                else:
                    console.print(f"[red]Formatos válidos: {', '.join(AUDIO_FORMATS)}[/red]")
            
            elif command == 'output':
                if args:
                    downloader.output_dir = Path(args)
                    downloader.output_dir.mkdir(parents=True, exist_ok=True)
                    console.print(f"[green]Directorio cambiado a: {args}[/green]")
                else:
                    console.print("[red]Uso: output <ruta>[/red]")
            
            elif command == 'config':
                config_table = Table(title="⚙️ Configuración Actual", border_style="blue")
                config_table.add_column("Opción", style="cyan")
                config_table.add_column("Valor", style="white")
                config_table.add_row("Directorio", str(downloader.output_dir.absolute()))
                config_table.add_row("Formato", downloader.audio_format)
                config_table.add_row("Calidad", f"{downloader.audio_quality} kbps")
                config_table.add_row("Metadatos", "Sí" if downloader.add_metadata else "No")
                config_table.add_row("Carátula", "Sí" if downloader.add_thumbnail else "No")
                console.print(config_table)
            
            elif command.startswith('http'):
                downloader.download(user_input)
            
            else:
                console.print(f"[red]Comando no reconocido: {command}[/red]")
                console.print("[dim]Escribe 'help' para ver comandos disponibles[/dim]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Usa 'exit' para salir[/yellow]")
        except EOFError:
            break


def main():
    """Función principal."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        import yt_dlp
    except ImportError:
        console.print("[red]Error: yt-dlp no está instalado[/red]")
        console.print("Instala con: pip install yt-dlp")
        sys.exit(1)
    
    downloader = SoundCloudDownloader(
        output_dir=args.output,
        audio_format=args.format,
        audio_quality=args.quality,
        add_metadata=not args.no_metadata,
        add_thumbnail=not args.no_thumbnail,
        keep_original=args.keep_original
    )
    
    if args.search:
        show_banner()
        results = downloader.search(args.search, args.search_limit)
        
        if args.download_search and results:
            idx = args.download_search - 1
            if 0 <= idx < len(results):
                url = results[idx].get('webpage_url')
                if url:
                    downloader.download(url)
        sys.exit(0)
    
    if args.url:
        show_banner()
        if args.info:
            downloader.show_info(args.url)
        else:
            success = downloader.download(args.url)
            sys.exit(0 if success else 1)
    else:
        interactive_mode(downloader)


if __name__ == '__main__':
    main()