"""
Obfuscates the code and makes it a one-liner
"""
import dis
from opcodes import opcodes_map


def emulate(bytecode: dis.Bytecode):
    stack = []
    indents = []

    start = '(lambda: ['
    end = '][-1])()'

    instr_i = 0
    instructions = list(bytecode)

    # for instr in bytecode:
    #     instructions.append(instr)
    #     if instr.opname == 'JUMP_FORWARD':
    #         # else branch is not implemented in the bytecode, so in order to decompile it with proper indents
    #         # I created this instruction
    #         instructions.append(
    #             dis.Instruction(opname='SUP_ELSE', opcode=-111, arg=instr.arg, argval=instr.argval,
    #                             argrepr=instr.argrepr, offset=instr.offset + 2,
    #                             starts_line=0, is_jump_target=False)
    #         )

    while instr_i < len(instructions):
        instr = instructions[instr_i]
        instr_i += 1

        if instr.opname not in opcodes_map:
            raise ValueError(f'Unknown opname: {instr.opname}')

        instruction = opcodes_map[instr.opname](instr, stack, {}, instr_i, indents.copy(), instructions)
        res = instruction.execute_onelinerizer()
        start += res[0]
        end = res[1] + end
        stack = instruction.stack
        instr_i = instruction.index
        indents = instruction.indents

    print(start + end)


if __name__ == '__main__':
    from samples.sum import main as sample
    dis.dis(sample)

    emulate(dis.Bytecode(sample))
