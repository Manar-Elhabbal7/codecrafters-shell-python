import sys
import subprocess
import shlex
import os


def cmd_exit(*_):   
    sys.exit(0)


def cmd_echo(*args):
    output = []
    redirect_file = None
    redirect_type = None
    i = 0
    
    while i < len(args):
        word = args[i]
        
        if word in (">", "1>", "2>"):
            if i + 1 < len(args):
                redirect_file = args[i + 1]
                redirect_type = word
                break
            i += 1
            continue
        
        if word == "'":
            if output:
                output[-1] += "'"
            else:
                output.append("'")
        elif word.startswith("'") and len(word) > 1 and word.endswith("'"):
            output.append(word[1:-1])
        else:
            output.append(word)
        
        i += 1
    
    result = " ".join(output)
    
    if redirect_file:
        output_dir = os.path.dirname(redirect_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                pass
        
        if redirect_type in (">", "1>"):
            with open(redirect_file, 'w') as f:
                f.write(result + "\n")
        else:
            with open(redirect_file, 'w') as f:
                pass 
            print(result)
    else:
        print(result)
        

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
    "exit": cmd_exit,
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


def handle_redirection(args):
    for redirect_op in (">", "1>", "2>"):
        if redirect_op in args:
            redirect_index = args.index(redirect_op)
            if redirect_index + 1 < len(args):
                output_file = args[redirect_index + 1]
                cleaned_args = args[:redirect_index]
                return cleaned_args, output_file, redirect_op
    return args, None, None


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
                cleaned_args, output_file, redirect_op = handle_redirection(args)
                
                if output_file:
                    output_dir = os.path.dirname(output_file)
                    if output_dir and not os.path.exists(output_dir):
                        try:
                            os.makedirs(output_dir)
                        except OSError as e:
                            print(f"{command}: {output_file}: {e.strerror}")
                            continue
                    
                    try:
                        with open(output_file, 'w') as f:
                            if redirect_op == "2>":
                                subprocess.run([command] + cleaned_args, executable=path, stderr=f)
                            else:
                                subprocess.run([command] + cleaned_args, executable=path, stdout=f)
                    except FileNotFoundError:
                        print(f"{command}: {output_file}: No such file or directory")
                else:
                    subprocess.run([command] + cleaned_args, executable=path)
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()