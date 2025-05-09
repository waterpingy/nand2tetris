from parser import Parser
from code_writer import CodeWriter
import sys, os

def main():
    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        files = [f for f in os.listdir(input_path) if f.endswith('.vm')]
        output_file = os.path.join(input_path, os.path.basename(input_path) + '.asm')
    else:
        files = [os.path.basename(input_path)]
        input_path = os.path.dirname(input_path)
        output_file = os.path.join(input_path, files[0].replace('.vm', '.asm'))

    cw = CodeWriter(output_file)

    # Bootstrap code
    cw.file.write("@256\nD=A\n@SP\nM=D\n")
    cw.write_call("Sys.init", 0)

    for file in files:
        parser = Parser(os.path.join(input_path, file))
        while parser.has_more_commands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type == "C_ARITHMETIC":
                cw.write_arithmetic(parser.arg1())
            elif cmd_type in ["C_PUSH", "C_POP"]:
                cw.write_push_pop(cmd_type, parser.arg1(), parser.arg2())
            elif cmd_type == "C_LABEL":
                cw.write_label(parser.arg1())
            elif cmd_type == "C_GOTO":
                cw.write_goto(parser.arg1())
            elif cmd_type == "C_IF":
                cw.write_if(parser.arg1())
            elif cmd_type == "C_FUNCTION":
                cw.write_function(parser.arg1(), parser.arg2())
            elif cmd_type == "C_CALL":
                cw.write_call(parser.arg1(), parser.arg2())
            elif cmd_type == "C_RETURN":
                cw.write_return()

    cw.close()

if __name__ == "__main__":
    main()
