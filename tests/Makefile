CC_x86=i686-w64-mingw32-gcc
CC_x64=x86_64-w64-mingw32-gcc

all: \
	aO0_x64.exe aO3_x64.exe aO3_x64_upx.exe aO0_x86.exe aO3_x86.exe aO3_x86_upx.exe \
	bO0_x64.exe bO3_x64.exe bO3_x64_upx.exe bO0_x86.exe bO3_x86.exe bO3_x86_upx.exe \
	cO0_x64.exe cO3_x64.exe cO3_x64_upx.exe cO0_x86.exe cO3_x86.exe cO3_x86_upx.exe

%O0_x64.exe: %.c
	$(CC_x64) -O0 $^ -o $@

%O3_x64.exe: %.c
	$(CC_x64) -O3 $^ -o $@ -s -Qn -fno-ident
	strip -s -R .comment $@

%O0_x86.exe: %.c
	$(CC_x86) -O0 $^ -o $@

%O3_x86.exe: %.c
	$(CC_x86) -O3 $^ -o $@ -s -Qn -fno-ident
	strip -s -R .comment $@

%O3_x64_upx.exe: %O3_x64.exe
	-rm -f $@
	upx -o $@ $^

%O3_x86_upx.exe: %O3_x86.exe
	-rm -f $@
	upx -o $@ $^

