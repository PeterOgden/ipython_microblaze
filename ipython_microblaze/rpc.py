import pycparser
import struct
import functools
import itertools
from pycparser import c_ast
from pycparser import c_generator
from copy import deepcopy

from .compile import preprocess
from . import MicroblazeProgram

# Use a global parser and generator
_parser = pycparser.CParser()
_generator = c_generator.CGenerator()

# First we define a series of classes to represent types
# Each class is responsible for one particular type of C
# types
class StructWrapper:
    """ Wrapper for C primitives that can be represented by
    a single Struct string

    """
    def __init__(self, struct_string):
        self._struct = struct.Struct(struct_string)
        self.typedefname = None
    
    def param_encode(self, old_val):
        return self._struct.pack(old_val)
    
    def param_decode(self, old_val, stream):
        pass
    
    def return_decode(self, stream):
        data = stream.read(self._struct.size)
        return self._struct.unpack(data)[0]


class ConstCharWrapper:
    """ Wrapper for const char pointers, transfers data in only
    one direction.

    """
    def __init__(self):
        self._lenstruct = struct.Struct('h')
        self.typedefname = None
        
    def param_encode(self, old_val):
        return self._lenstruct.pack(len(old_val)) + old_val
    
    def param_decode(self, old_val, stream):
        pass
    
    def return_decode(self, stream):
        raise RuntimeError("Cannot use a char* decoder as a return value")


class CharWrapper:
    """ Wrapper for non-const char pointers that retrieves any
    data modified by the called function.

    """
    def __init__(self):
        self._lenstruct = struct.Struct('h')
        self.typedefname = None
        
    def param_encode(self, old_val):
        return self._lenstruct.pack(len(old_val)) + old_val
    
    def param_decode(self, old_val, stream):
        data = stream.read(self._lenstruct.size)
        length = self._lenstruct.unpack(data)[0]
        assert(length == len(old_val))
        old_val[:] = stream.read(length)
    
    def return_decode(self, stream):
        raise RuntimeError("Cannot use a char* decoder as a return value")


class VoidWrapper:
    """ Wraps void - only valid for return types

    """
    def __init__(self):
        self.typedefname = None
        
    def param_encode(self, old_val):
        return b''
    
    def param_decode(self, old_val, stream):
        pass
    
    def return_decode(self, stream):
        return None


def _type_to_interface(tdecl, typedefs):
    """ Returns a wrapper for a given C AST

    """        
    
    if type(tdecl) is c_ast.PtrDecl:
        nested_type = tdecl.type
        if type(nested_type) is not c_ast.TypeDecl:
            raise RuntimeError("Only single level pointers supported")
        if 'char' in nested_type.type.names:
            if 'const' in nested_type.quals:
                return ConstCharWrapper()
            else:
                return CharWrapper()
        else:
            raise RuntimeError("Only pointers to char supported")
    elif type(tdecl) is not c_ast.TypeDecl:
        raise RuntimeError("Unsupport Type")
        
    names = tdecl.type.names
    signed = True
    if len(names) == 2:
        if names[0] == 'unsigned':
            unsigned = False
        name = names[1]
    else:
        name = names[0]
    if name == 'void':
        return VoidWrapper()
    if name in ['long', 'int']:
        if signed:
            return StructWrapper('l')
        else:
            return StructWrapper('L')
    if name == 'short':
        if signed:
            return StructWrapper('h')
        else:
            return StructWrapper('H')
    if name == 'char':
        if signed:
            return StructWrapper('b')
        else:
            return StructWrapper('B')
    if name == 'float':
        return StructWrapper('f')
    if name in typedefs:
        interface = _type_to_interface(typedefs[name], typedefs)
        interface.typedefname = name
        return interface
    raise RuntimeError(f'Unknown type {name}')

def _generate_read(name, size=None, address=True):
    """ Helper function to generate read functions. size
    should be an AST fragment

    """
    if size is None:
        size = c_ast.UnaryOp('sizeof', c_ast.ID(name))
    if address:
        target = c_ast.UnaryOp('&', c_ast.ID(name))
    else:
        target = c_ast.ID(name)

    return c_ast.FuncCall(
        c_ast.ID('read'),
        c_ast.ExprList([c_ast.Constant('int', '0'), 
                        target,
                        size]))

