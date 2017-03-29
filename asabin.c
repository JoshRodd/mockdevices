/* asabin.c */

#include <stdio.h>
#include <unistd.h>

const char *shellexec = "asash";
const char *searchpath = "/usr/local/bin:/opt/local/bin:/opt/bin:/usr/bin:/bin:/usr/sbin:/sbin:.";

int main(int argc, char *argv[]) {
	execvP(shellexec, searchpath, argv);
	perror("asabin: execvp failed");
	return 1;
}
