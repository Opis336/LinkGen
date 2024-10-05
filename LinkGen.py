# Imports
try:
    import json, os, platform, time, asyncio
    import discord
    from discord.ext import commands
except Exception:
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    print("LinkGen uses Pycord, Try to remove discord.py if installed")
    time.sleep(3)
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    print("Pycord not found - Installing...\n")
    os.system("pip install py-cord==2.0.0b4")
    os._exit(0)

# Use discord.Bot() since it's from Pycord
client = discord.Bot()

# Check if correctly setup
if not os.path.exists("accounts"):
    os.mkdir("accounts")
if platform.system() != "Windows":
    os.system("clear")

# Load config
try:
    with open("config.json", "r") as f:
        config_data = json.load(f)
except Exception:
    print("[ERROR] Config File missing")
    os._exit(1)

# Validate config settings
required_keys = ["token", "guild_id", "log_channel", "gen_role", "gen_channel"]
for key in required_keys:
    if key not in config_data:
        print(f"[ERROR] {key.replace('_', ' ').title()} not set")
        os._exit(1)

# When bot is logged in
@client.event
async def on_ready():
    print(f"Logged in as: {client.user.name}")
    
    if client.guilds:
        print(f"Using guild: {client.guilds[0].name}")
    else:
        print("[ERROR] The bot is not in any guilds.")
        return

    print("LinkGen Ready", "\n")
    await client.change_presence(activity=discord.Game(name="LinkGen V2.0"))

    # Check for roles and channels
    try:
        client.guilds[0].get_role(int(config_data["gen_role"]))
    except Exception:
        print("[ERROR] Gen Role not set")
    
    try:
        client.guilds[0].get_channel(int(config_data["gen_channel"]))
    except Exception:
        print("[ERROR] Gen Channel not set")

    services = ["nordvpn", "roblox", "expressvpn", "nitro", "creditcard", "spotify", "netflix", "disney", "minecraft"]
    for service in services:
        if not os.path.exists(f"accounts/{service}.txt"):
            with open(f"accounts/{service}.txt", "a") as f:
                f.write(f"Paste {service} accounts here")
            print(f"[WARNING] No Accounts found for {service} - Creating file...")

# Generate Command
@client.slash_command(name="generate", guild_ids=[config_data["guild_id"]])
async def generate(ctx, service_name):
    if str(ctx.channel.id) != config_data["gen_channel"]:
        await ctx.respond(f"You can only gen in: <#{config_data['gen_channel']}>", ephemeral=True)
        return

    services = ["NordVPN", "Roblox", "ExpressVPN", "Nitro", "CreditCard", "Spotify", "Netflix", "Disney", "Minecraft"]
    if service_name not in services:
        await ctx.respond("Invalid service name!", ephemeral=True)
        return

    if str(config_data["gen_role"]) not in [str(role.id) for role in ctx.author.roles]:
        await ctx.respond(f"You cannot gen {service_name}!", ephemeral=True)
        return

    try:
        with open(f"accounts/{service_name.lower()}.txt", "r+") as accounts:
            data = accounts.readlines()
            if not data:  # Check if there are accounts available
                await ctx.respond(f"We are currently out of {service_name}!", ephemeral=True)
                return

            # Remove the first line (the account being generated)
            account_to_use = data[0]
            accounts.seek(0)
            accounts.writelines(data[1:])
            accounts.truncate()

            embed = discord.Embed(title=f"{service_name} Account Generated", description="LinkGen Account Generator", color=0x46a9f0)
            embed.add_field(name="Login Credentials", value=f"```{account_to_use}```", inline=True)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/773133136929226763/797514521997828106/777514274829893683.gif")

            # Send DM to the user
            try:
                user = await client.fetch_user(ctx.author.id)  # Fetch the user directly
                await user.send(embed=embed)
            except Exception as e:
                print(f"Failed to send DM: {str(e)}")
                await ctx.respond("Account Generated, but I couldn't send you a DM.", ephemeral=True)

            log = client.guilds[0].get_channel(int(config_data["log_channel"]))
            log_embed = discord.Embed(title=f"{ctx.author.name} has genned 1 {service_name}", description=f"**Account**\n```{account_to_use}```", color=0x46a9f0)
            await log.send(embed=log_embed)
            await ctx.respond("Account Generated, check your DM. Vouch in #🎫︱vouch.")

            # Send vouch message in the generation channel
            await ctx.channel.send(f"{ctx.author.mention} has successfully generated an account!")  # Vouch message in the gen channel

    except Exception as e:
        await ctx.respond(f"Error: {str(e)}", ephemeral=True)

# Stock Command
@client.slash_command(name="stock", guild_ids=[config_data["guild_id"]])
async def stock(ctx):
    embed = discord.Embed(title="Current Account Stock", color=0x46a9f0)
    
    services = ["nordvpn", "roblox", "expressvpn", "nitro", "creditcard", "spotify", "netflix", "disney", "minecraft"]
    for service in services:
        if os.path.exists(f"accounts/{service}.txt"):
            with open(f"accounts/{service}.txt", "r") as file:
                accounts = file.readlines()
                embed.add_field(name=service.capitalize(), value=f"{len(accounts)} accounts available", inline=False)
        else:
            embed.add_field(name=service.capitalize(), value="No accounts available", inline=False)
    
    embed.set_footer(text="Made by Tom the Guy")
    await ctx.respond(embed=embed)

# Start the bot
client.run(config_data["token"])

