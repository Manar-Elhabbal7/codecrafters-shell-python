import sys

commands = {
    "exit": lambda code=0, *_: sys.exit(int(code)),
    "echo": lambda *args: print(" ".join(args)),
    "type": lambda command: print(
         f"{command} is a shell builtin" if command in commands else
        f"{command}: not found"
    ),

}
def main():
    while(True):
        sys.stdout.write("$ ")
        sys.stdout.flush()

        user_input = input().split()

        command =user_input[0]
        args =user_input[1:]

        if command in commands:
            commands[command](*args)
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
