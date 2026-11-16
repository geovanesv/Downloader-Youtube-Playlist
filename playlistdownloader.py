# playlistdownloader.py
import os
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import urllib.parse
import yt_dlp


class PlaylistDownloader:
    def __init__(self, playlist_path: str, folder_path: str, progress_callback=None) -> None:
        self.playlist_path = playlist_path
        self.folder_path = folder_path
        self.is_cancelled = False
        self.archive_path = os.path.join(self.folder_path, 'historico_downloads.txt')
        self.progress_callback = progress_callback
        self.current_meta = {'title': 'Iniciando...', 'index': 0, 'total': 0}

    def cancel(self):
        self.is_cancelled = True

    def _progress_hook(self, d):
        if self.is_cancelled:
            raise yt_dlp.utils.DownloadCancelled()
        
        if self.progress_callback:
            # Mescla os dados do hook com os metadados capturados no filtro
            data = d.copy()
            data.update(self.current_meta)
            self.progress_callback(data)

    def download(self):
        def match_filter(info_dict):
            if self.is_cancelled:
                return "Cancelado pelo usuário"
            
            # Captura metadados antes do download começar
            self.current_meta['title'] = info_dict.get('title', 'Desconhecido')
            self.current_meta['index'] = info_dict.get('playlist_index', 0) or 0
            self.current_meta['total'] = info_dict.get('n_entries') or info_dict.get('playlist_count', 0) or 0

            # Ignora entradas que não sejam vídeos (ex: outras playlists aninhadas)
            if info_dict.get('_type') in ('playlist', 'channel', 'multi_video'):
                return "Item ignorado (não é vídeo)"
            return None

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.folder_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ignoreerrors': True,
            'download_archive': self.archive_path,
            'progress_hooks': [self._progress_hook],
            'match_filter': match_filter,
            'noplaylist': False,
            'playlistend': 50,
            'source_address': '0.0.0.0',  # Força IPv4 para evitar bloqueios 403 comuns em IPv6
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.playlist_path])


