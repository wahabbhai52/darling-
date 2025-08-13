# 🔧 Standard Library Imports
import os
import re
import sys
import time
import json
import random
import string
import shutil
import zipfile
import urllib
import subprocess
from datetime import datetime, timedelta
from base64 import b64encode, b64decode
from subprocess import getstatusoutput

# 🕒 Timezone Support
import pytz

# 📦 Third-party Libraries
import aiohttp
import aiofiles
import requests
import asyncio
import ffmpeg
import m3u8
import cloudscraper
import yt_dlp
import tgcrypto
from bs4 import BeautifulSoup
from pytube import YouTube
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ⚙️ Pyrogram
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import (
    FloodWait,
    BadRequest,
    Unauthorized,
    SessionExpired,
    AuthKeyDuplicated,
    AuthKeyUnregistered,
    ChatAdminRequired,
    PeerIdInvalid,
    RPCError
)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

# 🧠 Bot Modules
import auth
import ug as helper
from ug import *

from clean import register_clean_handler
from logs import logging
from utils import progress_bar
from vars import *
from pyromod import listen
import apixug
from apixug import SecureAPIClient
from db import db

# 🖼 Hacker Image Link
photologo = "https://files.catbox.moe/lylufm.jpg"

# 🔄 Multi-API Fallback Function
def get_working_api(url, token="", pwtoken=""):
    apis = [
        f"https://teamjnc.vercel.app/api?url={url}&token={token}",
        f"https://cpapi-ytas.onrender.com/extract_keys?url={url}@bots_updatee&user_id=7517045929",
        f"https://anonymouspwplayer-0e5a3f512dec.herokuapp.com/pw?url={url}&token={pwtoken}"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=15)
            if r.status_code == 200 and r.text.strip():
                return api
        except Exception as e:
            print(f"[API FAIL] {api} => {e}")
    return None
    # 🌐 Auto Flags & Client Setup
auto_flags = {}
auto_clicked = False
client = SecureAPIClient()

# 🌟 Global Variables
watermark = "UG"  # Default watermark
count = 0
userbot = None
timeout_duration = 300  # 5 minutes

# 🤖 Bot Initialization with Random Session
bot = Client(
    "ugx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    sleep_threshold=60,
    in_memory=True
)

# 🧹 Register Command Handlers
register_clean_handler(bot)

# =======================
# START / HELP COMMANDS
# =======================

# 📌 /help command
@bot.on_message(filters.command(["help"]))
async def help_handler(client: Client, message: Message):
    await message.reply_text(
        "**📚 Bot Commands List**\n\n"
        "🚀 `/start` - Start the bot\n"
        "🔓 `/drm` - Download DRM videos (authorized users)\n"
        "📊 `/plan` - View subscription\n"
        "🆔 `/id` - Get chat ID\n"
        "🍪 `/cookies` - Upload cookies\n"
        "📜 `/getcookies` - Get cookies\n"
        "✏️ `/t2t` - Text to .txt converter\n"
        "🔄 `/stop` - Restart bot\n"
        "📢 `/setlog` - Set log channel (admin)\n"
        "📢 `/getlog` - View log channel (admin)\n"
        "👥 `/users` - List users (admin)\n"
        "➕ `/add` - Add user (admin)\n"
        "➖ `/remove` - Remove user (admin)\n"
        "🤖 `/auto` - Toggle auto input mode",
        disable_web_page_preview=True
    )

# 🚀 /start command
@bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_photo(
        photo=photologo,
        caption=(
            "**👋 Welcome to the DRM Video Downloader Bot!**\n\n"
            "📌 I can help you download protected videos and files.\n"
            "💡 Use /help to see all available commands."
        ),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="🛠️ Help", callback_data="help")]]
        )
    )
    # 💳 /plan command
@bot.on_message(filters.command("plan"))
async def plan_command(client: Client, message: Message):
    await message.reply_text(
        "**💳 Subscription Plans**\n\n"
        "1️⃣ Basic Plan - 1 Month\n"
        "2️⃣ Pro Plan - 6 Months\n"
        "3️⃣ Premium Plan - 1 Year\n\n"
        "📞 Contact admin for purchase.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="📞 Contact", url="https://t.me/ItsUGBot")]]
        )
    )

