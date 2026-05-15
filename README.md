# Discord Bot Testing

A small Discord bot built with `discord.py` that allows users to download and share videos directly in Discord. It also includes **automatic video compression** to handle Discord upload limits.

[![Invite Bot](https://img.shields.io/badge/Invite-Discord%20Bot-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1500747950610055248&permissions=2048&integration_type=0&scope=bot)

---

## 🚀 Features

- Download videos from Facebook, Instagram, YouTube Shorts, and Reels
- Automatic video compression for large files
- Smart file handling to stay within Discord upload limits
- Easy-to-use commands

---

## 📌 Commands

- `!video <url>` → Downloads and processes any supported video link  
- `!fb <facebook_video_url>` → Downloads a Facebook video  
- `!insta <instagram_video_url>` → Downloads an Instagram video
- 
---

## ⚙️ Requirements

- Python 3.10+
- `discord.py`
- `yt-dlp`
- FFmpeg (required for video processing & compression)

---

## 📦 Installation

Install required Python packages:

```bash
pip install discord.py yt-dlp
