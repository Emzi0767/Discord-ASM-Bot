#!/bin/bash

# Target:
# i386
#   x86, i386
#
# x86_64
#   x64, x86_64
#
# armv6-arm-none-eabi
# -mfloat-abi=hard
#   armv6
#
# armv7a-arm-none-eabi
# -mfloat-abi=hard
#   armv7
#
# aarch64-arm-none-eabi
#   armv8, aarch64

cat <&0 | clang-3.9 --target=$1 $2 -x assembler -c -o /proc/self/fd/1 /proc/self/fd/0 | llvm-objdump-3.9 -s -j .text /proc/self/fd/0
