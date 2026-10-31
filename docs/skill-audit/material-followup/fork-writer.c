#define _POSIX_C_SOURCE 200809L
#include <fcntl.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    pid_t pid = fork();
    if (pid < 0) return 3;
    if (pid == 0) {
        int fd = open(argv[1], O_RDWR);
        char original;
        if (fd < 0 || pread(fd, &original, 1, 0) != 1) _exit(4);
        unsigned seed = 37;
        for (int i = 0; i < 64; i++) {
            seed = seed * 1664525u + 1013904223u;
            char value = (char)(seed & 255u);
            if (pwrite(fd, &value, 1, 0) != 1) _exit(5);
        }
        if (pwrite(fd, &original, 1, 0) != 1 || close(fd) != 0) _exit(6);
        _exit(0);
    }
    int status;
    if (waitpid(pid, &status, 0) != pid) return 7;
    return WIFEXITED(status) ? WEXITSTATUS(status) : 8;
}
