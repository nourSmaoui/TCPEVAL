#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	float delay = atof(argv[1]);
	usleep(1000000*delay);
	return 1;
}
