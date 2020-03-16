#include <stdio.h>

void foo(int a)
{
	if( a < 42 )
		puts("String AA");
	else if ( a > 42 )
		puts("String AB");
	else
		puts("String AC");
}

int bar(int a)
{
	int x = a * 1337;
	x %= 13;
	if( x == 3 )
		x *= 31;
	else if( x == 7 )
		x *= 42;
	else
		x += 3;
	return x;
}

int main(int argc, char *argv[])
{
	puts("Software A");
	foo(42);
	return bar(13);
}

