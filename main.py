import discord
from discord import Option
from datetime import timedelta
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from asyncio import sleep
import asyncio
import datetime
from discord import Member
from discord.ext import commands

intents = discord.Intents.all()

# Define your bot
bot = commands.Bot(command_prefix='/', intents=intents)

#define the IDs
servers = [GUILD_ID] #Replace with the ID of your guild
co_moderator_role_id = CO-MODERATOR_ROLE_ID # Replace with the ID of the Co-Moderator role
moderator_role_id = MODERATOR_ROLE_ID # Replace with the ID of the Moderator role
mod_application_channel_id = MOD_APPLICATION_CHANNEL_ID # Replace with the ID of the mod-application channel
logs_channel = LOGS_CHANNEL_ID #Replace with the ID of the logs channel
unverified_role_id = UNVERIFIED_ROLE_ID #Replace with the ID of the Unverified role

@bot.slash_command(guild_ids=servers, name="help", description="Shows the available commands.")
async def help(ctx):
    embed = discord.Embed(title="Help", description="Hi, my name is Oinky.exe! Here are the available commands:")
    response = await ctx.defer()
    await asyncio.sleep(3)
    embed.color = discord.Color.blue()
    embed.add_field(name="help", value="Shows this menu.", inline=True)
    embed.add_field(name="apply", value="Apply for the Co-Moderator role.", inline=True)
    embed.add_field(name="ban", value="Bans a member. Only Moderators can use it!", inline=True)
    embed.add_field(name="bans", value="Get a list of members who are banned from this server, Only Moderators can use it!", inline=True)
    embed.add_field(name="clear", value="Clears a channel's messages. Only Owner, Co-Owners, Partners and Gods can use it!", inline=True)
    embed.add_field(name="kick", value="Kicks a member, Only Moderators can use it!", inline=True)
    embed.add_field(name="setup_verification_system", value="Sets up the verification system!, Only Moderators can use it!", inline=True)
    embed.add_field(name="timeout", value="Mutes/timeouts a member, Only Moderators can use it!", inline=True)
    embed.add_field(name="unban", value="Unbans a member, Only Moderators can use it!", inline=True)
    embed.add_field(name="unmute", value="Unmutes/untimeouts a member, Only Moderators can use it!", inline=True)
    await ctx.respond(embed=embed)

async def send_mod_application_embed(user, timezone, country, region, city, reason):
    embed = discord.Embed(
        title="Co-Moderator Application",
        description="The user below has applied for the Co-Moderator role.",
        color=discord.Color.blue()
    )
    embed.set_author(
        name=user.name,
        icon_url=user.display_avatar.url
    )
    embed.add_field(
        name="Timezone",
        value=timezone
    )
    embed.add_field(
        name="Country",
        value=country
    )
    embed.add_field(
        name="Region",
        value=region
    )
    embed.add_field(
        name="City",
        value=city
    )
    embed.add_field(
        name="Reason for Applying",
        value=reason
    )
    embed.set_footer(text="React with ✅ to approve, or ❌ to reject.")
    mod_application_channel = bot.get_channel(mod_application_channel_id) # Replace with the ID of the channel where you want to send the application
    message = await mod_application_channel.send(embed=embed)
    return message

