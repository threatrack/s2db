#include <stdio.h>

void foo(int a)
{
	if( a > 13 )
		puts("String BA");
	else if ( a < 13 )
		puts("String BB");
	else
		puts("String BC");
}

int bar(int a)
{
	int x = a * 4242;
	x %= 31;
	if( x == 7 )
		x *= 13;
	else if( x == 11 )
		x *= 19;
	else
		x += 11;
	return x;
}

int main(int argc, char *argv[])
{
	puts("Software B");
	foo(13);
	return bar(42);
}

