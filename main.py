import os
import subprocess
import datetime
import asyncio
import glob
import yt_dlp
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest
import whisper
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from tqdm import tqdm
import edge_tts


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
FINAL_OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
SOURCE_CHANNEL = os.getenv('SOURCE_CHANNEL')

if SOURCE_CHANNEL and SOURCE_CHANNEL.strip().replace('-', '').isdigit():
    SOURCE_CHANNEL = int(SOURCE_CHANNEL)

print("🔄 Carregando Whisper...")
model = whisper.load_model("base")


def format_timestamp(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds_flat = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds_flat:02d},{milliseconds:03d}"

async def generate_voice_and_srt(audio_path, base_path):
    result = model.transcribe(audio_path, language="en", fp16=False)
    translator = GoogleTranslator(source='en', target='pt')

    srt_path = f"{base_path}.srt"
    full_text = ""

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(tqdm(result["segments"], desc="Traduzindo")):
            translated = translator.translate(seg['text'].strip())
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            f.write(f"{i+1}\n{start} --> {end}\n{translated}\n\n")
            full_text += translated + " "

    dub_audio = f"{base_path}_dub.mp3"
    communicate = edge_tts.Communicate(full_text, "pt-BR-FranciscaNeural")
    await communicate.save(dub_audio)

    return srt_path, dub_audio

def finalize_video(video_in, audio_dub, srt_in, video_out):
    subprocess.run([
        "ffmpeg", "-i", video_in, "-i", audio_dub, "-i", srt_in,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-c:s", "mov_text",
        "-y", video_out
    ])

def baixar_video_youtube(url, diretorio_saida):
    print(f"📥 Verificando e baixando do YouTube: {url}")
    
    ydl_opts = {
        'outtmpl': os.path.join(diretorio_saida, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
    }
    
    arquivos_baixados = []
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        
        if 'entries' in info:
            print(f"📚 Playlist detectada com {len(info['entries'])} vídeos!")
            for entry in info['entries']:
                if entry:
                    filename = ydl.prepare_filename(entry)
                    arquivos_baixados.append(filename)
        else:
            filename = ydl.prepare_filename(info)
            arquivos_baixados.append(filename)
            
    print(f"✅ Download concluído: {len(arquivos_baixados)} vídeo(s) baixado(s).")
    return arquivos_baixados
def progresso_upload(enviado, total):
    porcentagem = (enviado / total) * 100
    print(f"⏳ Progresso do upload: {porcentagem:.2f}% ({enviado}/{total} bytes)", end='\r')

async def obter_ou_criar_canal(client, nome_canal="Vídeos Traduzidos"):
    target_channel = os.getenv('TARGET_CHANNEL')

    if target_channel and target_channel.strip():
        print(f"✅ Usando canal existente configurado no .env.")
        if target_channel.strip().replace('-', '').isdigit():
            target_channel = int(target_channel)
        return await client.get_entity(target_channel)
    else:
        print("⚠️ Nenhum canal de destino configurado. Criando um novo canal automaticamente...")
        try:
            resultado = await client(CreateChannelRequest(
                title=nome_canal,
                about="Canal criado automaticamente pelo bot de tradução.",
                megagroup=False
            ))
            novo_canal = resultado.chats[0]
            print(f"🎉 Canal '{nome_canal}' criado com sucesso! ID: {novo_canal.id}")
            print(f"💡 DICA: Adicione TARGET_CHANNEL={novo_canal.id} no seu arquivo .env para reutilizar o canal.")
            return novo_canal
        except Exception as e:
            print(f"❌ Erro ao criar o canal: {e}")
            return None

async def main():
    youtube_url = input("🔗 Cole o link do YouTube (ou pressione Enter para usar vídeos locais): ")

    videos_para_processar = []

    if youtube_url.strip():
        videos_baixados = baixar_video_youtube(youtube_url, LOCAL_VIDEOS_DIR)
        videos_para_processar.extend(videos_baixados)
    else:
        videos_para_processar = sorted(glob.glob(os.path.join(LOCAL_VIDEOS_DIR, "*.mp4")))

    for video_in in videos_para_processar:
        nome_base = os.path.splitext(os.path.basename(video_in))[0]
        caminho_base_temp = os.path.join(TEMP_DIR, nome_base)
        video_out = os.path.join(FINAL_OUTPUT_DIR, f"{nome_base}_final.mp4")

        print(f"⚙️ Processando: {video_in}")
        
        srt_path, dub_audio = await generate_voice_and_srt(video_in, caminho_base_temp)
        
        print("🎬 Finalizando edição do vídeo...")
        finalize_video(video_in, dub_audio, srt_path, video_out)

        print("Conectando ao Telegram para envio...")
        client = TelegramClient('session', API_ID, API_HASH)
        await client.start(phone=PHONE_NUMBER)

        canal = await obter_ou_criar_canal(client, nome_canal="Meus Vídeos Traduzidos")
        
        if canal:
            print("📤 Iniciando envio para o Telegram...")
            await client.send_file(
                canal, 
                video_out, 
                caption=f"Vídeo traduzido: {nome_base}",
                supports_streaming=True,
                progress_callback=progresso_upload
            )
            print("\n✅ Enviado com sucesso!\n")
        else:
            print("❌ Falha ao obter/criar o canal. O vídeo não foi enviado.")

        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())