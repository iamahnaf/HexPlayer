import discord 
from discord.ext import commands
from datetime import timedelta
import yt_dlp
import os
import asyncio
import tempfile

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("hello am your bot")

# ─── Facebook Video Command ───────────────────────────────────────────────────
@bot.command()
async def fb(ctx, url: str):
    """Download a Facebook video and send it directly in Discord.
    Usage: !fb <facebook_video_url>
    """
    status_msg = await ctx.send("⏳ Downloading video, please wait...")

    # yt-dlp options — cap at 25 MB to stay under Discord's upload limit
    ydl_opts = {
        "format": "best[filesize<25M]/best",      # prefer a single file under 25 MB
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
            # yt-dlp may change extension after merging
            if not os.path.exists(filepath):
                filepath = os.path.splitext(filepath)[0] + ".mp4"
            return filepath, info.get("title", "Facebook Video")

    try:
        filepath, title = await loop.run_in_executor(None, download)

        file_size = os.path.getsize(filepath)

        if file_size > 25 * 1024 * 1024:          # 25 MB hard limit for Discord
            await status_msg.edit(content=(
                "❌ The video is too large to upload (Discord limit: 25 MB).\n"
                "Try a shorter clip or check if the video has a lower-quality option."
            ))
        else:
            await status_msg.edit(content=f"✅ **{title}**")
            await ctx.send(file=discord.File(filepath, filename="video.mp4"))

    except yt_dlp.utils.DownloadError as e:
        await status_msg.edit(content=(
            f"❌ Could not download the video.\n"
            f"Make sure the link is a **public** Facebook video.\n"
            f"```{str(e)[:200]}```"
        ))
    except Exception as e:
        await status_msg.edit(content=f"❌ Unexpected error: `{e}`")
    finally:
        # Clean up the temp file
        try:
            if "filepath" in dir() and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
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
bot.run("MTUwMDc0Nzk1MDYxMDA1NTI0OA.GJgMqw.IdDUj-y0Exy4umUkSWt7PZBFBlPwhlJkDpLPEY")