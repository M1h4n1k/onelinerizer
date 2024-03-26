import dis
from opcodes import opcodes_map


def emulate(bytecode: dis.Bytecode):
    stack = []
    indents = []

    def ind_print(*args, **kwargs):
        print('\t' * len(indents), end='')
        print(*args, **kwargs)

    instr_i = 0
    instructions = []
    for instr in bytecode:
        instructions.append(instr)
        if instr.opname == 'JUMP_FORWARD':
            # else branch is not implemented in the bytecode, so in order to decompile it with proper indents
            # I created this instruction
            instructions.append(
                dis.Instruction(opname='SUP_ELSE', opcode=-111, arg=instr.arg, argval=instr.argval,
                                argrepr=instr.argrepr, offset=instr.offset + 2,
                                starts_line=0, is_jump_target=False)
            )

    while instr_i < len(instructions):
        instr = instructions[instr_i]
        instr_i += 1

        indents.sort(reverse=True)  # not cool for large number of elems, but I'm sure noone has more than 6-7 indents
        while len(indents) != 0 and instr.offset >= indents[-1]:
            indents.pop()

        if instr.opname not in opcodes_map:
            raise ValueError(f'Unknown opname: {instr.opname}')

        instruction = opcodes_map[instr.opname](instr, stack, {}, instr_i, indents.copy(), instructions)
        res = instruction.execute_decompiler()
        if res != '':
            ind_print(res)
        stack = instruction.stack
        instr_i = instruction.index
        indents = instruction.indents


if __name__ == '__main__':
    from samples.simple_game import main as sample
    dis.dis(sample)

    emulate(dis.Bytecode(sample))
