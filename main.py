import discord 
from discord.ext import commands
from datetime import timedelta
import yt_dlp
import asyncio
import tempfile
import os
from dotenv import load_dotenv
import subprocess
import shutil

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.command()
async def hello(ctx):
    await ctx.send("hello am your bot")

#checking 

print("FFmpeg found:", shutil.which("ffmpeg"))


#Job for videos those are more than 25mb , so we need to compress them


MAX_SIZE = 10 * 1024 * 1024   # 10MB for servers with out any boosts



def get_file_size(path):
    return os.path.getsize(path)


def compress_video(input_path, output_path):

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg not installed or not in PATH")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-vcodec", "libx264",
        "-crf", "32",
        "-preset", "veryfast",
        "-acodec", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-y",
        output_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        # ✅ Print full error so you can see it in Railway logs
        print("FFmpeg STDOUT:", result.stdout)
        print("FFmpeg STDERR:", result.stderr)
        raise RuntimeError(f"FFmpeg compression failed: {result.stderr[-500:]}")


def ensure_under_limit(input_file):
    size = get_file_size(input_file)
    print(f"Original file size: {size/(1024*1024):.2f} MB")

    if size <= MAX_SIZE:
        return input_file

    # ✅ Use temp directory instead of current folder
    compressed_file = os.path.join(
        tempfile.gettempdir(),
        "compressed_" + os.path.basename(input_file)
    )

    compress_video(input_file, compressed_file)

    compressed_size = get_file_size(compressed_file)
    print(f"Compressed file size: {compressed_size/(1024*1024):.2f} MB")

    if compressed_size <= MAX_SIZE:
        return compressed_file

    return None




#caption issue fix er
def trim_caption(text: str, limit: int = 200):
    if not text:
        return "No title"

    if len(text) > limit:
        return text[:limit].rstrip() + "..."
    return text



# Shared Video Downloader
async def download_and_send(source, url: str, platform: str):

    is_interaction = isinstance(source, discord.Interaction)

    if is_interaction:
        await source.response.send_message(
            f"⏳ Downloading {platform} video, please wait..."
        )
        status_msg = await source.original_response()
    else:
        status_msg = await source.send(
            f"⏳ Downloading {platform} video, please wait..."
        )

    ydl_opts = {
    # Best quality
    "format": "bv*+ba/b",

    # Save path
    "outtmpl": os.path.join(
        tempfile.gettempdir(),
        "%(id)s.%(ext)s"
    ),

    # Cleaner console
    "quiet": True,
    "no_warnings": True,

    # Merge to mp4
    "merge_output_format": "mp4",

    # Retry system
    "retries": 10,
    "fragment_retries": 10,
    "extractor_retries": 10,

    # Avoid instant blocking
    "sleep_interval": 2,
    "max_sleep_interval": 5,

    # Better compatibility
    "nocheckcertificate": True,

    # Browser headers
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    },

    # Extractor specific args
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]
        },
        "instagram": {
            "api_version": ["v1"]
        }
    },
}

    loop = asyncio.get_event_loop()

    def download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

            if not os.path.exists(filepath):
                filepath = os.path.splitext(filepath)[0] + ".mp4"

            return filepath, info.get("title", f"{platform} Video")

    filepath = None
    compressed_file = None

    try:
        filepath, title = await loop.run_in_executor(None, download)
        await status_msg.edit(content="📥 Download complete. Checking file size...")
        title = trim_caption(title,200)
        

        # compression
        size = get_file_size(filepath)

        if size > MAX_SIZE:

            await status_msg.edit(content="📦 File too large. Compressing video...")

        final_file = ensure_under_limit(filepath)

        if final_file is None:
            await status_msg.edit(
                content=(
                    "❌ The video is too large even after compression "
                    
                )
            )
            return

        compressed_file = final_file if (final_file and final_file != filepath) else None

        #await status_msg.edit(content=f"✅ **{title}**")

        safe_title = trim_caption(title, 200)
        await status_msg.edit(content=f"✅ Ready: **{safe_title}** (uploading...)")

        file_to_send = discord.File(final_file, filename="video.mp4")

        if is_interaction:
            await source.followup.send(file=file_to_send)
        else:
            await source.send(file=file_to_send)

    except yt_dlp.utils.DownloadError as e:
        await status_msg.edit(
            content=f"❌ Download failed:\n```{str(e)[:200]}```"
        )

    except Exception as e:
        
        await status_msg.edit(
        content=f"❌ Unexpected error: `{str(e)[:300]}`"  # ✅ str(e) shows full message
        )

    finally:
        # cleanup original + compressed
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

            if compressed_file and os.path.exists(compressed_file):
                os.remove(compressed_file)

        except Exception:
            pass
# ────────

# Facebook 
@bot.command()
async def fb(ctx, url: str):
    await download_and_send(ctx, url, "Facebook")
#slash one    
@bot.tree.command(name="fb", description="Download Facebook video")
async def fb(interaction: discord.Interaction, url: str):

    await download_and_send(interaction, url, "Facebook")


#Instagram Reel Command
# Prefix command
@bot.command()
async def insta(ctx, url: str):
    await download_and_send(ctx, url, "Instagram")
#slash one
@bot.tree.command(name="insta", description="Download Instagram reel/video")
async def insta(interaction: discord.Interaction, url: str):

    await download_and_send(interaction, url, "Instagram")




#play any
@bot.command()
async def video(ctx, url: str):

    from urllib.parse import urlparse
    link = url
    domain = urlparse(link).netloc
    platform = domain.replace("www.","").split(".")[0]

    await download_and_send(ctx, url, platform)

#slash one er
@bot.tree.command(name="video", description="Download any supported video")
async def video(interaction: discord.Interaction, url: str):

    from urllib.parse import urlparse
    link = url
    domain = urlparse(link).netloc
    platform = domain.replace("www.","").split(".")[0]

    await download_and_send(interaction, url, platform)


# bot token to connect
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise SystemExit("DISCORD_TOKEN is missing. Add it to your environment or a .env file.")

bot.run(token)