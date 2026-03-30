# Tradutor e Dublador Automático de Vídeos (YouTube + Telegram)

Este projeto automatiza o processo de **download, transcrição, tradução e dublagem de vídeos**, integrando o YouTube e o Telegram com ferramentas de inteligência artificial.

## Principais Recursos

* **Suporte ao YouTube:** Baixe vídeos únicos ou **playlists inteiras** colando apenas o link.
* **Nomes Originais:** O sistema preserva o título original do YouTube em todas as etapas e arquivos processados.
* **Criação Automática de Canal:** Se você não tiver um canal de destino configurado, o bot cria um canal no Telegram automaticamente para salvar seus vídeos traduzidos.
* **Barra de Progresso:** Acompanhe o status do envio (upload) do vídeo para o Telegram em tempo real no terminal.
* **Suporte a Vídeos Locais:** Permite processar vídeos em lote salvos diretamente no seu computador.

---

## Fluxo de Funcionamento

Link do YouTube ou Vídeo Local (.mp4) → Download (yt-dlp) → Extração de áudio → Transcrição (Whisper) → Tradução (EN → PT-BR) → Dublagem (Edge TTS) → Legendas (.srt) → Renderização (FFmpeg) → Envio para o Telegram (Telethon)

---

## Tecnologias Utilizadas

* Python 3.10+
* yt-dlp (Download do YouTube)
* Whisper (Transcrição)
* Deep Translator (Tradução)
* Edge TTS (Geração de Voz)
* FFmpeg (Edição e Renderização)
* Telethon (Automação do Telegram)

---

## Estrutura do Projeto

```text
├── videos/          # Vídeos originais ou baixados ficam aqui
├── output/          # Vídeos finais traduzidos e dublados
├── temp/            # Arquivos temporários (áudios, legendas)
├── main.py          # Script principal
├── requirements.txt # Dependências do projeto
├── .env             # Suas credenciais e configurações
└── README.md
```

## Configuração do Ambiente

### 1. Clonar o repositório
```bash
git clone [https://github.com/dsnasciimento/translate_videos.git](https://github.com/dsnasciimento/translate_videos.git)
```

### 2. Criar e ativar o ambiente virtual
```bash
python -m venv venv
```

**No Windows:**
```bash
venv\Scripts\activate
```

**No Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependências
Execute no terminal:
```bash
pip install -r requirements.txt
```

---

## Configuração do .env (Telegram API)
Este projeto utiliza a API do Telegram via Telethon. Para isso, você precisa criar suas credenciais.

### 1. Criar credenciais no Telegram
##### 1. Acesse: https://my.telegram.org
##### 2. Faça login com seu número de telefone.
##### 3. Clique em **API development tools**.
##### 4. Preencha os campos App title e Short name (pode ser qualquer nome).
##### 5. Após concluir, você receberá o **API_ID** e o **API_HASH**.

### 2. Criar o arquivo de ambiente
Na raiz do projeto, crie um arquivo chamado `.env` e adicione as seguintes informações:

```env
API_ID=seu_api_id
API_HASH=seu_api_hash
PHONE_NUMBER=seu_numero_com_ddi
TARGET_CHANNEL=
```

### 3. Explicação das variáveis
* **API_ID:** ID da aplicação do Telegram.
* **API_HASH:** Hash da aplicação.
* **PHONE_NUMBER:** Seu número de telefone com código do país (ex: +5511999999999).
* **TARGET_CHANNEL:** ID do canal para onde os vídeos prontos serão enviados (ex: -1001234567890). **Dica:** Se você deixar em branco, o bot criará um canal chamado "Meus Vídeos Traduzidos" automaticamente e você poderá copiar o ID gerado para usar nas próximas vezes!

---

## Instalação do FFmpeg (Obrigatório)
O FFmpeg é essencial para extrair o áudio, mesclar a dublagem com o vídeo final e embutir as legendas.

### Verificar instalação
Para checar se o FFmpeg já está instalado, execute:

```bash
ffmpeg -version
```

### Windows
##### 1. Baixe os arquivos binários em: https://ffmpeg.org/download.html
##### 2. Extraia o conteúdo baixado.
##### 3. Copie o caminho da pasta `bin`.
##### 4. Adicione o caminho às variáveis de ambiente (PATH) do seu sistema.

### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

### Mac
```bash
brew install ffmpeg
```

---

## Como Usar

### 1. Execute o script principal:
```bash
python main.py
```

### 2. O terminal fará a seguinte pergunta:
```text
🔗 Cole o link do YouTube (ou pressione Enter para usar vídeos locais): 
```

### 3. **Opção A (YouTube):** Cole o link de um vídeo ou de uma playlist do YouTube. O script fará o download, processará os vídeos e os enviará para o Telegram.
### 4. **Opção B (Local):** Apenas pressione `Enter`. O script processará qualquer vídeo `.mp4` que você tiver colocado manualmente na pasta `/videos`.

O vídeo final traduzido e dublado também estará disponível fisicamente na pasta `/output`.

---

## Observações Importantes

* O processo substitui o áudio original do vídeo pelo áudio dublado gerado na IA.
* É estritamente necessário que o FFmpeg esteja configurado no PATH do seu sistema operacional.
* O script requer conexão ativa com a internet para baixar do YouTube, se comunicar com o Telegram, realizar as traduções e gerar as vozes.
* Tarefas muito longas (como processar vídeos grandes) podem demorar. O bot se reconectará automaticamente ao Telegram na etapa de envio final para evitar quedas de conexão (`TimeoutError`).