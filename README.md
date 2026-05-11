# Discord Bot Testing

A small Discord bot built with discord.py. It includes:

[![Invite Bot](https://img.shields.io/badge/Invite-Discord%20Bot-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1500747950610055248&permissions=2048&integration_type=0&scope=bot+applications.commands)

- - Facebook/Instagram/YouTube shorts or reels video download  (25 MB limit).

## Commands

- `!hello` - Reply with a greeting.
- `!fb <facebook_video_url>` - Download a Facebook video and upload it to Discord.
- `!insta <instagram_video_url>` - Download a Instagram video and upload it to Discord.
- `!video` - Download any type of videos.

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