def start_gui():
    current_downloader = None

    # Pasta padrão (pode mudar à vontade)
    default_folder = os.path.join(os.path.expanduser("~"), "Músicas", "playlists")

    def browse_folder():
        folder = filedialog.askdirectory(initialdir=folder_path.get())
        if folder:
            folder_path.set(folder)

    def cancel_process():
        if current_downloader:
            current_downloader.cancel()
            download_button.config(text="Cancelando...")

    def run_process():
        nonlocal current_downloader

        url = url_entry.get().strip()

        # Sanitização: Corrige links colados duplicados (ex: https://...https://...)
        if "https://" in url:
            first_idx = url.find("https://")
            second_idx = url.find("https://", first_idx + 8)
            if second_idx != -1:
                url = url[first_idx:second_idx]

        # Lógica de tratamento de URL de playlist/mix
        if "list=" in url:
            try:
                parsed = urllib.parse.urlparse(url)
                qs = urllib.parse.parse_qs(parsed.query)
                list_id = qs.get('list', [None])[0]
                video_id = qs.get('v', [None])[0]

                if list_id:
                    # Mixes (RD...) precisam do ID do vídeo para funcionar corretamente
                    if list_id.startswith('RD') and video_id:
                        url = f"https://www.youtube.com/watch?v={video_id}&list={list_id}"
                    # Outras playlists (PL, LL, etc) funcionam melhor diretamente pelo link da playlist
                    else:
                        url = f"https://www.youtube.com/playlist?list={list_id}"
            except Exception:
                pass

        folder = folder_path.get().strip()

        if not url or not folder:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        download_button.config(state=tk.DISABLED, text="Processando...")
        cancel_button.config(state=tk.NORMAL)

        # Resetar UI
        progress_bar['value'] = 0
        status_label.config(text="Iniciando...")
        count_label.config(text="")
        percent_label.config(text="")

        def update_progress(data):
            # Executa na thread principal do Tkinter
            status = data.get('status')
            if status == 'downloading':
                title = data.get('title', 'Desconhecido')
                index = data.get('index', 0)
                total = data.get('total', 0)
                
                # Porcentagem
                total_bytes = data.get('total_bytes') or data.get('total_bytes_estimate') or 0
                downloaded = data.get('downloaded_bytes', 0)
                percent = (downloaded / total_bytes * 100) if total_bytes > 0 else 0

                status_label.config(text=f"Baixando: {title[:50]}..." if len(title) > 50 else f"Baixando: {title}")
                count_label.config(text=f"Música: {index} de {total}" if total else f"Música: {index}")
                percent_label.config(text=f"{percent:.1f}%")
                progress_bar['value'] = percent

        def safe_progress_callback(data):
            root.after(0, update_progress, data)

        current_downloader = PlaylistDownloader(url, folder, progress_callback=safe_progress_callback)

        def process_thread():
            try:
                current_downloader.download()

                def finish():
                    if current_downloader.is_cancelled:
                        messagebox.showinfo("Cancelado", "Download cancelado.")
                    else:
                        messagebox.showinfo("Concluído", "Download finalizado!")
                        progress_bar['value'] = 100
                        status_label.config(text="Concluído!")

                    download_button.config(state=tk.NORMAL, text="Baixar")
                    cancel_button.config(state=tk.DISABLED)

                root.after(0, finish)

            except Exception as e:
                root.after(0, lambda: messagebox.showerror("Erro", str(e)))
                root.after(0, lambda: download_button.config(state=tk.NORMAL, text="Baixar"))
                root.after(0, lambda: cancel_button.config(state=tk.DISABLED))

        Thread(target=process_thread, daemon=True).start()

    # ---------------- GUI ----------------

    root = tk.Tk()
    root.title("🎵 Playlist Downloader")
    root.geometry("600x550")  # Aumentei a altura para caber os novos widgets
    root.configure(bg="#f2f2f2")
    root.resizable(False, False)

    main_frame = tk.Frame(root, bg="white", padx=30, pady=25)
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(
        main_frame,
        text="Playlist Downloader",
        font=("Segoe UI", 18, "bold"),
        bg="white"
    )
    title.pack(pady=(0, 20))

    # URL
    tk.Label(main_frame, text="URL da Playlist", bg="white", anchor="w").pack(fill="x")
    url_entry = tk.Entry(main_frame, width=55)
    url_entry.pack(pady=(5, 15))

    def select_all(event):
        event.widget.select_range(0, 'end')
        event.widget.icursor('end')
        return 'break'
    url_entry.bind("<Control-a>", select_all)

    # Pasta
    tk.Label(main_frame, text="Pasta de Download", bg="white", anchor="w").pack(fill="x")
    folder_path = tk.StringVar(value=default_folder)

    folder_frame = tk.Frame(main_frame, bg="white")
    folder_frame.pack(fill="x", pady=(5, 20))

    tk.Entry(folder_frame, textvariable=folder_path, width=42).pack(side="left")
    tk.Button(
        folder_frame,
        text="📂",
        command=browse_folder,
        relief="flat",
        bg="#e0e0e0",
        width=4
    ).pack(side="left", padx=5)

    # Botões
    buttons_frame = tk.Frame(main_frame, bg="white")
    buttons_frame.pack(pady=10)

    download_button = tk.Button(
        buttons_frame,
        text="Baixar",
        width=15,
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        command=run_process
    )
    download_button.pack(side="left", padx=10)

    cancel_button = tk.Button(
        buttons_frame,
        text="Cancelar",
        width=15,
        bg="#f44336",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        state=tk.DISABLED,
        command=cancel_process
    )
    cancel_button.pack(side="left", padx=10)

    # --- Área de Progresso ---
    progress_frame = tk.Frame(main_frame, bg="white", pady=10)
    progress_frame.pack(fill="x")

    status_label = tk.Label(progress_frame, text="Aguardando...", bg="white", font=("Segoe UI", 9), anchor="w")
    status_label.pack(fill="x")

    stats_frame = tk.Frame(progress_frame, bg="white")
    stats_frame.pack(fill="x", pady=2)

    count_label = tk.Label(stats_frame, text="", bg="white", font=("Segoe UI", 9, "bold"))
    count_label.pack(side="left")

    percent_label = tk.Label(stats_frame, text="", bg="white", font=("Segoe UI", 9, "bold"), fg="#4CAF50")
    percent_label.pack(side="right")

    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
    progress_bar.pack(fill="x", pady=5)

    root.mainloop()


if __name__ == "__main__":
    start_gui()
