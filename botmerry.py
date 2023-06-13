import disnake
from disnake.ext import commands
import json
import os
from disnake import Member
from disnake.permissions import PermissionOverwrite

# Перевірка наявності JSON-файлу, в іншому випадку створення нового
if not os.path.exists('marriages.json'):
    with open('marriages.json', 'w') as f:
        json.dump({}, f)

# Завантаження даних з JSON-файлу
with open('marriages.json', 'r') as f:
    marriages = json.load(f)

# Збереження даних у JSON-файл
def save_marriages():
    with open('marriages.json', 'w') as f:
        json.dump(marriages, f)

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.slash_command()
async def merry(ctx, member: Member):
    if str(ctx.author.id) in marriages:
        await ctx.send("Ви вже перебуваєте в шлюбу!")
    elif member.id == ctx.author.id:
        await ctx.send("Ви не можете одружитися самі з собою!")
    else:
        if str(member.id) in marriages:
            await ctx.send("Цей учасник вже одружений!")
        else:
            marriages[str(member.id)] = str(ctx.author.id)
            marriages[str(ctx.author.id)] = str(member.id)
            save_marriages()
            await ctx.send(f"{ctx.author.mention} пропонує {member.mention} одружитися. Згодні?")

@bot.slash_command()
async def acceptmerry(ctx, member: Member = None):
    if member is None:
        if str(ctx.author.id) in marriages:
            await ctx.send("Ви вже перебуваєте в шлюбу!")
        else:
            await ctx.send("Ви не отримали жодної пропозиції шлюбу.")
    else:
        if str(member.id) in marriages and marriages[str(member.id)] == str(ctx.author.id):
            del marriages[str(member.id)]
            del marriages[str(ctx.author.id)]
            save_marriages()

            role_id = 1116026915074088980  # Замініть на ID ролі, яку потрібно додати
            role = ctx.guild.get_role(role_id)

            await member.add_roles(role)
            await ctx.author.add_roles(role)

            await ctx.send(f"{ctx.author.mention} приймає пропозицію шлюбу від {member.mention}. Роль надана!")

            # Створення голосових каналів для подружжя
            category_id = 1116053352963395634  # Замініть на ID категорії, де потрібно створити канали
            category = ctx.guild.get_channel(category_id)

            # Зміна прав доступу до голосового каналу
            overwrite = PermissionOverwrite()
            overwrite.connect = True  # Дозволити доступ

            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(connect=False),  # Заборонити доступ за замовчуванням
                ctx.author: overwrite,  # Дозволити доступ пропонуючому учаснику
                member: overwrite  # Дозволити доступ приймаючому учаснику
            }

            loveroom_name = f"loveroom_{ctx.author.id}_{member.id}"
            loveroom = await category.create_voice_channel(loveroom_name, overwrites=overwrites)

            await ctx.author.move_to(loveroom)
            await member.move_to(loveroom)
        else:
            await ctx.send("Цей учасник не пропонував вам шлюб.")


@bot.slash_command()
async def divorce(ctx):
    if str(ctx.author.id) in marriages:
        spouse_id = marriages[str(ctx.author.id)]
        if str(spouse_id) == str(ctx.author.id):
            del marriages[str(ctx.author.id)]
            del marriages[spouse_id]
            save_marriages()

            role_id = 1116026915074088980  # Замініть на ID ролі, яку потрібно зняти
            role = ctx.guild.get_role(role_id)

            await ctx.author.remove_roles(role)

            spouse = ctx.guild.get_member(int(spouse_id))
            if spouse:
                await spouse.remove_roles(role)

            category_id = 1116053352963395634  # Замініть на ID категорії, де знаходиться голосовий канал
            category = ctx.guild.get_channel(category_id)

            voice_channels_to_delete = []
            for channel_id, members in marriages.items():
                if str(channel_id).startswith('voice_'):
                    if str(ctx.author.id) in members or spouse_id in members:
                        voice_channels_to_delete.append(int(channel_id))

            for channel_id in voice_channels_to_delete:
                voice_channel = category.get_channel(channel_id)
                if voice_channel:
                    await voice_channel.delete()
                    del marriages[str(channel_id)]

            await ctx.send("Ваш шлюб розлучено. Роль забрана і голосовий канал видалений.")
        else:
            await ctx.send("Ви не перебуваєте в шлюбі з цією особою.")


bot.run('MTEwNDcyMDMwNTU0MjQwMjExMA.GPSNzY.NGJl_76Z0ETcNBDOM4OLy_F8t-7wsAoQN0MAPI')