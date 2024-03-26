"""
Virtual machine for Python bytecode
"""

import dis
from opcodes import opcodes_map


def emulate(bytecode: dis.Bytecode):
    stack = []
    co_varnames = dict()

    instr_i = 0
    instructions = []

    # get all instructions, cuz we need to jump around and I don't understand how to do that without a list
    for instr in bytecode:
        # stupid way of padding weird offset, currently there is a situation
        # when previous instruction's offset is 8 and next is 32
        while len(instructions) and instructions[-1].offset < instr.offset - 2:
            instructions.append(
                dis.Instruction(opname='NOP', opcode=-123, arg=None, argval=None,
                                argrepr='', offset=instructions[-1].offset + 2,
                                starts_line=0, is_jump_target=False)
            )
        instructions.append(instr)

    while instr_i < len(instructions):
        instr = instructions[instr_i]
        instr_i += 1

        if instr.opname not in opcodes_map:
            raise ValueError(f'Unknown opname: {instr.opname}')

        instruction = opcodes_map[instr.opname](instr, stack, co_varnames, instr_i)
        instruction.execute_vm()
        stack = instruction.stack
        instr_i = instruction.index
        co_varnames = instruction.co_varnames


if __name__ == '__main__':
    from samples.simple_game import main as sample
    dis.dis(sample)

    emulate(dis.Bytecode(sample))
