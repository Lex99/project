import math

# split a string into mathematical tokens
# returns a list of numbers, operators, parantheses and commas
# output will not contain spaces
def tokenize(string):
    splitchars = list("+-*/(),")
    
    # surrounds any splitchar by spaces, numbers are left alone:
    tokenstring = []
    for c in string:
        if c in splitchars:
            tokenstring.append(' %s ' % c)
        else:
            tokenstring.append(c)
    tokenstring = ''.join(tokenstring)
    #split on spaces - this gives us our tokens
    tokens = tokenstring.split()
    
    #checks for double *'s and converts them to **'s:
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    return ans
    
# check if a string represents a numeric value
def isnumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

# check if a string represents an integer value        
def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

class Expression():
    """
    A mathematical expression, represented as an expression tree
    """
    
    """
    Any concrete subclass of Expression should have these methods:
    - __str__(): return a string representation of the Expression.
    - __eq__(other): tree-equality, check if other represents the same expression tree.
    """

    """
    TODO: when adding new methods that should be supported by all subclasses,
    add them to this list
    """
    
    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions,
    # and obtain another expression
    def __add__(self, other):
        return AddNode(self, other)

    def __sub__(self, other):
        return SubtractNode(self, other)

    def __mul__(self, other):
        return MultiplyNode(self, other)

    def __truediv__(self, other):
        return DivideNode(self, other)

    def __pow__(self, other):
        return PowerNode(self, other)
        
    
    #------------------basic Shunting-yard algorithm------------------------------
    def fromString(string):
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
        # output of the algorithm: a list representing the formula in RPN
        # this will contain Constant's and operators
        output = []
        
        # list of operators
        oplist = ['+','-','*','/','**']

        # precedence of operators ('(' has value 0, so that the stack
        # is treated as 'empty' if '(' is on top of the stack)
        Prec={'(':0,'+':1,'-':1,'*':2,'/':2,'**':3,}
        
        for token in tokens:
            
            # numbers go directly to the output
            if isnumber(token):
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
                    
            # operators will be compared (+,- < *,/ < **)
            elif token in oplist:
                while True:
                    # we push operator if stack is empty,
                    # or if operator has higher precedence than
                    # top operator in stack (we break from while-loop):
                    if stack==[] or Prec[stack[-1]]<Prec[token]:
                        break
                    # if Prec(stack[-1])>=Prec(token) we pop stack to
                    # output and go back to while-loop
                    output.append(stack.pop())
                # the while-loop is broken and we finally push operator
                stack.append(token)

            # left parenthesis     
            elif token == '(':
                stack.append(token)
                
            # right parenthesis
            elif token == ')':
                # right parenthesis: pop everything until left parenthesis to the output
                while not stack[-1] == '(':
                    output.append(stack.pop())
                # remove left parenthesis '('
                stack.pop()
                
            # We might find an unknown token:
            else:
                raise ValueError('Unknown token: %s' % token)
            
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        
        # convert RPN to an actual expression tree
        for t in output:
            if t in oplist:
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            else:
                # a constant, push it to the stack
                stack.append(t)
        # the resulting expression tree is what's left on the stack
        return stack[0]
    #-------------------------END fromString----------------------------------------


    #---------------------Evaluate function-------------------------------------
    # Evaluates the expression, values of variables are loaded through dictionary
    # Uses inorder read of tree
    def evaluate(self,Dic={}):
        if isint(self):
            return int(self)
        elif isnumber(self):
            return float(self)
        elif isinstance(self,Variable):
            return Dic[self.char]
        else: # for now we assume that this mean self is a tree
            if self.op_symbol=='+':
                return self.lhs.evaluate(Dic) + self.rhs.evaluate(Dic)
            elif self.op_symbol=='-':
                return self.lhs.evaluate(Dic) - self.rhs.evaluate(Dic)
            elif self.op_symbol=='*':
                return self.lhs.evaluate(Dic) * self.rhs.evaluate(Dic)
            elif self.op_symbol=='/':
                return self.lhs.evaluate(Dic) / self.rhs.evaluate(Dic)
            elif self.op_symbol=='**':
                return self.lhs.evaluate(Dic) ** self.rhs.evaluate(Dic)
    #--------------------------END evaluate---------------------------------
    
class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)

class Variable(Expression):
    """Represents a variable"""
    def __init__(self, character):
        self.char=str(character)
        
    def __str__(self):
        return self.char
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
    
    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        Prec={'+':1,'-':1,'*':2,'/':2,'**':3,}
        # To invert operators, which allows us to remove more brackets:
        Invert={'+':'-','-':'+','*':'/','/':'*'} 
        oplist = ['+','-','*','/','**']
        
        # We don't need parenthesis in these cases (node is always internal):
        # Node has no parent (is root)
        # Parent has lower precedence
        # If parent has same precedence:
            # If parent is "positive" operator (+,*):
                # No brackets
            # If parent is "negative" operator (-,/):
                # If node is left node:
                    # No brackets
                # If node is right node:
                    # Invert node operator (+,-,*,/ to resp -,+,/,*)
                    # No brackets

        # Difference with previous algorithm: previous algorithm added brackets around
        # every parent and its children, this algorithm checks whether to add brackets
        # around children only (so that the root has not brackets).
        if isinstance(self.lhs,BinaryNode): # left child is operator
            if Prec[self.lhs.op_symbol]<Prec[self.op_symbol]:
                Left="(%s)" % (lstring)
            else:
                Left="%s" % (lstring)
        else: # left child is not an operator
            Left="%s" % (lstring)
        if isinstance(self.rhs,BinaryNode): # right child is operator
            if Prec[self.rhs.op_symbol]<Prec[self.op_symbol]:
                Right="(%s)" % (rstring)
            elif Prec[self.rhs.op_symbol]==Prec[self.op_symbol]:
                if self.rhs.op_symbol in ['-','/']:
                    # Changes tree (operator), might not be a good idea
                    # Alternative: keep brackets in this specific case
                    self.rhs.op_symbol = Invert[self.rhs.op_symbol]
                    rstring = str(self.rhs)
                    Right="%s" % (rstring)
                else:
                    Right="%s" % (rstring)
            else:
                Right="%s" % (rstring)
        else: # right child is not an operator
            Right="%s" % (rstring)
        return Left+' '+self.op_symbol+' '+Right # all seperate strings
        
class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

class SubtractNode(BinaryNode):
    """Represents the subtraction operator"""
    def __init__(self, lhs, rhs):
        super(SubtractNode, self).__init__(lhs, rhs, '-')

class MultiplyNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MultiplyNode, self).__init__(lhs, rhs, '*')

class DivideNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivideNode, self).__init__(lhs, rhs, '/')

class PowerNode(BinaryNode):
    """Represents the exponentiation operator"""
    def __init__(self, lhs, rhs):
        super(PowerNode, self).__init__(lhs, rhs, '**')
        
# TODO: add more subclasses of BinaryNode to represent operators, variables, functions, etc.

expression='56* (3,3**9)'
print(tokenize(expression))
a=Constant(2)
b=Constant(3)
c=Variable('x')
d=Variable('y')
Exp=(a+c)*d-(b-d)**b
Exp2=((a*d)**b)-(b-c)
print(Exp)
print(Exp2)
print(Exp.evaluate({'x':-2,'y':1}))
print(Exp2.evaluate({'x':-1,'y':0}))


