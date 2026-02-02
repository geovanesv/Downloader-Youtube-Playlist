# playlistdownloader.py
import os
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp


class PlaylistDownloader:
    def __init__(self, playlist_path: str, folder_path: str) -> None:
        self.playlist_path = playlist_path
        self.folder_path = folder_path
        self.is_cancelled = False
        self.archive_path = os.path.join(self.folder_path, 'historico_downloads.txt')

    def cancel(self):
        self.is_cancelled = True

    def _progress_hook(self, d):
        if self.is_cancelled:
            raise yt_dlp.utils.DownloadCancelled()

    def download(self):
        def match_filter(info_dict):
            if self.is_cancelled:
                return "Cancelado pelo usuário"
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

        folder = folder_path.get().strip()

        if not url or not folder:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        download_button.config(state=tk.DISABLED, text="Processando...")
        cancel_button.config(state=tk.NORMAL)

        current_downloader = PlaylistDownloader(url, folder)

        def process_thread():
            try:
                current_downloader.download()

                def finish():
                    if current_downloader.is_cancelled:
                        messagebox.showinfo("Cancelado", "Download cancelado.")
                    else:
                        messagebox.showinfo("Concluído", "Download finalizado!")
                        root.destroy()

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
    root.geometry("600x420")
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

    root.mainloop()


if __name__ == "__main__":
    start_gui()
