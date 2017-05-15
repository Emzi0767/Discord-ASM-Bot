import datetime
import traceback
import sys
import os
import asyncio
import discord
import asmbot
from discord.ext import commands
from concurrent.futures import CancelledError


class AsmBot(commands.Bot):
    def __init__(self, guild_blacklist=[], guild_exempt_list=[], **kwargs):
        super().__init__(command_prefix=self.prefix_callback, **kwargs)
        self.tasks = []
        self.guild_blacklist = guild_blacklist
        self.guild_exempt_list = guild_exempt_list
        self.processed_guilds = []
        self.gamewatch_running = False

    def cancel_everything(self):
        self.future.cancel()

    def _embed(self, ctx, title, description, cat="info"):
        clr = 0x00007FFF
        if cat == "error":
            clr = 0x00FF7F00
        elif cat == "success":
            clr = 0x007FFF00

        embed = discord.Embed(title=title, description=description, colour=discord.Colour(clr))
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        return embed

    def _embed_self(self, title, description, cat="info"):
        clr = 0x00007FFF
        if cat == "error":
            clr = 0x00FF7F00
        elif cat == "success":
            clr = 0x007FFF00

        embed = discord.Embed(title=title, description=description, colour=discord.Colour(clr))
        embed.set_thumbnail(url=self.user.avatar_url)
        return embed

    def _prefix(self, guild):
        return ["<@" + self.user.id + "> ", "<@!" + self.user.id + "> "]

    def _restart_gamewatch(self, fut):
        self.tasks.remove(fut)
        fut.cancel()

        if not self.is_closed and not self.gamewatch_running:
            asmbot.log("Gamewatch for shard {} crashed, restarting".format(self.shard_id), tag="ASM GAME")
            task = self.loop.create_task(self.game_watch())
            task.add_done_callback(self._restart_gamewatch)
            self.tasks.append(task)

    def prefix_callback(self, bot, message):
        return self._prefix(message.channel.server)

    @property
    def future(self):
        return self._future

    @future.setter
    def future(self, value):
        self._future = value

    async def game_watch(self):
        if self.gamewatch_running:
            return

        self.gamewatch_running = True
        try:
            lop = datetime.datetime(2015, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
            asmbot.log("Gamewatch for shard {} initialized".format(self.shard_id), tag="ASM GAME")

            while not self.is_closed:
                cop = datetime.datetime.now(datetime.timezone.utc)
                tdelta = cop - lop

                if tdelta.seconds >= 900:
                    lop = cop
                    await self.change_presence(game=discord.Game(name="RYZEN HYYYYYYYPEEEE"))

                await asyncio.sleep(0.1)

        except CancelledError:
            pass

        except Exception as e:
            asmbot.logex(e, tag="ASM GAME")

        finally:
            self.gamewatch_running = False
            asmbot.log("Gamewatch for shard {} closed".format(self.shard_id), tag="ASM GAME")

    # Error handling
    async def on_error(self, event, *args, **kwargs):
        exinfo = sys.exc_info()
        exfmts = [s.replace("\\n", "") for s in traceback.format_exception(*exinfo)]
        asmbot.log(*exfmts, tag="ASM ERR")

    async def on_command_error(self, exception, context):
        extype = type(exception)
        value = exception
        tback = exception.__traceback__
        exinfo = (extype, value, tback)

        exfmts = [s.replace("\\n", "") for s in traceback.format_exception(*exinfo)]
        exfmt = [""]

        for exf in exfmts:
            ci = len(exfmt) - 1
            if len(exfmt[ci]) + len(exf) + 1 > 1024:
                exfmt.append(exf)
            else:
                exfmt[ci] = exfmt[ci] + "\n" + exf

        if context.command is None:
            return
        cmd = context.command.qualified_name

        embed = self._embed(context, "Error executing command",
                            "An error occured when executing command `{}`".format(cmd), "error")

        asmbot.log(*exfmts, tag="CMD ERR")
        await self.send_message(context.message.channel, embed=embed)

    # Bot preparation
    async def on_resumed(self):
        await self.on_ready()

    async def on_ready(self):
        self.processed_guilds = []
        asmbot.log("Logged in as {} on shard {} as PID {:05}".format(self.user.name, self.shard_id, os.getpid()), tag="ASM CORE")

        for gld in self.servers:
            await self.on_server_available(gld)

        task = self.loop.create_task(self.game_watch())
        task.add_done_callback(self._restart_gamewatch)
        self.tasks.append(task)

    # Guild init
    async def on_server_join(self, guild):
        await self.on_server_available(guild)

    async def on_server_available(self, guild):
        if guild.id in self.processed_guilds:
            return

        asmbot.log("Guild available: {}".format(guild.name), tag="ASM CORE")

        # check blacklist
        if guild.id in self.guild_exempt_list:
            asmbot.log("Ignoring exempt guild {} ({})".format(guild.name, guild.id), tag="ASM CORE")
            self.processed_guilds += guild.id
            return

        if guild.id in self.guild_blacklist:
            asmbot.log("Leaving blacklisted guild {} ({})".format(guild.name, guild.id), tag="ASM CORE")
            await self.leave_server(guild)

        mra = [0, 0]
        for xm in guild.members:
            mra[0] += 1
            if xm.bot:
                mra[1] += 1

        mr = mra[1] / (mra[0] - mra[1])
        if mra[0] > 25 and mr >= 0.4:
            asmbot.log("Guild {} ({}) has too high bot-to-human ratio ({:.0f}% at {:n} members)".format(guild.name, guild.id, mr * 100, mra[0]), tag="ASM CORE")
            await self.leave_server(guild)

        self.processed_guilds += guild.id

    # Command and chat handling
    async def on_message(self, message):
        if message.channel.is_private:
            return

        if message.author.bot:
            return

        await self.process_commands(message)

    async def on_command(self, command, context):
        pass

    async def on_command_completion(self, command, context):
        usr = context.message.author
        chn = context.message.channel
        gld = chn.server
        asmbot.log("{} ({}) executed command {} in guild {} ({}) on shard {}, channel {} ({})".format(usr, usr.id, command.qualified_name, gld.name, gld.id, self.shard_id, chn.name, chn.id),
                   tag="ASM CMD")
