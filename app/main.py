import sys
import os
import subprocess

def cmd_exit(code="0", *_):
    sys.exit(int(code))

def cmd_echo(*args):
    print(" ".join(args))

def cmd_type(command):
    if command in builtins:
        print(f"{command} is a shell builtin")
    else:
        path = find_executable(command)
        if path:
            print(f"{command} is {path}")
        else:
            print(f"{command}: not found")

builtins = {
    "exit": cmd_exit,
    "echo": cmd_echo,
    "type": cmd_type
}

path  = os.getenv("PATH", "")
paths = path.split(os.pathsep)

def find_executable(command):
    for path in paths:
        full_path = os.path.join(path, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        user_input = input().split()
        if not user_input:
            continue

        command = user_input[0]
        args = user_input[1:]
        
        
        if command in builtins:
            builtins[command](*args)
        else:
            path = find_executable(command)
            if path:
                subprocess.run([path] + args)
            else:
                print(f"{command}: not found")

if __name__ == "__main__":
    main()
