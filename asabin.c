/* asabin.c */

#include <stdio.h>
#include <unistd.h>

const char *shellexec = "asash";
const char *absshellexec = "/opt/local/bin/asash";
#ifdef __MACH__
const char *searchpath = "/usr/local/bin:/opt/local/bin:/opt/bin:/usr/bin:/bin:/usr/sbin:/sbin:.";
#endif

int main(int argc, char *argv[]) {
#ifdef __MACH__
	execvP(shellexec, searchpath, argv);
#else
	execv(absshellexec, argv);
#endif
	perror("asabin: exec failed");
	return 1;
}
