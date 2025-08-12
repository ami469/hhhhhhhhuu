from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
import asyncio, time, logging

# Konfigurasi API (isi sesuai akun kamu)
api_id = 20518796      # Ganti dengan API ID kamu
api_hash = 'c3c628644ca8025ed82feb3150ca80d5'  # Ganti dengan API Hash kamu

client = TelegramClient('promo_pro_session', api_id, api_hash)

# Variabel global
promo_text = "🔥 PROMO SPESIAL! Dapatkan penawaran terbaik hari ini!"
promo_enabled = False
promo_delay = 5  # Default delay antar grup (detik)

# Logging ke file
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

@client.on(events.NewMessage(pattern=r"\.help"))
async def help_cmd(event):
    await event.reply(
        "**📘 hallo perkenalkan aku userbot untuk membuat kamu lebih nyaman menggunakan saya , semoga tertarik ya **\n\n"
        "💡 Umum:\n"
        "`• .ping` - Cek kecepatan\n"
        "`• .help` - Bantuan perintah\n"
        "`• .status` - Cek status promosi\n"
        "`• .preview` - Lihat isi promosi\n"
        "`• .setdelay <detik>` - Atur delay antar grup\n\n"
        "📣 Promosi:\n"
        "`• .setpromo <teks>` - Atur teks promosi\n"
        "`• .autopromo on/off` - Hidup/Matikan auto promo\n"
        "`• .promote` - Kirim promosi ke semua grup\n\n"
        "📤 Broadcast:\n"
        "`• .sendall <teks>` - Kirim ke semua grup\n"
        "`• .tagall` - Mention semua member\n"
        "`• .listgroups` - Tampilkan semua grup\n\n"
        "🔗 Grup:\n"
        "`• .join @grup` - Join ke grup publik\n"
        "`• .leave` - Keluar dari grup (reply pesan)\n\n"
        "🆔 User Info:\n"
        "`• .cekid` - Lihat ID dan username kamu"
    )

@client.on(events.NewMessage(pattern=r"\.ping"))
async def ping_cmd(event):
    start = time.time()
    tmp = await event.reply("🔁 Menghitung ping...")
    end = time.time()
    duration = round((end - start) * 1000)
    await tmp.edit(f"✅ **Online**\n⏱️ `Ping: {duration} ms`")

@client.on(events.NewMessage(pattern=r"\.status"))
async def status_cmd(event):
    status = "🟢 AKTIF" if promo_enabled else "🔴 NONAKTIF"
    await event.reply(
        f"📊 **Status Promosi:**\n"
        f"➤ AutoPromo: {status}\n"
        f"➤ Delay: {promo_delay}s\n"
        f"➤ Teks:\n`{promo_text}`"
    )

@client.on(events.NewMessage(pattern=r"\.preview"))
async def preview_cmd(event):
    await event.reply(f"📝 **Teks Promosi Sekarang:**\n\n{promo_text}")

@client.on(events.NewMessage(pattern=r"\.setdelay (\d+)"))
async def set_delay(event):
    global promo_delay
    promo_delay = int(event.pattern_match.group(1))
    await event.reply(f"✅ Delay diatur ke {promo_delay} detik.")

@client.on(events.NewMessage(pattern=r"\.setpromo (.+)"))
async def set_promo_cmd(event):
    global promo_text
    promo_text = event.pattern_match.group(1)
    await event.reply("✅ Teks promosi berhasil diperbarui!")

@client.on(events.NewMessage(pattern=r"\.autopromo (on|off)"))
async def toggle_autopromo(event):
    global promo_enabled
    promo_enabled = event.pattern_match.group(1) == 'on'
    await event.reply(f"✅ AutoPromo {'AKTIF' if promo_enabled else 'DINONAKTIFKAN'}.")

@client.on(events.NewMessage(pattern=r"\.promote"))
async def manual_promote(event):
    count = 0
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, promo_text)
                count += 1
                logging.info(f"Promosi dikirim ke {dialog.name}")
                await asyncio.sleep(promo_delay)
            except:
                continue
    await event.reply(f"📣 Promosi selesai ke {count} grup.")

@client.on(events.NewMessage(pattern=r"\.sendall (.+)"))
async def sendall(event):
    text = event.pattern_match.group(1)
    sent = 0
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, text)
                logging.info(f"Kirim manual ke {dialog.name}")
                sent += 1
                await asyncio.sleep(promo_delay)
            except:
                continue
    await event.reply(f"✅ Terkirim ke {sent} grup.")

@client.on(events.NewMessage(pattern=r"\.listgroups"))
async def list_groups(event):
    text = "**📋 Grup yang Diikuti:**\n"
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            text += f"• {dialog.name}\n"
    await event.reply(text or "⚠️ Tidak ada grup ditemukan.")

@client.on(events.NewMessage(pattern=r"\.join (.+)"))
async def join_group(event):
    try:
        target = event.pattern_match.group(1)
        await client(JoinChannelRequest(target))
        await event.reply(f"✅ Berhasil join ke `{target}`")
    except Exception as e:
        await event.reply(f"❌ Gagal join: {e}")

@client.on(events.NewMessage(pattern=r"\.leave"))
async def leave_group(event):
    if reply := await event.get_reply_message():
        try:
            chat = await event.get_chat()
            await client(LeaveChannelRequest(chat))
            await event.reply("👋 Keluar dari grup.")
        except:
            await event.reply("❌ Gagal keluar.")
    else:
        await event.reply("⚠️ Reply ke pesan grup untuk keluar.")

@client.on(events.NewMessage(pattern=r"\.tagall"))
async def tag_all(event):
    mentions = ""
    async for user in client.iter_participants(event.chat_id):
        if user.username:
            mentions += f"@{user.username} "
    if mentions:
        await event.reply(mentions[:4000])
    else:
        await event.reply("❌ Tidak ada username untuk di-tag.")

@client.on(events.NewMessage(pattern=r"\.cekid"))
async def cekid_cmd(event):
    user = await event.get_sender()
    user_id = user.id
    username = f"@{user.username}" if user.username else "Tidak ada username"
    fullname = f"{user.first_name or ''} {user.last_name or ''}".strip()
    is_bot = "Ya 🤖" if user.bot else "Tidak 👤"

    reply_text = (
        "🔎 **Info User:**\n"
        f"• Nama Lengkap : {fullname}\n"
        f"• Username     : {username}\n"
        f"• User ID      : `{user_id}`\n"
        f"• Status Bot   : {is_bot}\n"
    )
    await event.reply(reply_text)

async def autopromo_loop():
    while True:
        if promo_enabled:
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    try:
                        await client.send_message(dialog.id, promo_text)
                        logging.info(f"[AUTO] Promosi ke {dialog.name}")
                        await asyncio.sleep(promo_delay)
                    except:
                        continue
        await asyncio.sleep(600)  # jeda antar siklus 10 menit

print("🚀 Ubot PRO aktif dan berjalan...")
client.start()
client.loop.create_task(autopromo_loop())
client.run_until_disconnected()
