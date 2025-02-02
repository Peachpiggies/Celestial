import os
import git 
import nextcord
import chat_response
from dotenv import load_dotenv
from nextcord.ext import commands
from dotenv import load_dotenv
from importlib import reload

intents = nextcord.Intents.default()
intents.message_content = True

use_debug_mode = False

client = commands.Bot(
    command_prefix = '::<!' if use_debug_mode else '<!', 
    intents = intents, 
    help_command = None,
    activity = nextcord.Game(name = '<!help> for more info.')
)

def is_owner(ctx: commands.Context) -> bool:
    
    '''
        Check if the command user is authorized.
    '''
    
    return ctx.author.id in moderator_ids
    

@client.event
async def on_ready() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'\u001b[45;1m ** \u001b[0m Status: {"Debug" if use_debug_mode else "Production"}')
    print(f'\u001b[45;1m ** \u001b[0m Successfully logged in as: {client.user}')


@client.event
async def on_message(message: nextcord.Message) -> None:

    if message.content.startswith('<usr>'):
        chat_message = message.content.split('<usr>')[1].strip()
        await message.channel.send(chat_response.get_response(chat_message, debug = use_debug_mode))

    await client.process_commands(message)
    
    
@client.command(name = 'help>')
async def helper(ctx: commands.Context) -> None:
    
    help_embed = nextcord.Embed(
        title = '', 
        description = 'a Python Discord chat bot who can talk with you in English and Thai.', 
        color = 0xd357fe
    )
    
    help_embed.set_author(
        name = 'Celestial#0135', 
        icon_url = 'https://cdn.discordapp.com/app-icons/927573556961869825/b4b624c1cb68fa3a99a24a8e9942d2a5.png'
    )
    
    help_embed.add_field(
        name = 'How can you talk to me?', 
        value = 'You can talk to me by simply type\n`<usr> Your messages` to send me a messages!', 
        inline = False
    )
    
    help_embed.add_field(
        name = 'Report Issue', 
        value = 'If there is a problem with the bot response or any bug with the bot, \nfeel free to report us at: \n**https://github.com/StrixzIV/Celestial/issues/new/choose**', 
        inline = True
    )
    
    help_embed.add_field(
        name = 'Development & Update', 
        value = 'Follow the latest update at: \n**https://github.com/StrixzIV/Celestial**', 
        inline = False
    )
    
    help_embed.set_footer(text = '© 2022 MIT License - StrixzIV#6258, Peachpiggies#9229')
    
    await ctx.send(embed = help_embed)
    
    
@client.command(name = 'reload>')
@commands.check(is_owner)
async def reload_bot(ctx: commands.Context) -> None:
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print('\u001b[45;1m ** \u001b[0m Reloading...')
    
    reload(chat_response)
    
    print('\u001b[45;1m ** \u001b[0m Chat module reload successfully!')
    print(f'\u001b[45;1m ** \u001b[0m Reload command sended from {ctx.author}')
    

@reload_bot.error
async def on_reload_error(ctx: commands.Context, error: commands.errors) -> None:
    
    error_embed = nextcord.Embed(
        title = '⚠️ Permission Error ⚠️', 
        description = 'Reload attempt from non-authorized user.', 
        color = 0xFF0000
    )
    
    print(f'\u001b[41;1m !! \u001b[0m Error: Reload attempt from {ctx.author} which is not an authorized user.')
    await ctx.send(embed=error_embed)
    
    
@client.command(name = 'pull>')
@commands.check(is_owner)
async def pull(ctx: commands.Context) -> None:
    
    print('\u001b[45;1m ** \u001b[0m Pulling from origin...')
    
    repo = git.Repo(os.getcwd())
    repo.remote('origin').pull()
    
    print('\u001b[45;1m ** \u001b[0m Pull complete.')
    print('\u001b[45;1m ** \u001b[0m Reloading chat module...')
    
    reload(chat_response)
    
    print('\u001b[45;1m ** \u001b[0m Chat module reload successfully!')
    print(f'\u001b[45;1m ** \u001b[0m Pull command sended from {ctx.author}')
    
    
@pull.error
async def on_pull_error(ctx: commands.Context, error: commands.errors) -> None:
    
    error_embed = nextcord.Embed(
        title = '⚠️ Permission Error ⚠️', 
        description = 'Pull attempt from non-authorized user.', 
        color = 0xFF0000
    )
    
    print(f'\u001b[41;1m !! \u001b[0m Error: Pull attempt from {ctx.author} which is not an authorized user.')
    await ctx.send(embed=error_embed)
    

if __name__ == '__main__':

    load_dotenv()
    moderator_ids = set([int(ids) for (key, ids) in os.environ.items() if key.startswith('ID')])
    
    client.run(os.getenv('TOKEN'))