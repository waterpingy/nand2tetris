from parser import Parser
from code_writer import CodeWriter
import sys, os

def main():
    input_file = sys.argv[1]
    output_file = input_file.replace(".vm", ".asm")
    
    parser = Parser(input_file)
    writer = CodeWriter(output_file)

    while parser.has_more_commands():
        parser.advance()
        cmd_type = parser.command_type()

        if cmd_type == "C_ARITHMETIC":
            writer.write_arithmetic(parser.arg1())
        elif cmd_type in ["C_PUSH", "C_POP"]:
            writer.write_push_pop(cmd_type, parser.arg1(), parser.arg2())

    writer.close()

if __name__ == "__main__":
    main()
