import os
from subprocess import check_output
def get_pid(name):
    return map(int,check_output(["pidof",name]).split())

def kill(pid):
	return os.system("sudo kill -9 %i" %pid)


def killpython():
	pid = get_pid("python")[1]
	kill(pid)

if __name__ == '__main__':
	killpython()