import subprocess
import discord
from discord.ext import commands


class AsmBotCommands:
    def __init__(self, bot):
        self._bot = bot

    @property
    def script(self):
        return self._script

    @script.setter
    def script(self, value):
        self._script = value

    def _embed(self, ctx, title, description, cat="info"):
        clr = 0x00007FFF
        if cat == "error":
            clr = 0x00FF7F00
        elif cat == "success":
            clr = 0x007FFF00
        elif cat == "warning":
            clr = 0x00FFFF00

        embed = discord.Embed(title=title, description=description, colour=discord.Colour(clr))
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        return embed

    def _extract_code(self, code):
        istart = code.index("```")
        istart = code.index("\n", istart)
        iend = code.rindex("```")
        snip = code[istart:iend]
        return snip

    def _assemble(self, code, arch, clang_args=""):
        script_args = arch + " " + clang_args
        script_line = "bash " + self.script + " " + script_args

        proc = subprocess.Popen(script_line, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output = proc.communicate(input=code.encode())
        output = output[0].decode()

        sfind = "Contents of section .text:"
        oi = output.index(sfind)
        oi = output.index("\n", oi) + 1
        output = output[oi:]

        output = output.split("\n")
        obytes = []
        for line in output:
            line = line[:41]
            line = line.split(" ")
            line = "".join([x for x in line[2:] if x]).upper()
            line = [line[i:i + 2] for i in range(0, len(line), 2)]
            obytes += line

        return " ".join(obytes)

    @commands.command(name="help", description="Prints help text", pass_context=True)
    async def help(self, ctx):
        """
        Prints help
        """
        me = ctx.message.channel.server.me

        embed = self._embed(ctx, "Assembler help", "To invoke Assembler, call " + me.mention + " `<architecture>` `<assembly code block>`. For help, call " + me.mention + " help. "
                            "Source code of the bot is available [on Emzi's GitHub](https://github.com/Emzi0767/Discord-ASM-Bot). To invite the bot to your server, "
                            "Follow [this invite link](https://discordapp.com/oauth2/authorize?client_id=283200903937261569&scope=bot&permissions=0). For more help or support, join "
                            "[my server](https://discord.gg/rGKrJDR).", "info")
        embed.add_field(name="Example", value=me.mention + " x86\n```asm\nmov eax, sp\n```", inline=False)
        embed.add_field(name="Available architectures", value="`x86`: `x86`, `i386`\n`x86 (AT&T syntax)`: `x86_att`, `i386_att`\n`x64`: `x64`, `x86_64`\n`x64 (AT&T syntax)`: `x64_att`, "
                                                              "`x86_64_att`\n`ARMv6`: `armv6`, `armv6k`\n`ARMv7`, `armv7`, `armv7a`\n`ARMv8`: `armv8`, `aarch64`",
                        inline=False)

        await ctx.bot.say(embed=embed)

    @commands.command(name="x86", description="Assemble x86 assembly", pass_context=True, aliases=["i386"])
    async def x86(self, ctx, *, code):
        """
        Assembles x86 assembly
        """
        snip = self._extract_code(code)
        snip = ".intel_syntax noprefix\n" + snip
        snip = self._assemble(snip, "i386")

        await ctx.bot.say("```\n" + snip + "\n```")

    @commands.command(name="x86_att", description="Assemble x86 assembly using AT&T syntax", pass_context=True, aliases=["i386_att"])
    async def x86_att(self, ctx, *, code):
        """
        Assembles x86 assembly using AT&T syntax
        """
        snip = self._extract_code(code)
        snip = self._assemble(snip, "i386")

        await ctx.bot.say("```\n" + snip + "\n```")

    @commands.command(name="x64", description="Assemble x64 assembly", pass_context=True, aliases=["x86_64"])
    async def x64(self, ctx, *, code):
        """
        Assembles x64 assembly
        """
        snip = self._extract_code(code)
        snip = ".intel_syntax noprefix\n" + snip
        snip = self._assemble(snip, "x86_64")

        await ctx.bot.say("```\n" + snip + "\n```")

    @commands.command(name="x64_att", description="Assemble x64 assembly using AT&T syntax", pass_context=True, aliases=["x86_64_att"])
    async def x64_att(self, ctx, *, code):
        """
        Assembles x64 assembly using AT&T syntax
        """
        snip = self._extract_code(code)
        snip = self._assemble(snip, "x86_64")

        await ctx.bot.say("```\n" + snip + "\n```")

    @commands.command(name="armv6", description="Assemble ARMv6 assembly", pass_context=True, aliases=["armv6k"])
    async def armv6(self, ctx, *, code):
        """
        Assembles ARMv6 assembly
        """
        snip = self._extract_code(code)
        snip = self._assemble(snip, "armv6-arm-none-eabi", "-mfloat-abi=hard")

        await ctx.bot.say("```\n" + snip + "\n```")

    @commands.command(name="armv7", description="Assemble ARMv7 assembly", pass_context=True, aliases=["armv7a"])
    async def armv7(self, ctx, *, code):
        """
        Assembles ARMv7 assembly
        """
        snip = self._extract_code(code)
        snip = self._assemble(snip, "armv7a-arm-none-eabi", "-mfloat-abi=hard")

        await ctx.bot.say("```\n" + snip + "\n```")

    @commands.command(name="armv8", description="Assemble ARMv8 assembly", pass_context=True, aliases=["aarch64"])
    async def armv8(self, ctx, *, code):
        """
        Assembles ARMv8 assembly
        """
        snip = self._extract_code(code)
        snip = self._assemble(snip, "aarch64-arm-none-eabi")

        await ctx.bot.say("```\n" + snip + "\n```")
