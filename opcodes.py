# Problem: I am simultaneously working on virtual machine, decompiler and onelinerizer
# and I want to keep all opcodes synced and in case if I found a bug in one of them, I want to fix it in all of them
# because usually bugs are caused by misunderstanding of the documentation, and it is general for all "projects".
# Moreover, opcodes in all "projects" sometimes share the similar logic so it's also cool for the sake of reusing code
from abc import ABC, abstractmethod
from dis import Instruction


class InstructionABC(ABC):
    NAME = 'ABSTRACT_INSTRUCTION'

    def __init__(self,
                 instr: Instruction,
                 stack: list,
                 co_varnames: dict,
                 index: int,
                 indents: list = None,
                 next_instrs: list[Instruction] = None
                 ):
        """
        Constructor for the instruction. Probably not the best way to do it, but it's the first idea
        which came up at 11pm
        :param instr: instruction from dis
        :param stack: stack from VM or decompiler
        :param co_varnames: dict of variables from VM or decompiler
        :param current_index: current index of the instruction
        :param indents: list of indents from decompiler
        :param next_instrs: list of instructions from decompiler

        index is the index after the instruction is executed
        """
        self.instr = instr
        self.stack = stack
        self.co_varnames = co_varnames
        self.index = index
        self.indents = indents
        self.next_instrs = next_instrs

    @abstractmethod
    def execute_vm(self):
        """
        Method to execute the instruction on VM
        """
        pass

    @abstractmethod
    def execute_decompiler(self) -> str:
        """
        Method to execute the instruction on decompiler
        :return: string to append to the output
        """
        pass

    @abstractmethod
    def execute_onelinerizer(self) -> tuple[str, str]:
        """
        Method to execute the instruction on onelinerizer
        :return: tuple of strings to append to the start and end
        """
        pass


class PopTop(InstructionABC):
    NAME = 'POP_TOP'

    def execute_vm(self):
        self.stack.pop()

    def execute_decompiler(self) -> str:
        return f'{self.stack.pop()}'

    def execute_onelinerizer(self) -> tuple[str, str]:
        return self.stack.pop() + ', ', ''


class Return(InstructionABC):
    NAME = 'RETURN_VALUE'

    def execute_vm(self):
        self.stack.pop()

    def execute_decompiler(self) -> str:
        return f'return {self.stack.pop()}'

    def execute_onelinerizer(self) -> tuple[str, str]:
        return str(self.stack.pop()) + ', ', ''


class Resume(InstructionABC):
    NAME = 'RESUME'
    def execute_vm(self): pass
    def execute_decompiler(self) -> str: return ''
    def execute_onelinerizer(self) -> tuple[str, str]: return '', ''


class Nop(InstructionABC):
    NAME = 'NOP'
    def execute_vm(self): pass
    def execute_decompiler(self) -> str: return ''


class Precall(InstructionABC):
    NAME = 'PRECALL'
    def execute_vm(self): pass
    def execute_decompiler(self) -> str: return ''
    def execute_onelinerizer(self) -> tuple[str, str]: return '', ''


class BuildList(InstructionABC):
    NAME = 'BUILD_LIST'

    def execute_vm(self):
        self.stack.append(list())

    def execute_decompiler(self) -> str:
        self.execute_vm()
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_vm()
        return '', ''


class BuildTuple(InstructionABC):
    NAME = 'BUILD_TUPLE'

    def execute_vm(self):
        self.stack.append(tuple())

    def execute_decompiler(self) -> str:
        self.execute_vm()
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_vm()
        return '', ''


class BuildConstKeyMap(InstructionABC):
    NAME = 'BUILD_CONST_KEY_MAP'

    def execute_vm(self):
        keys = self.stack.pop()
        values = [self.stack.pop() for _ in range(len(keys))][::-1]
        self.stack.append(dict(zip(keys, values)))

    def execute_decompiler(self) -> str:
        keys = self.stack.pop()
        values = [self.stack.pop() for _ in range(len(keys))][::-1]
        self.stack.append(
            '{\n' + ',\n'.join(f'\t{k}: {v}' for k, v in zip(keys, values)) + '\n}'
        )
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        keys = self.stack.pop()
        values = [self.stack.pop() for _ in range(len(keys))][::-1]
        self.stack.append(
            '{' + ','.join(f'{k}: {v}' for k, v in zip(keys, values)) + '}'
        )
        return '', ''


