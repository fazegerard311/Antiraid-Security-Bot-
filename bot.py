import discord
from discord.ext import commands
import json

# Variables globales
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Diccionario que almacenará los IDs de usuarios baneados globalmente (en todos los servidores)
global_ban_list = {}

# ID del servidor de soporte (cámbialo por el ID real de tu servidor de soporte)
SUPPORT_SERVER_ID = '1349784181382582392'

# Token de tu bot de Discord (debes añadirlo como variable de entorno o directamente aquí)
DISCORD_TOKEN = 'MTM0OTc4MDk2ODQzMjYwMzE1Nw.GxVH_f.hYYr1sak_eLtes5c2WjIPvflvHIz_UHFBO_04k'


# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot está listo. Conectado como {bot.user}')


# Comando para banear un usuario
@bot.command()
async def ban(ctx, user: discord.User, *, reason=None):
    # Verifica si el usuario que ejecuta el comando tiene permisos
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("No tienes permisos para usar este comando.")
        return

    # Banea al usuario en el servidor actual
    await ctx.guild.ban(user, reason=reason)
    await ctx.send(f'Usuario {user} ha sido baneado.')

    # Almacenar el ban globalmente si no está ya registrado
    if user.id not in global_ban_list:
        global_ban_list[user.id] = [ctx.guild.id]
    else:
        global_ban_list[user.id].append(ctx.guild.id)


# Comando para desbanear un usuario en todos los servidores
@bot.command()
async def global_unban(ctx, user: discord.User):
    # Solo usuarios del servidor de soporte pueden ejecutar este comando
    if ctx.guild.id != int(SUPPORT_SERVER_ID):
        await ctx.send("Este comando solo está disponible en el servidor de soporte.")
        return

    # Verifica si el usuario que ejecuta el comando tiene permisos
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("No tienes permisos para usar este comando.")
        return

    # Verifica si el usuario está en la lista global de baneos
    if user.id not in global_ban_list:
        await ctx.send(f'{user} no está en la lista global de baneos.')
        return

    # Desbanea al usuario de todos los servidores donde está baneado
    for guild_id in global_ban_list[user.id]:
        guild = bot.get_guild(guild_id)
        if guild:
            member = guild.get_member(user.id)
            if member:
                await guild.unban(user)
                print(f'Usuario {user} desbaneado de {guild.name}.')
    
    # Elimina al usuario de la lista global de baneos
    del global_ban_list[user.id]
    await ctx.send(f'{user} ha sido desbaneado de todos los servidores.')


# Comando para ver los baneos globales
@bot.command()
async def global_bans(ctx):
    if ctx.guild.id != int(SUPPORT_SERVER_ID):
        await ctx.send("Este comando solo está disponible en el servidor de soporte.")
        return

    # Muestra la lista de usuarios baneados globalmente
    if global_ban_list:
        bans = "\n".join([f'{bot.get_user(user_id)}' for user_id in global_ban_list.keys()])
        await ctx.send(f'Usuarios baneados globalmente:\n{bans}')
    else:
        await ctx.send("No hay usuarios baneados globalmente.")


# Comando para verificar si un usuario está baneado globalmente
@bot.command()
async def check_ban(ctx, user: discord.User):
    if user.id in global_ban_list:
        await ctx.send(f'{user} está baneado globalmente en los siguientes servidores: {global_ban_list[user.id]}')
    else:
        await ctx.send(f'{user} no está baneado globalmente.')


# Comando para mostrar logs de baneos (se almacenan en un archivo `logs.json`)
@bot.command()
async def logs(ctx):
    if ctx.guild.id != int(SUPPORT_SERVER_ID):
        await ctx.send("Este comando solo está disponible en el servidor de soporte.")
        return

    # Cargar los logs desde un archivo JSON
    try:
        with open('logs.json', 'r') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = {}

    # Verifica si hay logs disponibles
    if logs:
        logs_text = "\n".join([f"{log['username']} - Baneado por: {log['moderator']} en {log['guild']}" for log in logs.values()])
        await ctx.send(f"Logs de baneos:\n{logs_text}")
    else:
        await ctx.send("No hay logs de baneos disponibles.")


# Evento cuando un miembro es baneado (se guarda un log en `logs.json`)
@bot.event
async def on_member_ban(guild, user):
    # Guardamos un log de cada baneo en un archivo JSON
    log_entry = {
        "username": user.name,
        "moderator": "Sistema",  # Puedes modificarlo para registrar el moderador
        "guild": guild.name
    }

    try:
        # Cargar los logs existentes
        with open('logs.json', 'r') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = {}

    # Almacenar el log
    logs[user.id] = log_entry

    # Guardar los logs actualizados
    with open('logs.json', 'w') as f:
        json.dump(logs, f, indent=4)


# Ejecuta el bot
bot.run(DISCORD_TOKEN)