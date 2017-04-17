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
    except Exception:
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
    
# checks if numerical constant is positive, or non-numerical constant/value is negated (begins with '-')
def ispos(string): 
    try:
        float(string)
        return float(string)>=0
    except Exception:
        return not str(string)[0]=='-'
    # TODO: check if this also works with expression trees

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
    #---END fromString--------------------------------------------------------------------------------
    
    #---Differentiation function----------------------------------------------------------------------
    def diff(self,var): 
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
    #---END Differentiation--------------------------------------------------------------------------

    #---Evaluate function----------------------------------------------------------------------------
    # Evaluates the expression, values of variables are loaded through dictionary
    # Returns a new tree, where numerical constants are united where possible (e.g. 1+2->3)
    def evaluate(self,Dic={}):
        # 1: Check is self is a number or variable
        # This is handled by the evaluate function in the subclasses   
        # 2: Self is tree
        #2a: Both children can be evaluated to numerical constants: we unite constants to new constant
        if isinstance(self.lhs.evaluate(Dic),Constant) and isinstance(self.rhs.evaluate(Dic),Constant):
            if isnumber(self.lhs.evaluate(Dic).value) and isnumber(self.rhs.evaluate(Dic).value):
                if self.op_symbol=='+':
                    return Constant(self.lhs.evaluate(Dic).value+self.rhs.evaluate(Dic).value)
                elif self.op_symbol=='-':
                    return Constant(self.lhs.evaluate(Dic).value-self.rhs.evaluate(Dic).value)
                elif self.op_symbol=='*':
                    return Constant(self.lhs.evaluate(Dic).value*self.rhs.evaluate(Dic).value)
                elif self.op_symbol=='/':
                    return Constant(self.lhs.evaluate(Dic).value/self.rhs.evaluate(Dic).value)
                elif self.op_symbol=='**':
                    return Constant(self.lhs.evaluate(Dic).value**self.rhs.evaluate(Dic).value)
        #2b: At least one child evaluates to tree or non-numerical constant: keep tree structure
        return type(self)(self.lhs.evaluate(Dic),self.rhs.evaluate(Dic))
    #---END evaluate-----------------------------------------------------------------------------------
    
#---Subclass: Constant-----------------------------------------------------    
class Constant(Expression):
    # Represents a constant value (numerical or non-numerical)
    def __init__(self, value): 
        if isnumber(value):
            if isint(value):
                self.value = int(float(value))
            else:
                self.value = float(value)
        else: # This is the case the constant is not a numerical value
            self.value = str(value)
        
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)

    # Negation function (adds/removes '-' from string if string)
    def __neg__(self):
        if isnumber(self.value):
            return Constant(-self.value)
        else: 
            if self.value[0] == '-':
                return Variable(self.value[1:])
            else:
                return Variable('-'+self.value)
        
    # Conversion to numerical values (if possible)
    def __int__(self):
        return int(float(self.value)) # Returns error if not numerical value
        #TODO: What happens when trying int(string), if it gives Value/TypeError: Great!
        
    def __float__(self): # Returns error if not numerical value
        return float(self.value)
    
    # Derivative
    def diff(self,var):
        return Constant(0)
    
    # Evaluate
    def evaluate(self,Dic={}):
        return self
#---END Subclass: Constant---------------------------------------------

#---Subclass: Variable-----------------------------------------------------
class Variable(Expression):
    # Represents a variable, should NOT contain the character '-'
    def __init__(self, character):
        self.char=str(character)
        
    def __str__(self):
        return self.char

    def __eq__(self,other):
        if isinstance(other, Variable):
            return self.char == other.char
        else:
            return False

    # Overload: Negation
    def __neg__(self):
        if self.char[0] == '-':
            return Variable(self.char[1:])
        else:
            return Variable('-'+self.char)
        
    # Derivative
    def diff(self,var):
        if self.char == var:
            return Constant(1)
        elif (-self).char == var:
            return Constant(-1)
        else:
            return Constant(0)

    # Evaluate
    def evaluate(self,Dic={}):
        if self.char in Dic:
            return Constant(Dic[self.char])
        elif (-self).char in Dic:
            return Constant(-Dic[self.char])
        else:
            return self
