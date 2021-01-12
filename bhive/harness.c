#define _GNU_SOURCE
#include <signal.h>
#include <stdlib.h>
#include <string.h> /* for memset */
#include <sys/ptrace.h>
#include <sys/resource.h> /* for PRIO_PROCESS */
#include <sys/user.h>     /* for user_regs_struct, PAGE_SIZE, PAGE_SHIFT */
#include <sys/wait.h>
#include <unistd.h>

#include <sched.h> /* for pinning child process */

#include <perfmon/pfmlib_perf_event.h>

#include "harness.h"

#define CHILD_MEM_SIZE 512

static int read_child_regs(pid_t child, struct user_regs_struct *regs) {
#ifdef __x86_64__
  return ptrace(PTRACE_GETREGS, child, NULL, regs);
#endif
}

int measure(char *code_to_test, unsigned long code_size,
            unsigned int unroll_factor, measure_results_t *res) {
  char child_ready_signal;
  int child_ready_pipefd[2];
  if (pipe(child_ready_pipefd) == -1) {
    perror("[PARENT, ERR] Cannot creating pipe");
    return -1;
  }

  pid_t child = fork();
  if (child == -1) { /* Error */
    perror("[PARENT, ERR] Cannot create child with fork");
    kill(child, SIGKILL);
    return -1;

  } else if (child != 0) { /* Parent program */

    close(child_ready_pipefd[1]); // Close unused write end

    /* Wait for child */
    int child_stat;
    if (wait(&child_stat) == -1) {
      perror("[PARENT, ERR] Wait error");
      kill(child, SIGKILL);
      return -1;
    }
    if (!WIFSTOPPED(child_stat)) {
      printf("[PARENT, ERR] Child not stopped by SIGSTOP.\n");
      kill(child, SIGKILL);
      return -1;
    }

    struct user_regs_struct regs;
    if (read_child_regs(child, &regs) == -1) {
      perror("[PARENT, ERR] Reading child regs");
      kill(child, SIGKILL);
      return -1;
    }

    /*
    Prepare child for testing block.
    TODO:
      - move child stack
      - copy block and tail
      - set child rip to execute test code
    */

    kill(child, SIGKILL);
    return -1;

  } else { /* Child program */
    int ret;

    close(child_ready_pipefd[0]); // Close unused read end

    /* Get perf encoding */
    pfm_initialize();
    struct perf_event_attr perf_attr;
    memset(&perf_attr, 0, sizeof(struct perf_event_attr));
    perf_attr.size = sizeof(struct perf_event_attr);
    pfm_perf_encode_arg_t pfm_arg;
    pfm_arg.attr = &perf_attr;
    pfm_arg.fstr = NULL;
    pfm_arg.size = sizeof(pfm_perf_encode_arg_t);
    ret = pfm_get_os_event_encoding("cycles:u", PFM_PLM0 | PFM_PLM3,
                                    PFM_OS_PERF_EVENT, &pfm_arg);
    if (ret != PFM_SUCCESS) {
      printf("[CHILD, ERR] Cannot get encoding: %s\n", pfm_strerror(ret));
      exit(EXIT_FAILURE);
    }
    /* Open perf event */
    perf_attr.read_format =
        PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING;
    perf_attr.disabled = 1; // Don't start immediately after opening
    int perf_fd = perf_event_open(&perf_attr, getpid(), -1, -1, 0);
    if (perf_fd < 0) {
      perror("[CHILD, ERR] Cannot create perf events");
      exit(EXIT_FAILURE);
    }
    printf("[CHILD] Perf. events opened.\n");

    /* Pin this process */
    cpu_set_t cpu_set;
    CPU_ZERO(&cpu_set);
    CPU_SET(1, &cpu_set);
    sched_setaffinity(0, sizeof(cpu_set_t), &cpu_set);
    setpriority(PRIO_PROCESS, 0, 0);
    printf("[CHILD] Process pinned\n");

    /* Let parent trace this child */
    ret = ptrace(PTRACE_TRACEME, 0, NULL, NULL);
    if (ret == -1) {
      perror("[CHILD, ERR] PTRACE_TRACEME error");
      exit(EXIT_FAILURE);
    }

    /* Stop execution until resumed by parent */
    kill(getpid(), SIGSTOP);
  }
}