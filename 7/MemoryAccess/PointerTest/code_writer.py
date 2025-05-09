class CodeWriter:
    def __init__(self, output_path):
        self.file = open(output_path, 'w')
        self.label_counter = 0

    def write_arithmetic(self, command):
        if command in ["add", "sub", "and", "or"]:
            self._binary_op(command)
        elif command in ["neg", "not"]:
            self._unary_op(command)
        elif command == "eq":
            self._compare("JEQ")
        elif command == "gt":
            self._compare("JGT")
        elif command == "lt":
            self._compare("JLT")

    def write_push_pop(self, cmd_type, segment, index):
        if cmd_type == "C_PUSH":
            if segment == "constant":
                self.file.write(
                    f"@{index}\n"
                    "D=A\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
        elif cmd_type == "C_POP":
            # Only implemented for stack (if needed for test, expand it)
            pass

    def _binary_op(self, command):
        op_map = {
            "add": "M=D+M",
            "sub": "M=M-D",
            "and": "M=D&M",
            "or":  "M=D|M"
        }
        self.file.write(
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "@SP\n"
            "AM=M-1\n"
            f"{op_map[command]}\n"
            "@SP\n"
            "M=M+1\n"
        )

    def _unary_op(self, command):
        op_map = {
            "neg": "-M",
            "not": "!M"
        }
        self.file.write(
            "@SP\n"
            "A=M-1\n"
            f"M={op_map[command]}\n"
        )

    def _compare(self, jump_command):
        self.label_counter += 1
        label_true = f"TRUE_{self.label_counter}"
        label_end = f"END_{self.label_counter}"

        self.file.write(
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "@SP\n"
            "AM=M-1\n"
            "D=M-D\n"
            f"@{label_true}\n"
            f"D;{jump_command}\n"
            "@SP\n"
            "A=M\n"
            "M=0\n"
            f"@{label_end}\n"
            "0;JMP\n"
            f"({label_true})\n"
            "@SP\n"
            "A=M\n"
            "M=-1\n"
            f"({label_end})\n"
            "@SP\n"
            "M=M+1\n"
        )

    def close(self):
        self.file.close()