#---END Subclass: Variable---------------------------------------------

#---Subclass: Function--------------------------------------------------------
class Function(Expression):
    # Represents a function of 1 variable   
    def __init__(self, funcharacter, varcharacter):
        self.funchar=str(funcharacter)
        self.varchar=str(varcharacter)
        
    def __str__(self):
        return self.funchar+'('+self.varchar+')'
#---END: Function-------------------------------------------------

#---Subsubclass: Standard-----------------------------------------------
class Standard(Function):
    # Represents a standard function of 1 variable (sin,cos,log)
    def diff(self,variable):
        if self.varchar == variable:
            if self.funchar=='sin':
                return Standard('cos',self.varchar)
            elif self.funchar=='cos':
                return -Standard('sin',self.varchar)
            elif self.funchar=='log':
                return Constant(1)/Variable(self.varchar)
            else:
                return None
        else:
            return Constant(0)

    def evaluate(self,Dic={}):
        if self.varchar in Dic:
            if self.funchar=='sin':
                return Constant(math.sin(Dic[self.varchar]))
            elif self.funchar=='cos':
                return Constant(math.cos(Dic[self.varchar]))
            elif self.funchar=='log':
                return Constant(math.log(Dic[self.varchar]))
        else:
            return self
#---END: Standard-------------------------------------------------
 
