# 🎵 YouTube Playlist Downloader & Converter

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Funcional-green?style=for-the-badge)

Uma ferramenta simples e eficiente com interface gráfica (GUI) para baixar playlists inteiras do YouTube e converter automaticamente os vídeos para MP3.

---

## 🚀 Funcionalidades

- **Interface Gráfica:** Fácil de usar, sem necessidade de linha de comando após a instalação.
- **Download em Lote:** Baixa todos os vídeos de uma playlist.
- **Conversão Automática:** Converte arquivos `.mp4` para `.mp3`.
- **Multithreading:** Utiliza múltiplas threads para downloads e conversões mais rápidas.

---

## 💻 Instalação e Uso

### 🐧 Linux (Ubuntu/Debian e derivados)

Devido às políticas de segurança recentes do Linux (PEP 668), recomendamos o uso de um ambiente virtual.

1. **Instale as dependências do sistema:**

   ```bash
   sudo apt update
   sudo apt install python3-venv python3-tk ffmpeg
   ```

2. **Crie e ative o ambiente virtual na pasta do projeto:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as bibliotecas necessárias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o programa:**
   ```bash
   python playlistdownloader.py
   ```
   _(Nota: Sempre que abrir um novo terminal, execute `source venv/bin/activate` antes de rodar o programa)._

---

### 🪟 Windows

1. **Certifique-se de ter o Python instalado.** (Marque a opção "Add Python to PATH" durante a instalação).

2. **Abra o CMD ou PowerShell na pasta do projeto e instale as dependências:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Execute o programa:**
   ```powershell
   python playlistdownloader.py
   ```

---

## 🛠️ Como Usar

1. Abra o programa.
2. Cole o **link da Playlist** do YouTube no primeiro campo.
3. Clique em **Selecionar** e escolha a pasta onde deseja salvar as músicas.
4. Clique em **Baixar** e aguarde o processo terminar. Uma mensagem de sucesso aparecerá ao final.
5. Caso queira cancelar basta clicar em ccancelar ou fechar a janela.

---

<div align="center">
  <sub style="font-size: 16px;">Desenvolvido por <strong>Geovane</strong></sub>
  <br /><br />

  <a href="https://www.linkedin.com/in/geovanesaraujo/" target="_blank">
    <img src="https://img.shields.io/badge/-LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  &nbsp;
  <a href=" https://geovanearaujo.dev.br/" target="_blank">
    <img src="https://img.shields.io/badge/-Portfólio-000000?style=for-the-badge&logo=About.me&logoColor=white" alt="Portfólio">
  </a>
</div>
