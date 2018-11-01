/* asabin.c */

#include <stdio.h>
#include <unistd.h>

#define MOCKDEVICES_PREFIX "/usr/local" /* prefix match
*/

const char *shellexec = "asash";
const char *absshellexec = MOCKDEVICES_PREFIX \
"/bin/asash";
#ifdef __MACH__
const char *searchpath = MOCKDEVICES_PREFIX \
"/bin:/opt/bin:/usr/bin:/bin:/usr/sbin:/sbin:.";
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
