import discord

from bot.utils.utils import get_pics_path_list


async def qsize(message, args_str, bot):
    pics_categories = {k: v for k, v in bot.config.pics_categories.items()
                       if 'PicsSendingModule' in v['modules']}
    category_names = set()
    args = args_str.split()
    if args:
        for category_name in args:
            if category_name in pics_categories:
                category_names.add(category_name)
    else:
        category_names.update(pics_categories.keys())
    if not category_names:
        return
    category_names = sorted(category_names)
    desc = ''
    embed = discord.Embed()
    for category_name in category_names:
        path = pics_categories[category_name]['send_directory']
        qsize = len(get_pics_path_list(path))
        desc += f'Queue size for `{category_name}` pictures: {qsize}\n'
    embed.description = desc.rstrip()
    await message.channel.send(embed=embed)