#---Subclass: BinaryNode-----------------------------------------------------
class BinaryNode(Expression):
    # Represents a binary tree, where each internal node represents an operation
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
       
    # Checks if two trees are equal
    # It should take into account commutativity and assiociativity of operators '+' and '*'
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
        Left=''
        Right=''
        Prec={'+':1,'-':1,'*':2,'/':2,'**':3,}
        oplist = ['+','-','*','/','**']
        # We print the expression in usual notation
        # Note: we (first) simplify in the following cases:
            # a+0,0+a,a-0,a*1,1*a,a/1,a**1 to a
            # 0-a,a*-1,-1*a,a/-1 to -a
                # Note: -1*a is first simplified to 0-a
            # a**0,a/a to 1
                # Note: this means also 0**0 is simplified to 1
                # TODO: fix 0**0 -> 1
            # a*0,0*a,0/a to 0
                # Note: this means also 0/0 is simplified to 0
                # TODO: fix 0/0 -> 0
        # Note: algorithm for adding brackets to a child
            # If child is left child
                # If child is not an expression
                    # No brackets
                # If child is expression
                    # If operator of child has lower precedence (than operator of parent)
                        # Brackets
                    # If operator of child has higher or equal precedence
                        # No brackets
            # If child is right child
                # If child is not an expression
                    # If operator (of parent) is '+' or '-'
                        # Brackets
                    # Else
                        # No brackets
                # If child is an expression
                    # If operator (of parent) is '-'
                        # If operator (of child) is '+'
                            # If a child is 0
                                # No brackets
                            # Else
                                # Brackets
                        # If operator (of child) is '-'
                            # If right child is 0
                                # No brackets
                            # If left child is 0
                                # If right child is not a expression and "positive"
                                    # No brackets
                                # Else
                                    # Brackets
                    # If operator (of parent) is '/'
                        # If operator (of child) is '*'
                            # Brackets
                        # If operator (of child) has lower precedence
                            # Brackets
                        # Else
                            # No brackets
                    # Else
                        # If operator (of child) has lower precendence
                            # No Brackets
                        # If operator (of child) has higher of equal precedence
        # Note: for now we do not simplify any further (i.e. 1+2->3), but
        # if we evaluate the expression without dictionary it will simplify further
        if isint(str(self.lhs)) and isint(str(self.rhs)):
            if int(float(str(self.lhs)))==0 and int(float(str(self.lhs)))==0:
                return str(0)
        if isint(str(self.lhs)):
            if int(float(str(self.lhs)))==0:
                if self.op_symbol=='+': # 0+a=a
                    return str(self.rhs)
                elif self.op_symbol in ['*','/','**']: # 0*a=0/a=0**a=0
                    return str(0)
                elif self.op_symbol=='-': # 0-a=-a, 0-(...)=-(...)
                    if not isinstance(self.rhs,BinaryNode): 
                        return str(-self.rhs)
                    else: # Expression
                        return '-'+'('+str(self.rhs)+')'
        if isint(str(self.rhs)):
            if int(float(str(self.rhs)))==0:
                if self.op_symbol in ['+','-']: # a+0=a-0=a
                    return str(self.lhs)
                elif self.op_symbol=='*': # a*0=0
                    return str(0)
                elif self.op_symbol=='**': # a**0=1
                    return str(1)
        if isint(str(self.lhs)):
            if int(float(str(self.lhs)))==1:
                if self.op_symbol=='*': # 1*a=a
                    return str(self.rhs)
                elif self.op_symbol=='**': # 1**a=1
                    return str(1)
        if isint(str(self.rhs)):
            if int(float(str(self.rhs)))==1 and self.op_symbol in ['*','/','**']: # a*1=a/1=a**1=a
                return str(self.lhs)
        #2: Deal with -1's
        if isint(str(self.lhs)):
            if int(float(str(self.lhs)))==-1 and self.op_symbol=='*':
                return(str(-self.lhs))
        if isint(str(self.rhs)):
            if int(float(str(self.rhs)))==-1 and self.op_symbol in ['*','/']:
                return(str(-self.rhs))
        #3: Deal with brackets
        if isinstance(self.lhs,BinaryNode): # left child is operator
            if Prec[self.lhs.op_symbol]<Prec[self.op_symbol]:
                Left='('+str(self.lhs)+')'
            else:
                Left=str(self.lhs)
        else: # left child is not an operator
            Left=str(self.lhs)
        if isinstance(self.rhs,BinaryNode): # right child is operator
            if Prec[self.rhs.op_symbol]<Prec[self.op_symbol]:
                Right='('+str(self.rhs)+')'
            elif Prec[self.rhs.op_symbol]==Prec[self.op_symbol]:
                if self.op_symbol=='-':
                    # Keep brackets in this case, except in cases:
                    # a-(b+0)=a-(0+b),a-(b-0)-> a-b,a-b,a-b
                    # Note: we do keep brackets in case a-(0-b)=a-(-b) if b "positive"
                    if isint(str(self.rhs.lhs)):
                        if int(float(str(self.rhs.lhs)))==0 and not ispos(self.rhs.rhs):                       
                            Right='('+str(self.rhs)+')'
                        elif int(float(str(self.rhs.lhs)))==0:
                            Right=str(self.rhs)
                        else:
                            Right='('+str(self.rhs)+')'
                    elif isint(str(self.rhs.rhs)):
                        if int(float(str(self.rhs.lhs)))==0:
                            Right=str(self.rhs)
                        else:
                            Right='('+str(self.rhs)+')'
                    else:
                        Right='('+str(self.rhs)+')'
                elif self.op_symbol=='/':
                    # Keep brackets in this case, except in cases:
                    # a/(b*1)=a/(1*b),a/(b/1)
                    if isint(str(self.rhs.lhs)):
                        if int(float(str(self.rhs.lhs)))==1 and self.rhs.op_symbol in ['*','/']:
                            Right=str(self.rhs)
                        else:
                            Right='('+str(self.rhs)+')'
                    elif isint(str(self.rhs.rhs)):
                        if int(float(str(self.rhs.lhs)))==1 and self.rhs.op_symbol=='/':
                            Right=str(self.rhs)
                        else:
                            Right='('+str(self.rhs)+')'        
                    else:
                        Right='('+str(self.rhs)+')'
                else:
                    Right=str(self.rhs)
            else:
                Right=str(self.rhs)
        else: # right child is not an operator
            if not ispos(self.rhs) and self.op_symbol in ['+','-']:
                Right='('+str(self.rhs)+')'
            else:
                Right=str(self.rhs)
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


