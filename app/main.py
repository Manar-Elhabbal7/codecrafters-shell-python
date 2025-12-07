import sys
import subprocess
import shlex
import os


def cmd_exit(*_):   
    sys.exit(0)

def cmd_echo(*args):
    output = []
    idx = 0

    while idx < len(args):
        word = args[idx]
        
        if word.startswith("'"):
            
            w = word[1:] 

            
            if w.endswith("'"):
                w = w[:-1]
                if w:       #handle if empty quotes    
                    output.append(w)

            else:
                
                parts = [w]
                idx += 1

                while idx < len(args) and not args[idx].endswith("'"):
                    parts.append(args[idx])
                    idx += 1

                if idx < len(args):  
                    parts.append(args[idx][:-1])

                final = " ".join(parts)
                if final:        
                    output.append(final)

        else:
            # unquoted words
            output.append(word)

        idx += 1

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