def _generate_write(name, address=True):
    """ Helper function generate write functions

    """
    if address:
        target = c_ast.UnaryOp('&', c_ast.ID(name))
    else:
        target = c_ast.ID(name)
    return c_ast.FuncCall(
        c_ast.ID('write'),
        c_ast.ExprList([c_ast.Constant('int', '1'), 
                        target,
                        c_ast.UnaryOp('sizeof', c_ast.ID(name))]))

def _generate_decl(name, decl):
    """ Generates a new declaration with a difference name
    but same type as the provided decl.

    """
    typedecl = c_ast.TypeDecl(name, [], decl.type)
    return c_ast.Decl(name, [], [], [], typedecl, [], [])

def _generate_arraydecl(name, decl, length):
    """ Generates a new declaration with an array type
    base on an existing declaration

    """
    typedecl = c_ast.TypeDecl(name, [], decl.type)
    arraydecl = c_ast.ArrayDecl(typedecl, length, [])
    return c_ast.Decl(name, [], [], [], arraydecl, [], [])

class FuncAdapter:
    """Provides the C and Python interfaces for a function declaration

    Attributes
    ----------
    return_interface : *Wrapper
        The type wrapper for the return type
    arg_interfaces   : [*Wrapper]
        An array of type wrappers for the arguments
    call_ast         : pycparser.c_ast
        Syntax tree for the wrapped function call
 
    """
    def __init__(self, decl, typedefs):
        self.return_interface = _type_to_interface(decl.type, typedefs)
        self.name = decl.type.declname
        
        self.arg_interfaces = []
    
        block_contents = []
        post_block_contents = []
        func_args = []
        
        if decl.args:
            for i, arg in enumerate(decl.args.params):
                interface = _type_to_interface(arg.type, typedefs)
                if type(interface) is ConstCharWrapper:
                    func_args.append(c_ast.ID(f'arg{i}'))
                    block_contents.append(
                        _generate_decl(
                            f'arg{i}_len',
                            c_ast.TypeDecl(f'arg{i}_len', [], 
                                           c_ast.IdentifierType(['unsigned', 'short']))))
                    block_contents.append(_generate_read(f'arg{i}_len'))
                    block_contents.append(_generate_arraydecl(f'arg{i}',
                                                              arg.type.type,
                                                              c_ast.ID(f'arg{i}_len')))
                    block_contents.append(_generate_read(f'arg{i}', address=False))
                    
                elif type(interface) is CharWrapper:
                    func_args.append(c_ast.ID(f'arg{i}'))
                    block_contents.append(
                        _generate_decl(
                            f'arg{i}_len',
                            c_ast.TypeDecl(f'arg{i}_len', [], 
                                           c_ast.IdentifierType(['unsigned', 'short']))))
                    block_contents.append(_generate_read(f'arg{i}_len'))
                    block_contents.append(_generate_arraydecl(f'arg{i}',
                                                              arg.type.type,
                                                              c_ast.ID(f'arg{i}_len')))
                    block_contents.append(_generate_read(f'arg{i}', address=False))
                    post_block_contents.append(_generate_write(f'arg{i}_len'))
                    post_block_contents.append(_generate_write(f'arg{i}', address=False))
                elif type(interface) is StructWrapper:
                    func_args.append(c_ast.ID(f'arg{i}'))
                    block_contents.append(_generate_decl(f'arg{i}', arg.type))
                    block_contents.append(_generate_read(f'arg{i}'))
                else:
                    raise RuntimeError(f"Unknown Interface Type {type(interface)}")
                self.arg_interfaces.append(interface)
        
        function_call = c_ast.FuncCall(c_ast.ID(self.name), 
                                       c_ast.ExprList(func_args))
        
        if type(self.return_interface) is VoidWrapper:
            block_contents.append(function_call)
        else:
            ret_assign = c_ast.Decl(
                'ret', [], [], [], 
                c_ast.TypeDecl('ret', [], decl.type.type),
                function_call, []
            )
            block_contents.append(ret_assign)
            block_contents.append(_generate_write('ret'))

        block_contents.extend(post_block_contents)
        self.call_ast = c_ast.Compound(block_contents)
        
    def pack_args(self, *args):
        """Create a bytes of the provided arguments

        """
        if len(args) != len(self.arg_interfaces):
            raise RuntimeError(f"Wrong number of arguments: expected{len(self.arg_interfaces)} got {len(args)}")
        return b''.join(
            [f.param_encode(a) for f, a in itertools.zip_longest(
                self.arg_interfaces, args
            )]
        )
    
    def receive_response(self, stream, *args):
        """Reads the response stream, updates arguments and
        returns the value of the function call if applicable

        """
        return_value = self.return_interface.return_decode(stream)
        if len(args) != len(self.arg_interfaces):
            raise RuntimeError(f"Wrong number of arguments: expected{len(self.arg_interfaces)} got {len(args)}")
        [f.param_decode(a, stream) for f, a in itertools.zip_longest(
             self.arg_interfaces, args
        )]
        return return_value