class ImportName(InstructionABC):
    NAME = 'IMPORT_NAME'

    def execute_vm(self):
        self.stack.append(__import__(self.instr.argval))

    def execute_decompiler(self) -> str:
        self.index += 1
        return f'import {self.instr.argval}'

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.stack.append(f'__import__("{self.instr.argval}")')
        return '', ''


class ListExtend(InstructionABC):
    NAME = 'LIST_EXTEND'

    def execute_vm(self):
        seq = self.stack.pop()
        list.extend(self.stack[-self.instr.argval], seq)

    def execute_decompiler(self) -> str:
        self.execute_vm()
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_vm()
        return '', ''


class BinarySubscr(InstructionABC):
    NAME = 'BINARY_SUBSCR'

    def execute_vm(self):
        ind = self.stack.pop()
        self.stack.append(self.stack.pop()[ind])

    def execute_decompiler(self) -> str:
        ind = self.stack.pop()
        self.stack.append(f'{self.stack.pop()}[{ind}]')
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_decompiler()
        return '', ''


class UnpackSequence(InstructionABC):
    NAME = 'UNPACK_SEQUENCE'

    def execute_vm(self):
        seq = self.stack.pop()
        for el in seq[::-1]:
            self.stack.append(el)

    def execute_decompiler(self) -> str:
        self.execute_vm()
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_vm()
        return '', ''


class LoadConst(InstructionABC):
    NAME = 'LOAD_CONST'

    def execute_vm(self):
        self.stack.append(self.instr.argval)

    def execute_decompiler(self) -> str:
        if type(self.instr.argval) in (list, tuple):
            self.stack.append(self.instr.argval)
        else:
            self.stack.append(self.instr.argrepr)
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        if type(self.instr.argval) in (list, tuple):
            self.stack.append(self.instr.argval)
        else:
            self.stack.append(self.instr.argrepr)
        return '', ''


class StoreFast(InstructionABC):
    NAME = 'STORE_FAST'

    def execute_vm(self):
        self.co_varnames[self.instr.argval] = self.stack.pop()

    def execute_decompiler(self) -> str:
        return f'{self.instr.argval} = {self.stack.pop()}'

    def execute_onelinerizer(self) -> tuple[str, str]:
        return (
            f'(lambda {self.instr.argval}: [',
            f'][-1])({self.stack.pop()})'
        )


class LoadFast(InstructionABC):
    NAME = 'LOAD_FAST'

    def execute_vm(self):
        if self.co_varnames.get(self.instr.argval) is None:
            raise ValueError(f'Variable {self.instr.argval} not defined')
        self.stack.append(self.co_varnames[self.instr.argval])

    def execute_decompiler(self) -> str:
        self.stack.append(self.instr.argval)
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.stack.append(self.instr.argval)
        return '', ''


class StoreName(InstructionABC):
    NAME = 'STORE_NAME'

    def execute_vm(self):
        self.co_varnames[self.instr.argval] = self.stack.pop()

    def execute_decompiler(self) -> str: raise NotImplementedError
    def execute_onelinerizer(self) -> tuple[str, str]: raise NotImplementedError


class LoadName(InstructionABC):
    NAME = 'LOAD_NAME'

    def execute_vm(self):
        self.stack.append(self.co_varnames[self.instr.argval])

    def execute_decompiler(self) -> str: raise NotImplementedError
    def execute_onelinerizer(self) -> tuple[str, str]: raise NotImplementedError


class LoadGlobal(InstructionABC):
    NAME = 'LOAD_GLOBAL'

    def execute_vm(self):
        # print(__builtins__.get('input'))
        # self.stack.append(getattr(__builtins__, self.instr.argval))
        self.stack.append(__builtins__.get(self.instr.argval))  # idk

    def execute_decompiler(self) -> str:
        self.stack.append(self.instr.argval)
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_decompiler()
        return '', ''


