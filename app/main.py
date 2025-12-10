import sys
import subprocess
import shlex
import os


def cmd_exit(*_):   
    sys.exit(0)


def cmd_echo(*args):
    output = []
    #hadle write in file
    
    
    for word in args:
        if word == "'":
            if output:
                output[-1] += "'"
            else:
                output.append("'")
        
        elif word == ">":
            if len(args) > args.index(word) + 1:
                filename = args[args.index(word) + 1]
                with open(filename, 'w') as f:
                    f.write(" ".join(output) + "\n")
                
                open(filename, 'a').close()
                return
       
        
        elif word.startswith("'") and len(word) > 1 and word.endswith("'"):
            output.append(word[1:-1])
        else:
            # unquoted words
            output.append(word)

    print(" ".join(output))

def cmd_type(command):
    if command in builtins:
        print(f"{command} is a shell builtin")
    else:
        path = find_executable(command)
        if path:
            print(f"{command} is {path}")
        else:
            print(f"{command}: not found")


def cmd_pwd(*_):
    print(os.getcwd())


def cmd_cd(directory):
    new_path = os.path.normpath(os.path.join(os.getcwd(), directory))
    if directory == "~":
        new_path = os.path.expanduser("~")
    try:
        os.chdir(new_path)
    except FileNotFoundError:
        print(f"cd: {directory}: No such file or directory")


builtins = {
    "exit":cmd_exit,
    "echo": cmd_echo,
    "type": cmd_type,
    "pwd": cmd_pwd,
    "cd": cmd_cd,
}

path = os.getenv("PATH", "")
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
        
        user_input = input()
        
        if not user_input.strip():
            continue
        
        parts = shlex.split(user_input)
        
        command = parts[0]
        args = parts[1:]
        
        
        if command in builtins:
            builtins[command](*args)
        else:
            path = find_executable(command)

            if path:
                subprocess.run([command] + args, executable=path)
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()