class ParsedEnum:
    """Holds the values of an enum from the C source

    """
    def __init__(self):
        self.name = None
        self.items = {}


class FuncDefVisitor(pycparser.c_ast.NodeVisitor):
    """Primary visitor that parses out function definitions,
    typedes and enumerations from a syntax tree

    """
    def __init__(self):
        self.functions = {}
        self.typedefs = {}
        self.enums = []
        self.defined = []
        
    def visit_Typedef(self, node):
        self.typedefs[node.name] = node.type
    
    def visit_FuncDef(self, node):
        self.defined.append(node.decl.name)
    
    def visit_FuncDecl(self, node):
        name = node.type.declname
        try:
            self.functions[name] = FuncAdapter(node, self.typedefs)
        except RuntimeError as e:
            print(f"Could not create interface for funcion {name}: {e}")
    
    def visit_Enum(self, node):
        enum = ParsedEnum()
        if node.name:
            enum.name = node.name
        cur_index = 0
        for entry in node.values.enumerators:
            if entry.value:
                cur_index = int(entry.value.value, 0)
            enum.items[entry.name] = cur_index
            cur_index += 1
        self.enums.append(enum)
            
def _build_case(functions):
    """ Builds the switch statement that will form the foundation
    of the RPC handler

    """
    cases = []
    for i, func in enumerate(functions.values()):
        case = c_ast.Case(
            c_ast.Constant('int', f'{i}'),
            [
                func.call_ast,
                c_ast.Break()
            ])
        cases.append(case)
    return c_ast.Switch(
        c_ast.ID('command'),
        c_ast.Compound(cases)
    )

def _build_handle_function(functions):
    """ Wraps the switch statement in a function definition

    """
    case_statement = _build_case(functions)
    handle_decl = c_ast.FuncDecl(None, 
        c_ast.TypeDecl('_handle_receive', [],
            c_ast.IdentifierType(['void'])),
    )
    command_decl = c_ast.Decl('command', [], [], [],
                             c_ast.TypeDecl('command', [], c_ast.IdentifierType(['int'])),
                              [], [])
    command_read = _generate_read('command')
    body = c_ast.Compound([command_decl, command_read, case_statement])
    return c_ast.FuncDef(handle_decl, [], body)

def _build_main(program_text, functions):
    sections = []
    sections.append(R"""
    #include <unistd.h>
    """)
    
    sections.append(program_text)
    sections.append(_generator.visit(_build_handle_function(functions)))
    
    sections.append(R"""
    int main() {
        while (1) {
            _handle_receive();
        }
    }
    """)
    
    return "\n".join(sections)

def _function_wrapper(stream, index, adapter, return_type, *args):
    """ Calls a function in the microblaze, designed to be used
    with functools.partial to build a new thing

    """
    arg_string = struct.pack('l', index)
    arg_string += adapter.pack_args(*args)
    stream.write(arg_string)
    response = adapter.receive_response(stream, *args)
    if return_type:
        return return_type(response)
    else:
        return response

