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
        float(string)
        if float(string).is_integer():
            return True
        else:
            return False
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
    
    def __neg__(self):
        return SubtractNode(Constant(0),self)
        
    
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
    
    #---------------------Differentiation function-------------------------------------
    def diff(self, var):
        if isint(self) or isnumber(self):
            return Constant(0)
        elif self != var and type(self) == Variable:
            return Constant(0)
        elif self == var:
             return Constant(1)
        # Sum rule
        if self.op_symbol == '+':
            return self.lhs.diff(var) + self.rhs.diff(var)
        # Difference rule
        if self.op_symbol == '-':
            return self.lhs.diff(var) - self.rhs.diff(var)
        # Product rule
        if self.op_symbol == '*':
            return (self.rhs * self.lhs.diff(var) ) + (self.rhs.diff(var) * self.lhs)
        # Quotient rule
        if self.op_symbol == '/':
            return ((self.rhs * self.lhs.diff(var)) - (self.rhs.diff(var) * self.lhs)) / (self.rhs * self.rhs)
        # Power rule
        if self.op_symbol == '**':
            return (self.rhs * (self.lhs**(self.rhs - Constant(1))))  * self.lhs.diff(var)
    #---------------------END Differentiation-------------------------------------

    #---------------------Evaluate function-------------------------------------
    # Evaluates the expression, values of variables are loaded through dictionary
    # Uses inorder read of tree
    def evaluate(self,Dic={}):
        Prec={'+':1,'-':1,'*':2,'/':2,'**':3,}
        oplist = ['+','-','*','/','**']
        Right=''
        Left=''
        # 1: Check is self is a number or variable
        if isint(self):
            return int(self)
        elif isnumber(self):
            return float(self)
        elif isinstance(self,Variable):
            if self.char in Dic:
                return Dic[self.char]
            else:
                return self.char
        # 2: Self is tree
        else:
            #2a: Both children can be evaluated to numbers
            if isnumber(self.lhs.evaluate(Dic)) and isnumber(self.rhs.evaluate(Dic)):
                if self.op_symbol=='+':
                    return self.lhs.evaluate(Dic)+self.rhs.evaluate(Dic)
                elif self.op_symbol=='-':
                    return self.lhs.evaluate(Dic)-self.rhs.evaluate(Dic)
                elif self.op_symbol=='*':
                    return self.lhs.evaluate(Dic)*self.rhs.evaluate(Dic)
                elif self.op_symbol=='/':
                    return self.lhs.evaluate(Dic)/self.rhs.evaluate(Dic)
                elif self.op_symbol=='**':
                    return self.lhs.evaluate(Dic)**self.rhs.evaluate(Dic)
            #2b: At least one child evaluates to a string
            if isinstance(self.lhs.evaluate(Dic),str): # left side is a string
                if isinstance(self.lhs,Variable): # left side is a variable not in dictionary
                    Left=self.lhs.char
                else: # left side is an expression with a variable not in dictionary
                    if Prec[self.lhs.op_symbol]<Prec[self.op_symbol]:
                        Left='('+self.lhs.evaluate(Dic)+')'
                    else:
                        Left=self.lhs.evaluate(Dic)
            else: # left side is just a number
                Left=str(self.lhs.evaluate(Dic))
            if isinstance(self.rhs.evaluate(Dic),str): # right side is a string
                if isinstance(self.rhs,Variable): # right side is a variable not in dictionary
                    Right=self.rhs.char
                else: # right side is an expression with a variable not in dictionary
                    if Prec[self.rhs.op_symbol]<Prec[self.op_symbol]:
                        Right='('+self.rhs.evaluate(Dic)+')'
                    elif Prec[self.rhs.op_symbol]==Prec[self.op_symbol]:
                        if self.rhs.op_symbol in ['-','/']:
                            Right='('+self.rhs.evaluate(Dic)+')'
                        else:
                            Right=self.rhs.evaluate(Dic)
                    else:
                        Right=self.rhs.evaluate(Dic)
            else: # right side is just a number
                Right=str(self.rhs.evaluate(Dic))
            return Left+' '+self.op_symbol+' '+Right # Returns a string
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
    
    def __neg__(self):
        return Constant(-self.value)
        
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
    
    def __neg__(self):
        return Variable('-'+self.char)
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
    
    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other): # equivalent to root node being the same
            if self.op_symbol in ['+','*']: 
                if isinstance(self.lhs,BinaryNode) and isinstance(self.rhs,BinaryNode) and\
                   isinstance(other.lhs,BinaryNode) and isinstance(other.rhs,BinaryNode) and\
                   self.op_symbol==self.lhs.op_symbol and\
                   self.op_symbol==self.rhs.op_symbol and\
                   self.op_symbol==other.lhs.op_symbol and\
                   self.op_symbol==other.rhs.op_symbol: # This is the case: (a+b)+(c+d)=(k+l)+(m+n) (LR-LR)
                    return (self.lhs == other.lhs and self.rhs == other.rhs) or\
                           (self.lhs == other.rhs and self.rhs == other.lhs) or\
                           (self.lhs == type(self)(other.lhs.lhs,other.rhs.lhs) and\
                            self.rhs == type(self)(other.lhs.rhs,other.rhs.rhs)) or\
                           (self.lhs == type(self)(other.lhs.rhs,other.rhs.rhs) and\
                            self.rhs == type(self)(other.lhs.lhs,other.rhs.lhs)) or\
                           (self.lhs == type(self)(other.lhs.lhs,other.rhs.rhs) and\
                            self.rhs == type(self)(other.lhs.rhs,other.rhs.lhs)) or\
                           (self.lhs == type(self)(other.lhs.rhs,other.rhs.lhs) and\
                            self.rhs == type(self)(other.lhs.lhs,other.rhs.rhs))
                elif isinstance(self.lhs,BinaryNode) and isinstance(other.lhs,BinaryNode) and\
                     self.op_symbol==self.lhs.op_symbol and\
                     self.op_symbol==other.lhs.op_symbol: # This is the case: (a+b)+c=(x+y)+z (L-L)
                    return (self.lhs == other.lhs and self.rhs == other.rhs) or\
                           (self.lhs == type(self)(other.lhs.lhs,other.rhs) and\
                           self.rhs == other.lhs.rhs) or\
                           (self.lhs == type(self)(other.lhs.rhs.other.rhs) and\
                           self.rhs == other.lhs.lhs)
                elif isinstance(self.rhs,BinaryNode) and isinstance(other.rhs,BinaryNode) and\
                     self.op_symbol==self.rhs.op_symbol and\
                     self.op_symbol==other.rhs.op_symbol: # This is the case: a+(b+c)=x+(y+z) (R-R)
                    return (self.lhs == other.lhs and self.rhs == other.rhs) or\
                           (self.rhs == type(self)(other.rhs.lhs,other.lhs) and\
                           self.lhs == other.rhs.rhs) or\
                           (self.rhs == type(self)(other.rhs.rhs,other.lhs) and\
                           self.lhs == other.rhs.lhs)
                elif isinstance(self.lhs,BinaryNode) and isinstance(other.rhs,BinaryNode) and\
                     self.op_symbol==self.lhs.op_symbol and\
                     self.op_symbol==other.rhs.op_symbol: # This is the case: (a+b)+c=x+(y+z) (L-R)
                    return (self.lhs == other.rhs and self.rhs == other.lhs) or\
                           (self.lhs == type(self)(other.rhs.lhs,other.lhs) and\
                           self.rhs == other.rhs.rhs) or\
                           (self.lhs == type(self)(other.rhs.rhs,other.lhs) and\
                           self.rhs == other.rhs.lhs)
                elif isinstance(self.rhs,BinaryNode) and isinstance(other.lhs,BinaryNode) and\
                     self.op_symbol==self.rhs.op_symbol and\
                     self.op_symbol==other.lhs.op_symbol: # This is the case: a+(b+c)=(x+y)+z (R-L)
                    return (self.lhs == other.rhs and self.rhs == other.lhs) or\
                           (self.rhs == type(self)(other.lhs.lhs,other.rhs) and\
                           self.lhs == other.lhs.rhs) or\
                           (self.rhs == type(self)(other.lhs.rhs,other.rhs) and\
                           self.lhs == other.lhs.lhs)
                else: # This is the normal commutative case: a+b=z+y
                    return (self.lhs == other.lhs and self.rhs == other.rhs) or\
                           (self.lhs == other.rhs and self.rhs == other.lhs)
            else:
                return self.lhs == other.lhs and self.rhs == other.rhs 
        else:
            return False
            