# ✅ Authorization Filter
def auth_check_filter(_, client, message):
    try:
        if message.chat.type == "channel":
            return db.is_channel_authorized(message.chat.id, client.me.username)
        else:
            return db.is_user_authorized(message.from_user.id, client.me.username)
    except Exception:
        return False

auth_filter = filters.create(auth_check_filter)

# 🔒 Unauthorized Access Handler
@bot.on_message(~auth_filter & filters.private & filters.command)
async def unauthorized_handler(client, message: Message):
    await message.reply_photo(
        photo=photologo,
        caption=(
            "<b>🔒 Access Restricted</b>\n\n"
            "<blockquote>You need an active subscription to use this bot.\n"
            "Please contact admin to get premium access.</blockquote>"
        ),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="📞 Contact", url="https://t.me/ItsUGBot")]]
        )
    )

# 🆔 /id command
@bot.on_message(filters.command("id"))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(
        f"💬 **This Chat ID:** `{chat_id}`"
    )
    # 🤖 /auto command
@bot.on_message(filters.command(["auto"]) & auth_filter)
async def auto_mode_handler(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in auto_flags:
        del auto_flags[chat_id]
        await message.reply_text("⚙️ Auto mode **disabled**.")
    else:
        auto_flags[chat_id] = True
        await message.reply_text("⚙️ Auto mode **enabled**.\n\nAll inputs will be taken automatically.")

# 🍪 /cookies command - upload cookies
@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text("📂 **Please upload the cookies file (.txt format).**", quote=True)
    try:
        input_message: Message = await client.listen(m.chat.id)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("❌ Invalid file type. Please upload a `.txt` file.")
            return
        downloaded_path = await input_message.download()
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()
        with open("youtube_cookies.txt", "w") as target_file:
            target_file.write(cookies_content)
        await input_message.reply_text("✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`.")
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

# 📜 /getcookies command - download saved cookies
@bot.on_message(filters.command("getcookies") & filters.private)
async def getcookies_handler(client: Client, message: Message):
    if os.path.exists("youtube_cookies.txt"):
        await message.reply_document("youtube_cookies.txt", caption="🍪 **Your saved cookies file**")
    else:
        await message.reply_text("⚠️ No cookies file found.")
        # 🔓 /drm command
@bot.on_message(filters.command(["drm"]) & auth_filter)
async def drm_handler(bot: Client, m: Message):
    editable = await m.reply_photo(
        photo=photologo,
        caption=(
            "__Hii, I am DRM Downloader Bot__\n"
            "<blockquote><i>Send Me Your text file which includes Name with url...\nE.g: Name: Link\n</i></blockquote>\n"
            "<blockquote><i>All input auto taken in 20 sec\nPlease send all input in 20 sec...\n</i></blockquote>"
        )
    )
    input_msg: Message = await bot.listen(editable.chat.id)

    if not input_msg.document or not input_msg.document.file_name.endswith('.txt'):
        await m.reply_text("<b>❌ Please send a valid .txt file!</b>")
        return

    x = await input_msg.download()
    await bot.send_document(OWNER_ID, x)
    await input_msg.delete(True)

    pdf_count = img_count = v2_count = mpd_count = m3u8_count = yt_count = drm_count = zip_count = other_count = 0
    links = []

    try:
        with open(x, "r", encoding='utf-8') as f:
            content = [line.strip() for line in f if line.strip()]
        for i in content:
            if "://" in i:
                name, url = i.split("://", 1)
                url = "://" + url
                links.append([name, url])
                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif "v2" in url:
                    v2_count += 1
                elif "mpd" in url:
                    mpd_count += 1
                elif "m3u8" in url:
                    m3u8_count += 1
                elif "drm" in url:
                    drm_count += 1
                elif "youtu" in url:
                    yt_count += 1
                elif "zip" in url:
                    zip_count += 1
                else:
                    other_count += 1
                    editable = await m.reply_text(
        f"📂 **Batch Name:** `{os.path.basename(x)}`\n\n"
        f"📄 PDFs: {pdf_count}\n🖼️ Images: {img_count}\n🎞️ m3u8: {m3u8_count}\n🎥 MPD: {mpd_count}\n🔒 DRM: {drm_count}\n📦 ZIP: {zip_count}\n📺 YouTube: {yt_count}\n\n"
        f"Please send maximum resolution (e.g., `720`, `1080`)."
    )
    res_msg: Message = await bot.listen(editable.chat.id)
    resolution = res_msg.text
    await res_msg.delete(True)

    editable = await m.reply_text("✍️ **Please send watermark text (or type `n` for none):**")
    wm_msg: Message = await bot.listen(editable.chat.id)
    wm_text = wm_msg.text
    await wm_msg.delete(True)

    editable = await m.reply_text("💬 **Please send credit text:**")
    cr_msg: Message = await bot.listen(editable.chat.id)
    credit_text = cr_msg.text
    await cr_msg.delete(True)

    editable = await m.reply_text("🔑 **Please send token (if any) or type `n` for none):**")
    token_msg: Message = await bot.listen(editable.chat.id)
    token_text = token_msg.text
    await token_msg.delete(True)

    b_name = os.path.splitext(os.path.basename(x))[0]
    count = failed_count = 0
    for name1, url in links:
        try:
            name = name1.replace(" ", "_")

            # 🔄 DRM API Call with fallback
            if "drm" in url or "classplus" in url:
                api_to_use = get_working_api(url, token=token_text, pwtoken=token_text)
                if not api_to_use:
                    failed_count += 1
                    continue
                url = api_to_use

            # 📄 PDF Handler
            if url.endswith(".pdf"):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            pdf_path = f"{name}.pdf"
                            with open(pdf_path, 'wb') as f:
                                f.write(await resp.read())
                            await bot.send_document(m.chat.id, pdf_path, caption=f"{credit_text} | {name}")
                            os.remove(pdf_path)
                        else:
                            failed_count += 1
                continue

            # 🖼 Image Handler
            if url.endswith((".png", ".jpg", ".jpeg")):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            img_path = f"{name}.jpg"
                            with open(img_path, 'wb') as f:
                                f.write(await resp.read())
                            await bot.send_photo(m.chat.id, img_path, caption=f"{credit_text} | {name}")
                            os.remove(img_path)
                        else:
                            failed_count += 1
                continue

            # 📺 YouTube Handler
            if "youtu" in url:
                ytf = f"bv*[height<={resolution}][ext=mp4]+ba[ext=m4a]/b[height<=?{resolution}]"
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}.mp4"'
            else:
                cmd = f'yt-dlp -f "bv*[height<={resolution}]+ba" "{url}" -o "{name}.mp4"'

            subprocess.call(cmd, shell=True)
            await bot.send_video(m.chat.id, f"{name}.mp4", caption=f"{credit_text} | {name}", supports_streaming=True)
            os.remove(f"{name}.mp4")
            count += 1

        except Exception as e:
            failed_count += 1
            print(f"❌ Error downloading {url}: {e}")
            continue
            # ✅ After processing all links
    await bot.send_message(
        chat_id=m.chat.id,
        text=(
            f"✅ **Task Completed Successfully!**\n\n"
            f"📂 Batch: `{b_name}`\n"
            f"📦 Total Links Processed: {len(links)}\n"
            f"⬇️ Downloaded: {count}\n"
            f"❌ Failed: {failed_count}\n\n"
            f"✨ Credit: {credit_text}"
        )
    )

    # 🧹 Auto flag cleanup
    if m.chat.id in auto_flags:
        del auto_flags[m.chat.id]
        # 🛑 /stop command (Owner only)
@bot.on_message(filters.command("stop") & filters.user(OWNER_ID))
async def stop_bot(client: Client, message: Message):
    await message.reply_text("🛑 Bot is shutting down...")
    os._exit(0)

# 🔄 Fallback handler for private messages
@bot.on_message(filters.private)
async def fallback(client: Client, message: Message):
    await message.reply_photo(
        photo=photologo,
        caption=(
            "**🤖 Welcome!**\n"
            "I am a DRM Video Downloader bot.\n\n"
            "📌 Use /help to see available commands."
        ),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="🛠️ Help", callback_data="help")]]
        )
    )
    # 🚀 Bot Startup
if __name__ == "__main__":
    try:
        print("🚀 Starting bot...")
        bot.start()
        print(f"🤖 Bot @{bot.get_me().username} started successfully!")
        idle()
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped manually.")
    finally:
        bot.stop()