@bot.slash_command(guild_ids=servers, name="apply", description="Apply for the Co-Moderator role.", defer=True, timeout=10)
async def apply(ctx, timezone: Option(str, description="The timezone you are located in", required=True), country: Option(str, description="The country you are located in", required=True), region: Option(str, description="The region you are located in", required=True), city: Option(str, description="The city you are located in", required=True), reason: Option(str, description="The reason why you want to become a Co-Moderator", required=True)):
    # Convert timezone string to a timedelta object
    offset_str = timezone.split()[0]
    if offset_str[0] == "+":
        offset = datetime.timedelta(hours=int(offset_str[1:3]), minutes=int(offset_str[3:]))
    else:
        offset = datetime.timedelta(hours=-int(offset_str[1:3]), minutes=-int(offset_str[3:]))
    
    # Get Co-Moderator role
    co_moderator_role = ctx.guild.get_role(co_moderator_role_id)
    
    # Calculate the expiration date for the Co-Moderator role
    expiration_date = datetime.datetime.now(datetime.timezone(offset)) + datetime.timedelta(weeks=3)

    # Schedule a task to remove the Co-Moderator role after 3 weeks
    async def remove_co_moderator_role():
        await asyncio.sleep((expiration_date - datetime.datetime.now(datetime.timezone(offset))).total_seconds())
        await ctx.author.remove_roles(co_moderator_role)
        moderator_role = ctx.guild.get_role(moderator_role_id)
        await ctx.author.add_roles(moderator_role)

    bot.loop.create_task(remove_co_moderator_role())
    
    # Send the moderator application embed and wait for moderator approval/rejection
    await ctx.send(f"{ctx.author.mention} Your Mod application has been submitted and waiting approval, I'll try keep you up-to-date!")
    message = await send_mod_application_embed(ctx.author, timezone, country, region, city, reason)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction, user):
        return str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == message.id and user.id != ctx.bot.user.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=604800, check=check)
    except (asyncio.TimeoutError, asyncio.CancelledError):
        await ctx.send(f"{ctx.author.mention} Your Co-Moderator role application has expired. Please re-apply if you're still interested.")
        return

    if str(reaction.emoji) == '✅':
        await ctx.send(f"{ctx.author.mention} Congratulations! Your Co-Moderator role application has been approved.")
        await ctx.author.add_roles(co_moderator_role)
    else:
        await ctx.send(f"{ctx.author.mention} Unfortunately, your Co-Moderator role application has been rejected.")
        return

@bot.event
async def on_member_join(member):
        unverified = discord.utils.get(member.guild.roles, id=unverified_role_id)
        await member.add_roles(unverified)

