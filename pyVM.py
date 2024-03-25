import dis


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

        match instr.opname:
            case 'RESUME': continue
            case 'NOP': continue
            case 'PRECALL': continue
            case 'RETURN_VALUE': stack.pop()
            case 'POP_TOP': stack.pop()
            case 'PUSH_NULL': stack.append(None)
            case 'BUILD_LIST': stack.append(list())
            case 'BUILD_TUPLE': stack.append(tuple())
            case 'BUILD_CONST_KEY_MAP':
                keys = stack.pop()
                values = [stack.pop() for _ in range(len(keys))][::-1]
                stack.append(dict(zip(keys, values)))

            case 'IMPORT_NAME':
                co_varnames[instr.argval] = __import__(instr.argval)
                instr_i += 1

            case 'LIST_EXTEND':
                seq = stack.pop()
                list.extend(stack[-instr.argval], seq)
            case 'BINARY_SUBSCR':
                ind = stack.pop()
                stack.append(stack.pop()[ind])

            case 'UNPACK_SEQUENCE':
                seq = stack.pop()
                for el in seq[::-1]:
                    stack.append(el)

            case 'LOAD_CONST':
                stack.append(instr.argval)
            case 'STORE_FAST':
                co_varnames[instr.argval] = stack.pop()
            case 'LOAD_FAST':
                if co_varnames.get(instr.argval) is None:
                    raise ValueError(f'Variable {instr.argval} not defined')
                stack.append(co_varnames[instr.argval])
            case 'STORE_NAME':
                co_varnames[instr.argval] = stack.pop()
            case 'LOAD_NAME':
                stack.append(co_varnames[instr.argval])
            case 'LOAD_GLOBAL':
                stack.append(getattr(__builtins__, instr.argval))
            case 'LOAD_METHOD':
                stack.append(getattr(stack.pop(), instr.argval))  # co_names.get(line.argval)))
            case 'CALL':
                args = [stack.pop() for _ in range(instr.argval)][::-1]
                func = stack.pop()
                stack.append(func(*args))

            case 'GET_ITER':
                stack.append(iter(stack.pop()))
            case 'FOR_ITER':
                try:
                    stack.append(next(stack[-1]))
                except StopIteration:
                    stack.pop()
                    instr_i = instr.argval // 2
            case 'JUMP_BACKWARD':
                instr_i = instr.argval // 2
            case 'JUMP_FORWARD':
                instr_i = instr.argval // 2
            case 'BINARY_OP':
                s = stack.pop()  # for some reason operands are reversed
                f = stack.pop()
                match instr.argrepr.replace('=', ''):
                    case '+':
                        stack.append(f + s)
                    case '-':
                        stack.append(f - s)
                    case '*':
                        stack.append(f * s)
                    case '/':
                        stack.append(f / s)
                    case '%':
                        stack.append(f % s)
                    case '//':
                        stack.append(f // s)
                    case _:
                        raise ValueError(f'Unknown binary operation: {instr.argrepr}')

            case 'COMPARE_OP':
                s = stack.pop()  # for some reason operands are reversed
                f = stack.pop()
                match instr.argrepr:
                    case '==':
                        stack.append(f == s)
                    case '!=':
                        stack.append(f != s)
                    case '<':
                        stack.append(f < s)
                    case '>':
                        stack.append(f > s)
                    case '<=':
                        stack.append(f <= s)
                    case '>=':
                        stack.append(f >= s)
                    case _:
                        raise ValueError(f'Unknown compare operation: {instr.argrepr}')
            case 'POP_JUMP_FORWARD_IF_FALSE':
                if not stack.pop():
                    instr_i = instr.argval // 2
            case 'POP_JUMP_FORWARD_IF_TRUE':
                if stack.pop():
                    instr_i = instr.argval // 2
            case _:
                raise ValueError(f'Unknown opname: {instr.opname}')
        # print(instr.opname, repr(instr.argval))


if __name__ == '__main__':
    from sample import main as sample
    dis.dis(sample)

    emulate(dis.Bytecode(sample))

