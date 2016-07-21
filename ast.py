"""Classes for the nodes that form our abstract syntax tree (AST). Each node
corresponds to a rule in the C grammar.

"""

from code_gen import ValueInfo
from tokens import Token
import token_kinds

class Node:
    """A general class for representing a single node in the AST. Inherit all
    AST nodes from this class. Every AST node also has a make_code function that
    accepts a code_store to which the generated code should be saved. Nodes 
    representing expressions also return a ValueInfo object describing the
    generated value.

    symbol (str) - Each node must set the value of this class attribute to the
    non-terminal symbol the corresponding rule produces. This helps enforce tree
    structure so bugs in the parser do not accidentally slip into output code.

    """
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def assert_symbol(self, node, symbol_name):
        """Useful for enforcing tree structure. Raises an exception if the
        node represents a rule that does not produce the expected symbol. 

        """
        if node.symbol != symbol_name:
            raise ValueError("malformed tree: expected symbol ", symbol_name,
                             ", got ", node.symbol)

    def assert_kind(self, token, kind):
        if token.kind != kind:
            raise ValueError("malformed tree: expected token kind ", kind,
                             ", got ", token.kind)

class MainNode(Node):
    """ General rule for the main function. Will be removed once function
    definition is supported. Ex: int main() { return `return_value`; }
    
    statements (List[statement]) - a list of the statement in main function

    """
    symbol = "main_function"
    
    def __init__(self, statements):
        super().__init__()

        for statement in statements: self.assert_symbol(statement, "statement")
        self.statements = statements
        
    def make_code(self, code_store):
        code_store.add_label("main")
        code_store.add_command(("push", "rbp"))
        code_store.add_command(("mov", "rbp", "rsp"))
        for statement in self.statements:
            statement.make_code(code_store)
        # We return 0 at the end, in case the code did not return
        code_store.add_command(("mov", "rax", "0"))
        code_store.add_command(("pop", "rbp"))
        code_store.add_command(("ret", ))

class ReturnNode(Node):
    """ Return statement

    return_value (expression) - value to return

    """
    symbol = "statement"

    def __init__(self, return_value):
        super().__init__()

        self.assert_symbol(return_value, "expression")
        self.return_value = return_value

    def make_code(self, code_store):
        value_info = self.return_value.make_code(code_store)
        if value_info.storage_type == ValueInfo.LITERAL:
            code_store.add_command(("mov", "rax", value_info.storage_info))
            code_store.add_command(("pop", "rbp"))
            code_store.add_command(("ret",))
        else:
            raise NotImplementedError
        

class NumberNode(Node):
    """ Expression that is just a single number. 

    number (Token(Number)) - number this expression represents

    """
    symbol = "expression"
    
    def __init__(self, number):
        super().__init__()

        self.assert_kind(number, token_kinds.number)
        self.number = number

    def make_code(self, code_store):
        return ValueInfo(ValueInfo.LITERAL, self.number.content)

class BinaryOperatorNode(Node):
    """ Expression that is a sum/difference/xor/etc of two expressions. 
    
    left_expr (expression) - expression on left side
    operator (Token) - the token representing this operator
    right_expr (expression) - expression on the right side

    """
    symbol = "expression"

    def __init__(self, left_expr, operator, right_expr):
        super().__init__()

        self.assert_symbol(left_expr, "expression")
        self.left_expr = left_expr
        
        assert isinstance(operator, Token)
        self.operator = operator
        
        self.assert_symbol(right_expr, "expression")
        self.right_expr = right_expr

    def add(self, left_value, right_value, code_store):
        if (left_value.storage_type == ValueInfo.LITERAL and
            right_value.storage_type == ValueInfo.LITERAL):
            return ValueInfo(ValueInfo.LITERAL,
                             str(int(left_value.storage_info) +
                                 int(right_value.storage_info)))
        else:
            raise NotImplementedError

    def multiply(self, left_value, right_value, code_store):
        if (left_value.storage_type == ValueInfo.LITERAL and
            right_value.storage_type == ValueInfo.LITERAL):
            return ValueInfo(ValueInfo.LITERAL,
                             str(int(left_value.storage_info) *
                                 int(right_value.storage_info)))
        else:
            return NotImplementedError
        
    def make_code(self, code_store):
        left_value = self.left_expr.make_code(code_store)
        right_value = self.right_expr.make_code(code_store)
        
        if self.operator == Token(token_kinds.plus):
            return self.add(left_value, right_value, code_store)
        elif self.operator == Token(token_kinds.star):
            return self.multiply(left_value, right_value, code_store)
        else:
            raise NotImplementedError
