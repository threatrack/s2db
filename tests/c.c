#include <stdio.h>

void foo(long long a)
{
	if( a > 1337 )
		puts("String CA");
	else if ( a < 1337 )
		puts("String CB");
	else
		puts("String CC");
}

int bar(int a)
{
	int x = a * 1111;
	x %= 3111;
	if( x == 711 )
		x *= 1311;
	else if( x == 1111 )
		x *= 1911;
	else
		x += 1111;
	return x;
}

int main(int argc, char *argv[])
{
	puts("Software C");
	foo(1337);
	return bar(13);
}

