#!/bin/bash

xxd -l 6 -ps /dev/null | xxd -r -ps > a.bin
xxd -l 6 -ps /dev/null | xxd -r -ps > b.bin
xxd -l 6 -ps /dev/null | xxd -r -ps > c.bin

echo "This is a common string" >> a.bin
echo "This is a common string" >> b.bin
echo "This is a common string" >> c.bin

xxd -l 6 -ps /dev/null | xxd -r -ps >> a.bin
xxd -l 6 -ps /dev/null | xxd -r -ps >> b.bin
xxd -l 6 -ps /dev/null | xxd -r -ps >> c.bin

echo "This string is unique to a.bin." >> a.bin
echo "This string is unique to b.bin." >> b.bin
echo "This string is unique to c.bin." >> c.bin

xxd -l 6 -ps /dev/null | xxd -r -ps >> a.bin
xxd -l 6 -ps /dev/null | xxd -r -ps >> b.bin
xxd -l 6 -ps /dev/null | xxd -r -ps >> c.bin

echo "Another common string" >> a.bin
echo "Another common string" >> b.bin
echo "Another common string" >> c.bin

xxd -l 6 -ps /dev/null | xxd -r -ps >> a.bin
xxd -l 6 -ps /dev/null | xxd -r -ps >> b.bin
xxd -l 6 -ps /dev/null | xxd -r -ps >> c.bin

