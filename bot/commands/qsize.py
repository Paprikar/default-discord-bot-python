import discord

from ..utils.utils import get_pics_path_list


async def message_qsize(message, args_str, bot):
    pics_categories = bot.pics_categories
    category_names = set()
    args = args_str.split()
    if not args or 'all' in args:
        category_names.update(pics_categories.keys())
    else:
        for category_name in args:
            if category_name in pics_categories:
                category_names.add(category_name)
    if not category_names:
        return
    category_names = sorted(category_names)
    desc = ''
    embed = discord.Embed()
    for category_name in category_names:
        path = pics_categories[category_name]['pictures_directory']
        qsize = len(get_pics_path_list(path))
        desc += f'Queue size for `{category_name}` pictures: {qsize}\n'
    embed.description = desc.rstrip()
    await message.channel.send(embed=embed)
