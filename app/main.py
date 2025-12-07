import sys
import subprocess
import shlex
import cmds_impl as cmd_impl


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
        
        if command == "exit":
            break
        
        if command in cmd_impl.builtins:
            cmd_impl.builtins[command](*args)
        else:
            path = cmd_impl.find_executable(command)

            if path:
                subprocess.run([command] + args, executable=path)
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()
