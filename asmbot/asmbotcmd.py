import subprocess
import discord
from discord.ext import commands


class AsmBotCommands:
    def __init__(self, bot):
        self._bot = bot
        # Commented out ones require clang-4.0+ or binaries not available on my system. Feel free to test them, and enable them if they work for you.
        self._archmap = [
            ArchitectureMap("x86", "i686-pc-none-gnu", "", ".intel_syntax noprefix", "x86", "i386", "i486", "i586", "i686"),
            ArchitectureMap("x64", "amd64-pc-none-gnu", "", ".intel_syntax noprefix", "x64", "x86_64", "amd64"),
            ArchitectureMap("x86 (AT&T syntax)", "i686-pc-none-gnu", "", "", "x86_att", "i386_att", "i486_att", "i586_att", "i686_att"),
            ArchitectureMap("x64 (AT&T syntax)", "amd64-pc-none-gnu", "", "", "x64_att", "x86_64_att", "amd64_att"),
            ArchitectureMap("ARMv6", "armv6-arm-none-eabi", "-mfloat-abi=hard", "", "armv6", "armv6k"),
            ArchitectureMap("ARMv6 (big-endian)", "armv6eb-arm-none-eabi", "-mfloat-abi=hard", "", "armv6eb", "armv6keb", "armv6_be", "armv6k_be"),
            ArchitectureMap("ARMv7", "armv7a-arm-none-eabi", "-mfloat-abi=hard", "", "armv7", "armv7a"),
            ArchitectureMap("ARMv7 (big-endian)", "armv7aeb-arm-none-eabi", "-mfloat-abi=hard", "", "armv7eb", "armv7aeb", "armv7_be", "armv7a_be"),
            ArchitectureMap("ARMv8", "armv8a-arm-none-eabi", "", "", "armv8", "armv8a"),
            ArchitectureMap("ARMv8 (big-endian)", "armv8aeb-arm-none-eabi", "", "", "armv8eb", "armv8aeb", "armv8_be", "armv8a_be"),
            ArchitectureMap("AArch64 (64-bit ARMv8)", "aarch64-arm-none-eabi", "", "", "aarch64", "arm64"),
            ArchitectureMap("AArch64 (64-bit ARMv8, big-endian)", "aarch64_be-arm-none-eabi", "", "", "aarch64eb", "arm64eb", "aarch64_be", "arm64_be"),
            ArchitectureMap("MIPS", "mips-pc-none-gnu", "", "", "mips"),
            ArchitectureMap("MIPS (little-endian)", "mipsel-pc-none-gnu", "", "", "mipsel", "mips_le"),
            # ArchitectureMap("MIPS64", "mips64-pc-none-gnu", "", "", "mips64"),
            # ArchitectureMap("MIPS64 (little-endian)", "mips64el-pc-none-gnu", "", "", "mips64el", "mips64_le"),
            ArchitectureMap("PowerPC", "powerpc-pc-none-gnu", "", "", "powerpc", "powerpc32", "ppc", "ppc32"),
            ArchitectureMap("PowerPC64", "powerpc64-pc-none-gnu", "", "", "powerpc64", "ppc64"),
            ArchitectureMap("PowerPC64 (little-endian)", "powerpc64le-pc-none-gnu", "", "", "powerpc64el", "ppc64el", "powerpc64_le", "ppc64_le"),
            # ArchitectureMap("Atmel AVR", "avr-none-none-gnu", "", "", "avr", "atmel"),
            # ArchitectureMap("TI MSP430", "msp430-none-none-gnu", "", "", "msp430")
            # ArchitectureMap("RISC-V", "riscv32-pc-none-gnu", "", "", "riscv32")
            # ArchitectureMap("RISC-V 64", "riscv64-pc-none-gnu", "", "", "riscv64")
            # ArchitectureMap("Qualcomm Hexagon", "hexagon-pc-none-gnu", "", "", "hexagon", "qdsp6")
            # ArchitectureMap("S390x", "s390x-pc-none-gnu", "", "", "s390x")
            # ArchitectureMap("SPARC", "sparc-pc-none-gnu", "", "", "sparc")
            # ArchitectureMap("SPARC (little-endian)", "sparcel-pc-none-gnu", "", "", "sparcel", "sparc_le")
            # ArchitectureMap("SPARC v9 (SPARC64)", "sparc64-pc-none-gnu", "", "", "sparcv9", "sparc64")
            # ArchitectureMap("XCore", "xcore-pc-none-gnu", "", "", "xcore")
            # ArchitectureMap("SPARC", "sparc-pc-none-gnu", "", "", "sparc")
        ]

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
    async def help(self, ctx, *, architecture: str = None):
        """
        Prints help
        """
        me = ctx.message.channel.server.me

        if architecture is None:
            embed = self._embed(ctx, "Assembler help", "To invoke Assembler, call {} assemble `<architecture>` `<assembly code block>`. For help, call {} help or {} help `[architecture]` to show how"
                                                       " to assemble for given architecture. Source code of the bot is available [on Emzi's GitHub](https://github.com/Emzi0767/Discord-ASM-Bot). To"
                                                       " invite the bot to your server, Follow [this invite link]"
                                                       "(https://discordapp.com/oauth2/authorize?client_id=283200903937261569&scope=bot&permissions=0). For more help or support, join [Emzi's server]"
                                                       "(https://discord.gg/rGKrJDR).".format(me.mention, me.mention, me.mention), "info")
            embed.add_field(name="Example", value=me.mention + " assemble x86 ```x86asm\nmov eax, sp\n```", inline=False)

            archstr = "• " + "\n• ".join(x.display_name for x in self._archmap)
            embed.add_field(name="Available architectures", value=archstr, inline=False)

        else:
            arch = None
            for xarch in self._archmap:
                if xarch.display_name == architecture:
                    arch = xarch

            if arch is None:
                raise Exception("Unknown architecture specified")

            embed = self._embed(ctx, "Architecture help", "Architecture name: {}\nArchitecture full name: `{}`".format(arch.display_name, arch.clang_name))

            archstr = ", ".join("`{}`".format(x) for x in arch.names)
            embed.add_field(name="Architecture aliases", value=archstr, inline=False)

        await ctx.bot.say(embed=embed)

    @commands.command(name="assemble", description="Assembles given assembly for given architecture", pass_context=True, aliases=["asm"])
    async def assemble(self, ctx, architecture: str, *, code):
        """
        Assembles given assembly for given architecture
        """
        architecture = architecture.lower()
        arch = None
        for xarch in self._archmap:
            if architecture in xarch.names:
                arch = xarch

        if arch is None:
            raise Exception("Unknown architecture specified")

        snip = self._extract_code(code)
        if arch.code_addon is not None:
            snip = arch.code_addon + snip
        snip = self._assemble(snip, arch.clang_name, arch.clang_options)

        await ctx.bot.say("```\n" + snip + "\n```")


class ArchitectureMap(object):
    def __init__(self, display_name: str, clang_name: str, clang_opt: str, code_add: str, *names: str):
        self.display_name = display_name
        self.clang_name = clang_name
        self.clang_options = clang_opt
        self.code_addon = code_add
        self.names = names
