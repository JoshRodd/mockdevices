/* asabin.c */

#include <stdio.h>
#include <unistd.h>

char *shellexec = "asash";
char *absshellexec = "/usr/local/bin/asash";
char *option = "214.0.0.1";
char *option2 = "22";
char *shellargv[3];
char *searchpath = "/usr/local/bin:/opt/local/bin:/opt/bin:/usr/bin:/bin:/usr/sbin:/sbin:.";

int main(int argc, char *argv[]) {
	shellargv[0] = option;
	shellargv[1] = option2;
	shellargv[2] = NULL;
#ifdef __MACH__
	execvP(shellexec, searchpath, shellargv);
#else
	execv(absshellexec, shellargv);
#endif
	perror("asabin214_0_0_1: exec failed");
	return 1;
}
