class Parser:
    def __init__(self, file_path):
        with open(file_path) as f:
            self.commands = []
            for line in f:
                clean = line.split('//')[0].strip()
                if clean:
                    self.commands.append(clean)
        self.current = -1

    def has_more_commands(self):
        return self.current < len(self.commands) - 1

    def advance(self):
        self.current += 1
        self.command = self.commands[self.current]

    def command_type(self):
        if self.command.startswith('push'):
            return 'C_PUSH'
        elif self.command.startswith('pop'):
            return 'C_POP'
        elif self.command.startswith('label'):
            return 'C_LABEL'
        elif self.command.startswith('goto'):
            return 'C_GOTO'
        elif self.command.startswith('if-goto'):
            return 'C_IF'
        elif self.command.startswith('function'):
            return 'C_FUNCTION'
        elif self.command.startswith('call'):
            return 'C_CALL'
        elif self.command.startswith('return'):
            return 'C_RETURN'
        else:
            return 'C_ARITHMETIC'

    def arg1(self):
        if self.command_type() == 'C_ARITHMETIC':
            return self.command.split()[0]
        return self.command.split()[1]

    def arg2(self):
        return int(self.command.split()[2])