class LoadMethod(InstructionABC):
    NAME = 'LOAD_METHOD'

    def execute_vm(self):
        self.stack.append(getattr(self.stack.pop(), self.instr.argval))

    def execute_decompiler(self) -> str:
        self.stack.append(f'{self.stack.pop()}.{self.instr.argval}')
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_decompiler()
        return '', ''


class Call(InstructionABC):
    NAME = 'CALL'

    def execute_vm(self):
        args = [self.stack.pop() for _ in range(self.instr.argval)][::-1]
        func = self.stack.pop()
        self.stack.append(func(*args))

    def execute_decompiler(self) -> str:
        args = [self.stack.pop() for _ in range(self.instr.argval)][::-1]
        func = self.stack.pop()
        self.stack.append(f'{func}({", ".join(map(str, args))})')
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        args = [self.stack.pop() for _ in range(self.instr.argval)][::-1]
        func = self.stack.pop()
        self.stack.append(f'{func}({", ".join(map(str, args))})')
        return '', ''


class GetIter(InstructionABC):
    NAME = 'GET_ITER'

    def execute_vm(self):
        self.stack.append(iter(self.stack.pop()))

    def execute_decompiler(self) -> str:
        self.stack.append(f'iter({self.stack.pop()})')
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_decompiler()
        return '', ''


class ForIter(InstructionABC):
    NAME = 'FOR_ITER'

    def execute_vm(self):
        try:
            self.stack.append(next(self.stack[-1]))
        except StopIteration:
            self.stack.pop()
            self.index = self.instr.argval // 2

    def unpack_sequence(self, next_instr) -> str:
        iter_name = []
        for _ in range(next_instr.argval):
            next_instr = self.next_instrs[self.index]
            self.index += 1
            iter_name.append(next_instr.argval)
        return ', '.join(iter_name)

    def get_iter_name(self, next_instr) -> str:
        if next_instr.opname == 'UNPACK_SEQUENCE':
            return self.unpack_sequence(next_instr)
        return next_instr.argval

    def execute_decompiler(self) -> str:
        next_instr = self.next_instrs[self.index]
        self.index += 1
        self.indents.append(self.instr.argval)
        return f'for {self.get_iter_name(next_instr)} in {self.stack.pop()}:'

    def execute_onelinerizer(self) -> tuple[str, str]:
        next_instr = self.next_instrs[self.index]
        self.index += 1
        self.indents.append(self.instr.argval)
        return f'[[', f'][-1] for {self.get_iter_name(next_instr)} in {self.stack.pop()}][-1]'


class JumpBackward(InstructionABC):
    NAME = 'JUMP_BACKWARD'

    def execute_vm(self):
        self.index = self.instr.argval // 2

    def execute_decompiler(self) -> str: return ''
    def execute_onelinerizer(self) -> tuple[str, str]: return '', ''


class JumpForward(InstructionABC):
    NAME = 'JUMP_FORWARD'

    def execute_vm(self):
        self.index = self.instr.argval // 2

    def execute_decompiler(self) -> str: return ''
    def execute_onelinerizer(self) -> tuple[str, str]: return '', ''


class SupElse(InstructionABC):
    """
    else branch is not implemented explicitly in the bytecode, so in order to decompile it with proper indents I created this instruction
    """
    NAME = 'SUP_ELSE'

    def execute_vm(self):
        raise NotImplementedError

    def execute_decompiler(self) -> str:
        self.indents.append(self.instr.argval)
        return 'else:'

    def execute_onelinerizer(self) -> tuple[str, str]:
        raise NotImplementedError
        # return '][-1]), False: (lambda: [', ''


