/* asabin214_0_0_1.c */

/* This is suitable for using with xinetd and in.telnetd */

#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <errno.h>
#include <string.h>

#ifdef __MACH__
const char *searchpath = "/usr/local/bin:/opt/local/bin:/opt/bin:/usr/bin:/bin:/usr/sbin:/sbin:.";
char *shellexec = "asash";
char *shellargv[4] = {"asash", "214.0.0.1", "23", NULL};
#else
char *absshellexec = "/usr/local/bin/asash";
char *shellargv[4] = {"/usr/local/bin/asash", "214.0.0.1", "23", NULL};
#endif

int main(int argc, char *argv[]) {
	char ip_addr[17];
	char ip_port[6];
	unsigned int ip_a = 214, ip_b = 0, ip_c = 0, ip_d = 1, ip_e = 23;
	char *argv0 = argv[0];
	int c;
	argv0 = strstr(argv[0], "asabin");
	printf("I'm %s\b", argv0);
	if(argv0) {
		c = sscanf(argv0, "asabin%u_%u_%u_%u_%u", &ip_a, &ip_b, &ip_c, &ip_d, &ip_e);
		if (c != 5) {
			c = sscanf(argv0, "asabin%u_%u_%u_%u", &ip_a, &ip_b, &ip_c, &ip_d);
			if (c != 4) {
				ip_a = 214; ip_b = 0; ip_c = 0; ip_d = 1;
			}
			ip_e = 23;
		}
	}
	if (ip_e < 1 || ip_e > 65535) {
		fprintf(stderr, "Program name %s contains invalid port %d.\n", argv[0], ip_e);
		return 1;
	}
	if (ip_a > 255 || ip_b > 255 || ip_c > 255 || ip_d > 255) {
		fprintf(stderr, "Program name %s contains invalid address %d.%d.%d.%d.\n", argv[0],
			ip_a, ip_b, ip_c, ip_d);
		return 1;
	}
	snprintf(ip_port, 6, "%d", ip_e);
	snprintf(ip_addr, 17, "%d.%d.%d.%d", ip_a, ip_b, ip_c, ip_d);
	shellargv[1] = ip_addr;
	shellargv[2] = ip_port;
	struct passwd *ent;
	do {
		errno = 0;
		ent = getpwent();
		if (ent) { 
			if (!strcmp(ent->pw_name, "asa")) {
				if(chdir(ent->pw_dir)) {
					perror("asabin214_0_0_1: chdir ~asa failed");
					return 1;
				}
				if(getuid() != ent->pw_uid) {
					if(setgid(ent->pw_gid)) {
						perror("asabin214_0_0_1: setgid asa failed");
						return 1;
					}
					if(setuid(ent->pw_uid)) {
						perror("asabin214_0_0_1: setuid asa failed");
						return 1;
					}
				}
				#ifdef __MACH__
					execvP(shellexec, searchpath, shellargv);
				#else
					execv(absshellexec, shellargv);
				#endif
				perror("asabin214_0_0_1: exec failed");
				return 1;
			}
		}
		else if(errno) {
			perror("asabin214_0_0_1: getpwent failed");
			return 1;
		}
	} while (ent);
	perror("asabin214_0_0_1: Cannot find asa user in /etc/passwd");
	return 1;
}
