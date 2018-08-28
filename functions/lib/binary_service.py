import os
import subprocess


def kill_leftover_processes():
    ps_aux = str(subprocess.check_output(['/bin/ps -Ao %P,%a'], stderr=subprocess.STDOUT,
                                         shell=True), 'UTF-8')

    for s in ps_aux.splitlines()[1:]:
        line = s.strip()
        process = line.split(',')
        if len(process) > 1:
            pid = process[0]
            cmd = process[1]
            if 'chrome' in cmd or 'xvfb' in cmd:
                print('Killing process PID: ' + pid + ', CMD: ' + cmd)
                print(str(subprocess.check_output(['/usr/bin/kill -9 ' + pid], stderr=subprocess.STDOUT,
                                                  shell=True), 'UTF-8'))


def clear_tmp():
    print('Cleaning /tmp directory:')

    command = 'rm -fR '
    for file in os.listdir("/tmp"):
        command += '/tmp/' + file + ' '

    print(command)
    clear_tmp_output = subprocess.check_output(
        [command],
        stderr=subprocess.STDOUT,
        shell=True)
    print(clear_tmp_output)
