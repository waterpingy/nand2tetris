class Parser:
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        self.commands = [line.strip().split("//")[0].strip() for line in lines if line.strip() and not line.startswith("//")]
        self.current_command = ""
        self.index = -1

    def has_more_commands(self):
        return self.index + 1 < len(self.commands)

    def advance(self):
        self.index += 1
        self.current_command = self.commands[self.index]

    def command_type(self):
        if self.current_command.startswith("push"):
            return "C_PUSH"
        elif self.current_command.startswith("pop"):
            return "C_POP"
        else:
            return "C_ARITHMETIC"

    def arg1(self):
        parts = self.current_command.split()
        if self.command_type() == "C_ARITHMETIC":
            return parts[0]
        return parts[1]

    def arg2(self):
        parts = self.current_command.split()
        return int(parts[2])
