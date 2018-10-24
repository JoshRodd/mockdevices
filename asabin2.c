/* asabin2.c */

#include <stdio.h>
#include <unistd.h>

const char *shellexec = "asash2";
const char *absshellexec = "/opt/local/bin/asash2";
#ifdef __MACH__
const char *searchpath = "/usr/local/bin:/opt/local/bin:/opt/bin:/usr/bin:/bin:/usr/sbin:/sbin:.";
#endif

int main(int argc, char *argv[]) {
#ifdef __MACH__
	execvP(shellexec, searchpath, argv);
#else
	execv(absshellexec, argv);
#endif
	perror("asabin2: exec failed");
	return 1;
}
