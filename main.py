import discord 
from discord.ext import commands
from datetime import timedelta
import yt_dlp
import asyncio
import tempfile
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("hello am your bot")


# ─── Shared Video Downloader ──────────────────────────────────────────────────
async def download_and_send(ctx, url: str, platform: str):
    """Download a video from the given URL and upload it to Discord.
    Works for any platform supported by yt-dlp (Facebook, Instagram, etc.)
    """
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
# ─────────────────────────────────────────────────────────────────────────────


# ─── Facebook Video Command ───────────────────────────────────────────────────
@bot.command()
async def fb(ctx, url: str):
    """Download a Facebook video and send it in Discord.
    Usage: !fb <facebook_video_url>
    """
    await download_and_send(ctx, url, "Facebook")
# ─────────────────────────────────────────────────────────────────────────────


# ─── Instagram Reel Command ───────────────────────────────────────────────────
@bot.command()
async def insta(ctx, url: str):
    """Download an Instagram Reel (or post video) and send it in Discord.
    Usage: !insta <instagram_reel_url>

    Note: Only PUBLIC Instagram accounts work without login.
    For private accounts, cookies would be required.
    """
    await download_and_send(ctx, url, "Instagram")
# ─────────────────────────────────────────────────────────────────────────────


# code for nickname changing
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, new_nick=None):
    try:
        await member.edit(nick=new_nick)
        if new_nick:
            await ctx.send(f"Changed nickname of {member.mention} to {new_nick}")
        else:
            await ctx.send(f"Reset nickname of {member.mention}")
    except discord.Forbidden:
        await ctx.send("I don't have the permission to change this user's nickname")


# code for timing out a member
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, min: int):
    try:
        duration = timedelta(minutes=min)
        await member.timeout(duration)
        await ctx.send(f"Timed out {member.mention} for {min} minutes.")
    except discord.Forbidden:
        await ctx.send("I don't have permissions to timeout this user")


# bot token to connect

bot.run(os.getenv("DISCORD_TOKEN"))