@bot.slash_command(guild_ids=servers, name="clear", description="Clears a channel's messages")
@commands.has_permissions(manage_messages=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def clear(ctx, messages: Option(int, description="How many messages do you want to clear?", required=True)):
    try:
        z = await ctx.channel.purge(limit=messages)
        await ctx.respond(f"I have cleared {len(z)}")
    except discord.errors.NotFound:
        pass

@clear.error
async def clearerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You need manage messages permissions to do this!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
    else:
        raise error

@bot.slash_command(name="setup_verification_system", guild_ids=[servers], description="Sets up the verification system!!")
@commands.has_permissions(moderate_members = True)
async def setup_verification_system(ctx):
    message = await ctx.send("<:ServerBooster:1089309398855319592>======Verify======<:ServerBooster:1089309398855319592>\nPlease click the Checkmark bellow to get access to the server content and chat with our amazing members")
    await message.add_reaction("<:Verify:1089311271079383081>")

@bot.slash_command(guild_ids = servers, name = 'timeout', description = "mutes/timeouts a member")
@commands.has_permissions(moderate_members = True)
async def timeout(ctx, member: Option(discord.Member, required = True), reason: Option(str, required = False), days: Option(int, max_value = 27, default = 0, required = False), hours: Option(int, default = 0, required = False), minutes: Option(int, default = 0, required = False), seconds: Option(int, default = 0, required = False)): #setting each value with a default value of 0 reduces a lot of the code
    if member.id == ctx.author.id:
        await ctx.respond("You can't timeout yourself!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.respond("You can't do this, this person is a moderator!")
        return
    duration = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
    if duration >= timedelta(days = 28): #added to check if time exceeds 28 days
        await ctx.respond("I can't mute someone for more than 28 days!", ephemeral = True) #responds, but only the author can see the response
        return
    if reason == None:
        await member.timeout_for(duration)
        await ctx.respond(f"<@{member.id}> has been timed out for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by <@{ctx.author.id}>.")
    else:
        await member.timeout_for(duration, reason = reason)
        await ctx.respond(f"<@{member.id}> has been timed out for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by <@{ctx.author.id}> for '{reason}'.")

@timeout.error
async def timeouterror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You can't do this! You need to have moderate members permissions!")
    else:
        raise error

@bot.slash_command(guild_ids = servers, name = 'unmute', description = "unmutes/untimeouts a member")
@commands.has_permissions(moderate_members = True)
async def unmute(ctx, member: Option(discord.Member, required = True), reason: Option(str, required = False)):
    if reason == None:
        await member.remove_timeout()
        await ctx.respond(f"<@{member.id}> has been untimed out by <@{ctx.author.id}>.")
    else:
        await member.remove_timeout(reason = reason)
        await ctx.respond(f"<@{member.id}> has been untimed out by <@{ctx.author.id}> for '{reason}'.")

@unmute.error
async def unmuteerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You can't do this! You need to have moderate members permissions!")
    else:
        raise error

@bot.slash_command(guild_ids = servers, name = "ban", description = "Bans a member")
@commands.has_permissions(ban_members = True, administrator = True)
async def ban(ctx, member: Option(discord.Member, description = "Who do you want to ban?"), reason: Option(str, description = "Why?", required = False)):
    if member.id == ctx.author.id: #checks to see if they're the same
        await ctx.respond("BRUH! You can't ban yourself!")
    elif member.guild_permissions.administrator:
        await ctx.respond("Stop trying to ban an admin! :rolling_eyes:")
    else:
        if reason == None:
            reason = f"None provided by {ctx.author}"
        await member.ban(reason = reason)
        await ctx.respond(f"<@{ctx.author.id}>, <@{member.id}> has been banned successfully from this server!\n\nReason: {reason}")
    
@ban.error
async def banerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You need Ban Members and Administrator permissions to do this!")
    else:
        await ctx.respond("Something went wrong...") #most likely due to missing permissions
        raise error

@bot.slash_command(guild_ids = servers, name = "kick", description = "Kicks a member")
@commands.has_permissions(kick_members = True, administrator = True)
async def kick(ctx, member: Option(discord.Member, description = "Who do you want to kick?"), reason: Option(str, description = "Why?", required = False)):
    if member.id == ctx.author.id: #checks to see if they're the same
        await ctx.respond("BRUH! You can't kick yourself!")
    elif member.guild_permissions.administrator:
        await ctx.respond("Stop trying to kick an admin! :rolling_eyes:")
    else:
        if reason == None:
            reason = f"None provided by {ctx.author}"
        await member.kick(reason = reason)
        await ctx.respond(f"<@{ctx.author.id}>, <@{member.id}> has been kicked from this server!\n\nReason: {reason}")

@kick.error
async def kickerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You need Kick Members and Administrator permissions to do this!")
    else:
        await ctx.respond("Something went wrong...") #most likely due to missing permissions 
        raise 

@bot.slash_command(guild_ids = servers, name = "bans", description = "Get a list of members who are banned from this server!")
@commands.has_permissions(ban_members = True)
async def bans(ctx):
    await ctx.defer()
    bans = await ctx.guild.bans()
    embed = discord.Embed(title = f"List of Bans in {ctx.guild}", timestamp = datetime.now(), color = discord.Colour.red())
    for entry in bans:
        if len(embed.fields) >= 25:
            break
        if len(embed) > 5900:
            embed.add_field(name = "Too many bans to list")
        else:
            embed.add_field(name = f"Ban", value = f"Username: {entry.user.name}#{entry.user.discriminator}\nReason: {entry.reason}\nUser ID: {entry.user.id}\nIs Bot: {entry.user.bot}", inline = False)
    await ctx.respond(embed = embed)

@bot.slash_command(guild_ids = servers, name = "unban", description = "Unbans a member")
@commands.has_permissions(ban_members = True)
async def unban(ctx, id: Option(discord.Member, description = "The User ID of the person you want to unban.", required = True)):
    await ctx.defer()
    member = await bot.get_or_fetch_user(id)
    await ctx.guild.unban(member)
    await ctx.respond(f"I have unbanned {member.mention}.")

@unban.error
async def unbanerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You need ban members permissions to do this!")
    else: 
        await ctx.respond(f"Something went wrong, I couldn't unban this member or this member isn't banned.")
        raise error

@bot.event
async def on_message_delete(message):
    z = bot.get_channel(logs_channel)
    embed = discord.Embed(title = f"{message.author}'s Message was Deleted", description = f"Deleted Message: {message.content}\nAuthor: {message.author.mention}\nLocation: {message.channel.mention}", timestamp = datetime.datetime.now(), color = discord.Colour.red())
    embed.set_author(name = message.author.name, icon_url = message.author.display_avatar)
    await z.send(embed = embed)

@bot.event
async def on_message_edit(before, after):
    z = bot.get_channel(logs_channel)
    embed = discord.Embed(title = f"{before.author} Edited Their Message", description = f"Before: {before.content}\nAfter: {after.content}\nAuthor: {before.author.mention}\nLocation: {before.channel.mention}", timestamp = datetime.datetime.now(), color = discord.Colour.blue())
    embed.set_author(name = after.author.name, icon_url = after.author.display_avatar)
    await z.send(embed = embed)

@bot.event
async def on_member_update(before, after):
    z = bot.get_channel(logs_channel)
    if len(before.roles) > len(after.roles):
        role = next(role for role in before.roles if role not in after.roles)
        embed = discord.Embed(title = f"{before}'s Role has Been Removed", description = f"{role.name} was removed from {before.mention}.",  timestamp = datetime.datetime.now(), color = discord.Colour.red())
    elif len(after.roles) > len(before.roles):
        role = next(role for role in after.roles if role not in before.roles)
        embed = discord.Embed(title = f"{before} Got a New Role", description = f"{role.name} was added to {before.mention}.",  timestamp = datetime.datetime.now(), color = discord.Colour.green())
    elif before.nick != after.nick:
        embed = discord.Embed(title = f"{before}'s Nickname Changed", description = f"Before: {before.nick}\nAfter: {after.nick}",  timestamp = datetime.datetime.now(), color = discord.Colour.blue())
    else:
        return
    embed.set_author(name = after.name, icon_url = after.display_avatar)
    await z.send(embed = embed)

@bot.event
async def on_guild_channel_create(channel):
    z = bot.get_channel(logs_channel)
    embed = discord.Embed(title = f"{channel.name} was Created", description = channel.mention, timestamp = datetime.datetime.now(), color = discord.Colour.green())
    await z.send(embed = embed)

@bot.event
async def on_guild_channel_delete(channel):
    z = bot.get_channel(logs_channel)
    embed = discord.Embed(title = f"{channel.name} was Deleted", timestamp = datetime.datetime.now(), color = discord.Colour.red())
    await z.send(embed = embed)

Unverified = "Unverified"

Member = "Member"

@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    if message_id == 1106264392623997050:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        if guild is not None:
            role1 = discord.utils.get(guild.roles, name=Unverified)
            role = discord.utils.get(guild.roles, name=Member)
            if role1 is not None:
                member = guild.get_member(payload.user_id)
                if member is not None:
                    await member.remove_roles(role1)
            if role is not None:
                member = guild.get_member(payload.user_id)
                if member is not None:
                    await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    if message_id == VERIFICATION_MESSAGE_ID: #Replace with the ID of your verification message
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        if guild is not None:
            role1 = discord.utils.get(guild.roles, name=Unverified)
            role = discord.utils.get(guild.roles, name=Member)
            if role1 is not None:
                member = guild.get_member(payload.user_id)
                if member is not None:
                    await member.add_roles(role1)
            if role is not None:
                member = guild.get_member(payload.user_id)
                if member is not None:
                    await member.remove_roles(role)

@bot.event
async def on_member_join(member):
    await sleep(10)
    for channel in member.guild.channels:
        if channel.name.startswith('Member'):
            await channel.edit(name=f'Members: {member.guild.member_count}')
            break

@bot.event
async def on_member_remove(member):
	await sleep(10)
	for channel in member.guild.channels: 
		if channel.name.startswith('Member'):
			await channel.edit(name=f'Members: {member.guild.member_count}')
			break

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over the server"))
    print('-----------------------------------------------------')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('-----------------------------------------------------')

bot.run('TOKEN') #Replace with your bot's token