def _create_typedef_classes(typedefs):
    """ Creates an anonymous class for each typedef in the C function

    """
    classes = {}
    for k, v in typedefs.items():
        class Wrapper:
            """Wrapper class for a C typedef

            The attributes are dynamically from the C definition using
            the functions name `type_`. If a function named this way
            takes `type` as the parameter it is added as a member function
            otherwise it is added as a static method.

            """
            def __init__(self, val):
                self.val = val

            def __index__(self):
                return self.val

            def __int__(self):
                return self.val

            def _call_func(self, function, *args):
                return function(self.val, *args)
        Wrapper.__name__ = k
        classes[k] = Wrapper
    return classes

class MicroblazeRPC:
    """ Provides a python interface to the Microblaze based on an RPC
    mechanism.

    The attributes of the class are generated dynamically from the
    typedefs, enumerations and functions given in the provided source.

    Functions are added as methods, the values in enumerations are
    added as constants to the class and types are added as classes.

    """
    def __init__(self, iop, program_text):
        """ Create a new RPC instance

        Parameters
        ----------
        iop          : MicroblazeHierarchy or mb_info
            Microblaze instance to run the RPC server on
        program_text : str
            Source of the program to extract functions from

        """
        preprocessed = preprocess(program_text, mb_info=iop);
        ast = _parser.parse(preprocessed, filename='<stdin>')
        visitor = FuncDefVisitor()
        visitor.visit(ast)
        main_text = _build_main(program_text, visitor.functions)
        typedef_classes = _create_typedef_classes(visitor.typedefs)
        self._mb = MicroblazeProgram(iop, main_text)
        self._build_functions(visitor.functions, typedef_classes)
        self._build_constants(visitor.enums)
        self._populate_typedefs(typedef_classes, visitor.functions)
        self.visitor = visitor
        
    def _build_constants(self, enums):
        for enum in enums:
            for name, value in enum.items.items():
                setattr(self, name, value)
                
    def _build_functions(self, functions, typedef_classes):
        index = 0
        for k, v in functions.items():
            return_type = None
            if v.return_interface.typedefname:
                return_type = typedef_classes[v.return_interface.typedefname]
            setattr(self, k, 
                    functools.partial(
                        _function_wrapper, self._mb.stream, index, v, return_type)
                    )
            index += 1
    
    def _populate_typedefs(self, typedef_classes, functions):
        for name, cls in typedef_classes.items():
            for fname, func in functions.items():
                if fname.startswith(f'{name}_'):
                    subname = fname[len(name)+1:]
                    if len(func.arg_interfaces) > 0 and func.arg_interfaces[0].typedefname == name:
                        setattr(cls, subname,
                                functools.partialmethod(cls._call_func, getattr(self, fname)))
                    else:
                        setattr(cls, subname, getattr(self, fname))
    def reset(self):
        """Reset and free the microblaze for use by other programs

        """
        self._mb.reset()


class MbioRPC(MicroblazeRPC):
    """Provides access to the basic `mbio` interface through python

    """
    def __init__(self, iop, modules=[]):
        """Create an instance of the RPC

        Parameters
        ----------
        iop     : MicroblazeHierary or mb_info dict
            Microblaze instance to run the RPC server on
        modules : [str]
            Names of the modules to add to the base API

        """
        header_text = ["#include <mbio.h>"]
        for module in modules:
            header_text.append(f'#include <{module}.h>')
        super().__init__(iop, "\n".join(header_text))


class IopRPC(MicroblazeRPC):
    """Provides access to the basic `mbio` and `iop_switch`
    interfaces through python

    """
    def __init__(self, iop, modules=[]):
        """Create an instance of the RPC

        Parameters
        ----------
        iop     : MicroblazeHierary or mb_info dict
            Microblaze instance to run the RPC server on
        modules : [str]
            Names of the modules to add to the base API

        """
        header_text = ["#include <mbio.h>", "#include <iop.h>"]
        for module in modules:
            header_text.append(f'#include <{module}.h>')
        super().__init__(iop, "\n".join(header_text))
