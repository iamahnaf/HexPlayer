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


#  Shared Video Downloader
# Shared Video Downloader
async def download_and_send(source, url: str, platform: str):

    is_interaction = isinstance(source, discord.Interaction)

    # Send initial message
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

            await status_msg.edit(
                content=(
                    "❌ The video is too large to upload "
                    "(Discord limit: 25 MB).\n"
                    "Try a shorter clip or lower quality."
                )
            )

        else:
            await status_msg.edit(content=f"✅ **{title}**")

            if is_interaction:
                await source.followup.send(
                    file=discord.File(filepath, filename="video.mp4")
                )
            else:
                await source.send(
                    file=discord.File(filepath, filename="video.mp4")
                )

    except yt_dlp.utils.DownloadError as e:

        await status_msg.edit(
            content=(
                f"❌ Could not download the {platform} video.\n"
                f"```{str(e)[:200]}```"
            )
        )

    except Exception as e:

        await status_msg.edit(
            content=f"❌ Unexpected error: `{e}`"
        )

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

    listofwordsFromURL = url.split('/')
    domain = listofwordsFromURL[2].split(".")

    await download_and_send(ctx, url, domain[1])
#slash one er
@bot.tree.command(name="video", description="Download any supported video")
async def video(interaction: discord.Interaction, url: str):

    listofwordsFromURL = url.split('/')
    domain = listofwordsFromURL[2].split(".")

    await download_and_send(interaction, url, domain[1])


# bot token to connect
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise SystemExit("DISCORD_TOKEN is missing. Add it to your environment or a .env file.")

bot.run(token)