class BinaryOp(InstructionABC):
    NAME = 'BINARY_OP'

    f = None
    s = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.s = self.stack.pop()  # for some reason operands are reversed
        self.f = self.stack.pop()

        if self.instr.argrepr.replace('=', '') not in ('+', '-', '*', '/', '%', '//'):
            raise ValueError(f'Unknown binary operation: {self.instr.argrepr}')

    def execute_vm(self):
        mmap = {
            '+': self.f + self.s,
            '-': self.f - self.s,
            '*': self.f * self.s,
            '/': self.f / self.s,
            '%': self.f % self.s,
            '//': self.f // self.s
        }
        self.stack.append(mmap[self.instr.argrepr.replace('=', '')])

    def execute_decompiler(self) -> str:
        self.stack.append(f'({self.f} {self.instr.argrepr.replace("=", "")} {self.s})')
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_decompiler()
        return '', ''


class CompareOp(InstructionABC):
    NAME = 'COMPARE_OP'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.s = self.stack.pop()  # for some reason operands are reversed
        self.f = self.stack.pop()

        if self.instr.argrepr not in ('==', '!=', '<', '>', '<=', '>='):
            raise ValueError(f'Unknown compare operation: {self.instr.argrepr}')

    def execute_vm(self):
        mmap = {
            '==': self.f == self.s,
            '!=': self.f != self.s,
            '<': self.f < self.s,
            '>': self.f > self.s,
            '<=': self.f <= self.s,
            '>=': self.f >= self.s
        }
        self.stack.append(mmap[self.instr.argrepr])

    def execute_decompiler(self) -> str:
        self.stack.append(f'{self.f} {self.instr.argrepr} {self.s}')
        return ''

    def execute_onelinerizer(self) -> tuple[str, str]:
        self.execute_decompiler()
        return '', ''


class PopJumpForwardIfFalse(InstructionABC):
    NAME = 'POP_JUMP_FORWARD_IF_FALSE'

    def execute_vm(self):
        if not self.stack.pop():
            self.index = self.instr.argval // 2

    def execute_decompiler(self) -> str:
        self.indents.append(self.instr.argval)
        return f'if {self.stack.pop()}:'

    def execute_onelinerizer(self) -> tuple[str, str]:
        return (
            '{True: (lambda: [',
            f'][-1])}}.get({self.stack.pop()}, lambda: None)()'
        )


class PopJumpForwardIfTrue(InstructionABC):
    NAME = 'POP_JUMP_FORWARD_IF_TRUE'

    def execute_vm(self):
        if self.stack.pop():
            self.index = self.instr.argval // 2

    def execute_decompiler(self) -> str:
        self.indents.append(self.instr.argval)
        return f'if not {self.stack.pop()}:'

    def execute_onelinerizer(self) -> tuple[str, str]:
        return (
            '{True: (lambda: [',
            f'][-1])}}.get(not {self.stack.pop()}, lambda: None)()'
        )


opcodes_map: dict[str: InstructionABC] = {
    'RESUME': Resume,
    'RETURN_VALUE': Return,
    'NOP': Nop,
    'POP_TOP': PopTop,
    'PRECALL': Precall,
    'BUILD_LIST': BuildList,
    'BUILD_TUPLE': BuildTuple,
    'BUILD_CONST_KEY_MAP': BuildConstKeyMap,
    'IMPORT_NAME': ImportName,
    'LIST_EXTEND': ListExtend,
    'BINARY_SUBSCR': BinarySubscr,
    'UNPACK_SEQUENCE': UnpackSequence,
    'LOAD_CONST': LoadConst,
    'STORE_FAST': StoreFast,
    'LOAD_FAST': LoadFast,
    'STORE_NAME': StoreName,
    'LOAD_NAME': LoadName,
    'LOAD_GLOBAL': LoadGlobal,
    'LOAD_METHOD': LoadMethod,
    'CALL': Call,
    'GET_ITER': GetIter,
    'FOR_ITER': ForIter,
    'JUMP_BACKWARD': JumpBackward,
    'JUMP_FORWARD': JumpForward,
    'SUP_ELSE': SupElse,
    'BINARY_OP': BinaryOp,
    'COMPARE_OP': CompareOp,
    'POP_JUMP_FORWARD_IF_FALSE': PopJumpForwardIfFalse,
    'POP_JUMP_FORWARD_IF_TRUE': PopJumpForwardIfTrue
}