def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        Prec={'+':1,'-':1,'*':2,'/':2,'**':3,}
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
                    # Brackets
        # Simplifications:
            # a + -b -> a-b (b is positive)
            # a - -b -> a+b (b is positive, we do not change operator '-')
            # a + -|...| -> a - |...| (|...| is an expression 0-|...|)
            # a - -|...| -> a + |...| (|...| is an expression 0-|...|)
            # 0 + a, a + 0 -> a
            # 0 * a, a * 0 -> 0
            # 1 * a, a * 1 -> a
            # a**1 -> a
            # 1**a -> 1
            # a**0 -> 1
            # 0**a -> 0
            # we assume, for now, that things like: a/0 and 0**0 do not exist
        # Difference with previous algorithm: previous algorithm added brackets around
        # every parent and its children, this algorithm checks whether to add brackets
        # around children only (so that the root has no brackets).
        if self.lhs==Constant(0) and self.rhs==Constant(0): # We ignore 0**0 and 0/0
            return str(0)
        if self.lhs==Constant(0):
            if self.op_symbol=='+': # 0+a=a
                return str(self.rhs)
            elif self.op_symbol in ['*','/','**']: # 0*a=0/a=0**a=0
                return str(0)
            elif self.op_symbol=='-': # 0-a=-a, 0-(...)=-(...)
                if not isinstance(self.rhs,BinaryNode): 
                    return str(-self.rhs)
                else: # Expression
                    return '-'+'('+str(self.rhs)+')'
        if self.rhs==Constant(0): # We ignore a/0
            if self.op_symbol in ['+','-']: # a+0=a-0=a
                return str(self.lhs)
            elif self.op_symbol=='*': # a*0=0
                return str(0)
            elif self.op_symbol=='**': # a**0=1
                return str(1)
        if self.lhs==Constant(1):
            if self.op_symbol=='*': # 1*a=a
                return str(self.rhs)
            elif self.op_symbol=='**': # 1**a=1
                return str(1)
        if self.rhs==Constant(1):
            if self.op_symbol in ['*','**']: # a*1=a**1=a
                return str(self.lhs)
        if isinstance(self.rhs,Constant) and self.rhs.value<0:
            if self.op_symbol=='+': # a+-b=a-b
                return str(SubtractNode(self.lhs,-self.rhs)) 
            if self.op_symbol=='-': # a--b=a+b
                return str(AddNode(self.lhs,-self.rhs))
        if isinstance(self.rhs,SubtractNode) and self.rhs.lhs==Constant(0):
            if self.op_symbol=='+': # a+-(b+c)=a-(b+c)
                return str(SubtractNode(self.lhs,self.rhs.rhs))
            if self.op_symbol=='-': # a--(b+c)=a+(b+c)
                return str(AddNode(self.lhs,self.rhs.rhs))
        # After dealing with 0's 1's and negations, we deal with brackets:
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
                    # Keep brackets in this specific case
                    Right="(%s)" % (rstring)
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


