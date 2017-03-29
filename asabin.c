/* asabin.c */

#include <stdio.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
	execvp("asash", argv);
	execvp("/opt/local/bin/asash", argv);
	perror("asabin: execvp(\"asash\", ...) failed");
	return 1;
}
