"""
ASM - Assembler bot

A Discord bot by Emzi0767. Designed to quickly assemble x86, x86_64, ARM, MIPS, and PowerPC assembly.
"""

__name__ = "asmbot"
__author__ = "Emzi0767"
__version__ = "2.1.2"
__license__ = "Apache License 2.0"
__copyright__ = "Copyright 2017 Emzi0767"

version_info = tuple(__version__.split("."))

# core modules
from .asmbot import AsmBot
from .asmbotcmd import AsmBotCommands
from .asmexception import AssemblerException

# utilities
from .utils import log
from .utils import logex