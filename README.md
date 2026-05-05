# Discord Bot Testing

A small Discord bot built with discord.py. It includes:

- A hello command.
- Facebook/Instagram video download and upload via yt-dlp (25 MB limit).

## Commands

- `!hello` - Reply with a greeting.
- `!fb <facebook_or_instagram_video_url>` - Download a Facebook/Instagram video and upload it to Discord.

## Requirements

- Python 3.10+ recommended.
- `discord.py` and `yt-dlp` installed.

## Setup

1. Install dependencies:

   ```bash
   pip install discord.py yt-dlp
   ```


## Notes

- The Facebook/Instagram downloader uses yt-dlp and enforces a 25 MB size limit to stay
  under Discord's upload limit.
- Only public Facebook/Instagram video links will work.
