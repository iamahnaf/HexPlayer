import discord 
from discord.ext import commands
from datetime import timedelta
import yt_dlp
import asyncio
import tempfile
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("hello am your bot")


#  Shared Video Downloader
async def download_and_send(ctx, url: str, platform: str):
    
    status_msg = await ctx.send(f"⏳ Downloading {platform} video, please wait...")

    ydl_opts = {
        "format": "best[filesize<25M]/best",
        "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
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
    try:
        filepath, title = await loop.run_in_executor(None, download)

        file_size = os.path.getsize(filepath)

        if file_size > 25 * 1024 * 1024:
            await status_msg.edit(content=(
                f"❌ The video is too large to upload (Discord limit: 25 MB).\n"
                f"Try a shorter clip or a lower-quality version."
            ))
        else:
            await status_msg.edit(content=f"✅ **{title}**")
            await ctx.send(file=discord.File(filepath, filename="video.mp4"))

    except yt_dlp.utils.DownloadError as e:
        await status_msg.edit(content=(
            f"❌ Could not download the {platform} video.\n"
            f"Make sure the link is **public** and valid.\n"
            f"```{str(e)[:200]}```"
        ))
    except Exception as e:
        await status_msg.edit(content=f"❌ Unexpected error: `{e}`")
    finally:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
# ────────

# Facebook 
@bot.command()
async def fb(ctx, url: str):
   
    await download_and_send(ctx, url, "Facebook")
# ─────────────────────────────────────────────────────────────────────────────


#Instagram Reel Command
@bot.command()
async def insta(ctx, url: str):
    
    await download_and_send(ctx, url, "Instagram")
# ─────────────────────────────────────────────────────────────────────────────
#play any
@bot.command()
async def video(ctx, url: str):
    listofwordsFromURL = url.split('/')
    domain = listofwordsFromURL[2].split(".")
    
    await download_and_send(ctx, url, domain[1])



# bot token to connect
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise SystemExit("DISCORD_TOKEN is missing. Add it to your environment or a .env file.")

bot.run(token)