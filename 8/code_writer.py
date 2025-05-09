class CodeWriter:
    def __init__(self, filename):
        self.file = open(filename, 'w')
        self.label_counter = 0
        self.filename = filename.split('/')[-1].replace('.asm', '')

    def write_arithmetic(self, command):
        if command == 'add':
            self._binary_op('M=D+M')
        elif command == 'sub':
            self._binary_op('M=M-D')
        elif command == 'neg':
            self._unary_op('M=-M')
        elif command == 'eq':
            self._compare_op('JEQ')
        elif command == 'gt':
            self._compare_op('JGT')
        elif command == 'lt':
            self._compare_op('JLT')
        elif command == 'and':
            self._binary_op('M=M&D')
        elif command == 'or':
            self._binary_op('M=M|D')
        elif command == 'not':
            self._unary_op('M=!M')

    def _binary_op(self, op):
        self.file.write(
            "@SP\nAM=M-1\nD=M\nA=A-1\n" + op + "\n"
        )

    def _unary_op(self, op):
        self.file.write(
            "@SP\nA=M-1\n" + op + "\n"
        )

    def _compare_op(self, jump):
        true_label = f"TRUE_{self.label_counter}"
        end_label = f"END_{self.label_counter}"
        self.label_counter += 1

        self.file.write(
            f"@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@{true_label}\nD;{jump}\n"
            "@SP\nA=M-1\nM=0\n"
            f"@{end_label}\n0;JMP\n"
            f"({true_label})\n"
            "@SP\nA=M-1\nM=-1\n"
            f"({end_label})\n"
        )

    def write_push_pop(self, command, segment, index):
        base = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
        if command == 'C_PUSH':
            if segment == 'constant':
                self.file.write(
                    f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                )
            elif segment in base:
                self.file.write(
                    f"@{index}\nD=A\n@{base[segment]}\nA=D+M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                )
        elif command == 'C_POP' and segment in base:
            self.file.write(
                f"@{index}\nD=A\n@{base[segment]}\nD=D+M\n@R13\nM=D\n"
                "@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n"
            )

    def write_label(self, label):
        self.file.write(f"({label})\n")

    def write_goto(self, label):
        self.file.write(f"@{label}\n0;JMP\n")

    def write_if(self, label):
        self.file.write(f"@SP\nAM=M-1\nD=M\n@{label}\nD;JNE\n")

    def write_function(self, name, n_vars):
        self.file.write(f"({name})\n")
        for _ in range(n_vars):
            self.file.write("@0\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

    def write_call(self, name, n_args):
        return_label = f"RETURN_{self.label_counter}"
        self.label_counter += 1
        self.file.write(
            f"@{return_label}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n"
            "@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
            "@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
            "@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
            "@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
            f"@{n_args}\nD=A\n@5\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n"
            "@SP\nD=M\n@LCL\nM=D\n"
            f"@{name}\n0;JMP\n"
            f"({return_label})\n"
        )

    def write_return(self):
        self.file.write(
            "@LCL\nD=M\n@R13\nM=D\n"
            "@5\nA=D-A\nD=M\n@R14\nM=D\n"
            "@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n"
            "@ARG\nD=M+1\n@SP\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@THAT\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@THIS\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@ARG\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@LCL\nM=D\n"
            "@R14\nA=M\n0;JMP\n"
        )

    def close(self):
        self.file.close()
