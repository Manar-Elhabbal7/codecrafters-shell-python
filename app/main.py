import readline
import sys
import subprocess
import shlex
import os

"""
*_ for arguments and it will be ignored 
whatever the user enter
ex : exit blabla bla 
just the program exit

"""


def cmd_exit(*_):
    sys.exit(0)


def cmd_echo(*args):
    output = []
    redirect_file = None
    redirect_type = None
    i = 0

    while i < len(args):
        word = args[i]
        if word in (">", "1>", "2>", ">>", "1>>", "2>>"):
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
            os.makedirs(output_dir)
        if redirect_type in (">", "1>"):
            with open(redirect_file, "w") as f:
                f.write(result + "\n")
        elif redirect_type in (">>", "1>>"):
            with open(redirect_file, "a") as f:
                f.write(result + "\n")
        elif redirect_type == "2>":
            with open(redirect_file, "w"):
                pass
            print(result, file=sys.stderr)
        elif redirect_type == "2>>":
            with open(redirect_file, "a"):
                pass
            print(result, file=sys.stderr)
    else:
        return result + "\n"


"""
builtin or external program or not found

"""


def cmd_type(command):
    if command in builtins:
        print(f"{command} is a shell builtin")
    else:
        path = find_executable(command)
        if path:
            print(f"{command} is {path}")
        else:
            print(f"{command}: not found")


"""
getcwd to get current working directory 
os is a library to excute with the operating system

"""


def cmd_pwd(*_):
    print(os.getcwd())


""" 
directory : the path we need to go to
norpath change the current path => the cur to the new 
~ change the path to the user path
chdir to change dir to the new path
i handled if the file not found

"""


def cmd_cd(directory):
    new_path = os.path.normpath(os.path.join(os.getcwd(), directory))

    if directory == "~":
        new_path = os.path.expanduser("~")

    try:
        os.chdir(new_path)
    except FileNotFoundError:
        print(f"cd: {directory}: No such file or directory")


auto_complete_states = {"tab_count": 0, "last_text": "", "options": []}


def auto_complete(text, state):
    if text != auto_complete_states["last_text"]:
        auto_complete_states["tab_count"] = 0
        auto_complete_states["last_text"] = text

        builtin_options = [cmd for cmd in builtins.keys() if cmd.startswith(text)]
        path_options = []

        for p in paths:
            try:
                for entry in os.listdir(p):
                    if entry.startswith(text) and os.access(
                        os.path.join(p, entry), os.X_OK
                    ):
                        path_options.append(entry)
            except (FileNotFoundError, PermissionError):
                continue

        auto_complete_states["options"] = sorted(set(builtin_options + path_options))

    if state == 0:
        auto_complete_states["tab_count"] += 1

    if auto_complete_states["tab_count"] == 1:
        if state == 0 and auto_complete_states["options"]:
            sys.stdout.write("\x07")
            sys.stdout.flush()

        if state < len(auto_complete_states["options"]):
            return auto_complete_states["options"][state] + " "
        else:
            return None
    elif auto_complete_states["tab_count"] >= 2:
        if state == 0 and auto_complete_states["options"]:
            print()
            print("  ".join(auto_complete_states["options"]))
            sys.stdout.write("$ " + readline.get_line_buffer())
            sys.stdout.flush()
        return None
    else:
        return None


def run_builtin_with_pipeline(cmd, input_pipe=None):
    r, w = os.pipe()

    stout = sys.stdout
    stin = sys.stdin

    try:
        if input_pipe:
            sys.stdin = input_pipe

        sys.stdout = os.fdopen(w, "w")
        result = builtins[cmd[0]](*cmd[1:])
        if result:
            sys.stdout.write(result)

    finally:
        sys.stdout.close()
        sys.stdout = stout
        sys.stdin = stin
    return os.fdopen(r)


def execute_pipeline(user_input):
    cmds = [shlex.split(cmd.strip()) for cmd in user_input.split("|")]
    processes = []
    prev = None

    for i, cmd in enumerate(cmds):
        command = cmd[0]

        if command in builtins:
            prev = run_builtin_with_pipeline(cmd, prev)

        else:
            path = find_executable(command)
            if not path:
                print(f"{command}: command not found")
                return

            p = subprocess.Popen(
                cmd,
                executable=path,
                stdin=prev,
                stdout=subprocess.PIPE if i < len(cmds) - 1 else None,
            )

            if prev:
                prev.close()

            prev = p.stdout
            processes.append(p)

    for p in processes:
        p.wait()

    if prev:
        sys.stdout.write(prev.read())



def cmd_history(*args):
    total = readline.get_current_history_length()

    if args and args[0].isdigit():
        limit = int(args[0])
        start = max(1, total - limit + 1)
    else:
        start = 1

    for i in range(start, total + 1):
        print(f"{i} {readline.get_history_item(i)}")


builtins = {
    "exit": cmd_exit,
    "echo": cmd_echo,
    "type": cmd_type,
    "pwd": cmd_pwd,
    "cd": cmd_cd,
    "history": cmd_history,
}

# give the path if not found give empty string
path = os.getenv("PATH", "")
# pathsep in ; in linux and unix :
paths = path.split(os.pathsep)


"""
command is the name we search about 
"""


def find_executable(command):
    for path in paths:
        full_path = os.path.join(path, command)
        # check if is file and excutable
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None


def handle_redirection(args):
    for redirect_op in (">>", "1>>", "2>>"):
        if redirect_op in args:
            redirect_index = args.index(redirect_op)
            if redirect_index + 1 < len(args):
                output_file = args[redirect_index + 1]
                cleaned_args = args[:redirect_index]
                return cleaned_args, output_file, redirect_op

    for redirect_op in (">", "1>", "2>"):
        if redirect_op in args:
            redirect_index = args.index(redirect_op)
            if redirect_index + 1 < len(args):
                output_file = args[redirect_index + 1]
                cleaned_args = args[:redirect_index]
                return cleaned_args, output_file, redirect_op

    return args, None, None


def main():

    readline.set_completer(auto_complete)
    readline.parse_and_bind("tab: complete")
    
    running = True

    while running:
        #sys.stdout.write("$ ")
        #sys.stdout.flush()
        
        try:
            user_input = input("$ ")
        except EOFError:
            break

        if not user_input.strip():
            continue



        if "|" in user_input:
            execute_pipeline(user_input)
            continue

        parts = shlex.split(user_input)
        command = parts[0]
        args = parts[1:]

        if command in builtins:
            result = builtins[command](*args)
            if result:
                sys.stdout.write(result)

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
                        if redirect_op in (">", "1>"):
                            with open(output_file, "w") as f:
                                subprocess.run(
                                    [command] + cleaned_args,
                                    executable=path,
                                    stdout=f,
                                    stderr=f if redirect_op == "2>" else None,
                                )
                        elif redirect_op in (">>", "1>>"):
                            with open(output_file, "a") as f:
                                subprocess.run(
                                    [command] + cleaned_args, executable=path, stdout=f
                                )
                        elif redirect_op == "2>":
                            with open(output_file, "w") as f:
                                subprocess.run(
                                    [command] + cleaned_args, executable=path, stderr=f
                                )
                        elif redirect_op == "2>>":
                            with open(output_file, "a") as f:
                                subprocess.run(
                                    [command] + cleaned_args, executable=path, stderr=f
                                )
                    except FileNotFoundError:
                        print(f"{command}: {output_file}: No such file or directory")
                else:
                    subprocess.run([command] + cleaned_args, executable=path)
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()
