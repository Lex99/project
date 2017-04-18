import math

# Splits a string into mathematical tokens
# Returns a list of numbers, operators, parenthesis and commas
# Output will not contain spaces
def tokenize(string):
    splitchars = list("+-*/(),")
    
    # Surrounds any splitchar by spaces, numbers are left alone
    tokenstring = []
    for c in string:
        if c in splitchars:
            tokenstring.append(' %s ' % c)
        else:
            tokenstring.append(c)
    tokenstring = ''.join(tokenstring)
    # Splits on spaces - this gives us our tokens
    tokens = tokenstring.split()
    
    # Checks for double *'s and converts them to **'s:
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    return ans

# Checks is a string represents a expression (by checking for operators)
def isexp(string):
    if str(string)[0]=='-':
        for i in str(string)[1:]:
            if i in ['+','-','/','*']:
                return True
            return False
    else:
        for i in str(string):
            if i in ['+','-','/','*']:
                return True
        
# Checks if a string represents an integer value        
def isint(string):
    try:
        float(string)
        if float(string).is_integer():
            return True
        else:
            return False
    except Exception:
        return False

# Checks if a string represents a numeric value
def isnumber(string):
    try:
        float(string)
        return True
    except Exception:
        return False

# Checks if numerical constant is positive, or non-numerical constant/value is negated (begins with '-')
def ispos(string): 
    try:
        float(string)
        return float(string)>=0
    except Exception:
        return not str(string)[0]=='-'

# Represents an expression tree or an constant, variable or basic function
class Expression():
    
    # Overload: arithmetics
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
        
    #---Shunting-yard algorithm-------------------------------------------------
    
    def fromString(string):
        # Splits into tokens
        tokens = tokenize(string)
        
        # Stack used by the Shunting-Yard algorithm
        stack = []
        # Output of the algorithm: a list representing the formula in RPN
        # This will contain Constant's and operators
        output = []
        
        # List of operators
        oplist = ['+','-','*','/','**']

        # Precedence of operators, '(' has value 0, so that the stack is treated as 'empty' if '(' is on top of the stack
        Prec={'(':0,'+':1,'-':1,'*':2,'/':2,'**':3,}
        
        for token in tokens:
            
            # Numbers go directly to the output
            if isnumber(token):
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
                    
            # Operators will be compared (+,- < *,/ < **)
            elif token in oplist:
                while True:
                    # Pushes operator (and break from loop) if:
                    # Stack is empty
                    # Operator has higher precedence than top operator in stack
                    if stack==[] or Prec[stack[-1]]<Prec[token]:
                        break
                    # If Prec(stack[-1])>=Prec(token) we pop stack to output and go back to while-loop
                    output.append(stack.pop())
                stack.append(token)

            # Left parenthesis is added to top of the stack    
            elif token == '(':
                stack.append(token)
                
            # Right parenthesis:
            elif token == ')':
                # Pops everything to output until left parenthesis
                while not stack[-1] == '(':
                    output.append(stack.pop())
                # Removes left parenthesis '('
                stack.pop()
                
            # We might find an unknown token:
            else:
                raise ValueError('Unknown token: %s' % token)
            
        # Pops any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        
        # Converts RPN to an actual expression tree
        for t in output:
            if t in oplist:
                # Lets eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            else:
                # a constant, push it to the stack
                stack.append(t)
                
        # The resulting expression tree is what's left on the stack
        return stack[0]
    
    #---END Shunting-yard algorithm---------------------------------------------------------------

#---END Class: Expression----------------------------------------------------------------------------

#---Subclass: Constant--------------------------------------------------------------

# Represents a constant (numerical or non-numerical value)
class Constant(Expression):

    # Constants can be numerical or non-numerical
    def __init__(self, value): 
        if isnumber(value):
            if isint(value):
                self.value = int(float(value))
            else:
                self.value = float(value)
        else:
            self.value = str(value)

    # Overload: Equality ==
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False

    # Overload: String str
    def __str__(self):
        return str(self.value)

    # Overload: Negation
    # If the constant is non-numerical we add or remove '-'
    def __neg__(self):
        
        if isnumber(self.value):
            return Constant(-self.value)
        else: 
            if self.value[0] == '-':
                return Variable(self.value[1:])
            else:
                return Variable('-'+self.value)
        
    # Overload: Integer conversion (int), if possible
    def __int__(self):
        return int(float(self.value))

    # Overload: Integer conversion (float), if possible
    def __float__(self): 
        return float(self.value)
    
    # Derivative
    def diff(self,var):
        return Constant(0)
    
    # Evaluate
    def evaluate(self,Dic={}):
        return self
    
#---END Subclass: Constant---------------------------------------------


#---Subclass: Variable-----------------------------------------------------

# Represents a variable
class Variable(Expression):
    
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

# Represents a function of 1 variable
# Note: at the moment we cannot deal with function composition (functions are leaves)
# Note: at the moment we cannot deal with multiple variable
class Function(Expression):
    
    def __init__(self, funcharacter, varcharacter):
        self.funchar=str(funcharacter)
        self.varchar=str(varcharacter)
        
    def __str__(self):
        return self.funchar+'('+self.varchar+')'

    def __eq__(self,other):
        return self.funchar==other.funchar and self.varchar==other.varchar
    
#---END Subclass: Function-------------------------------------------------


#---Subclass: Basic-----------------------------------------------
class Basic(Function):
    # Represents a standard function of 1 variable (sin,cos,log or negations)

    # Overload: Negation (-)
    def __neg__(self):
        if self.char[0] == '-':
            return Variable(self.char[1:])
        else:
            return Variable('-'+self.char)

    # Derivative of basic functions
    def diff(self,variable):
        if self.varchar == variable:
            if self.funchar=='sin':
                return Basic('cos',self.varchar)
            elif self.funchar=='cos':
                return Basic('-sin',self.varchar)
            elif self.funchar=='-sin':
                return Basic('-cos',self.varchar)
            elif self.funchar=='-cos':
                return Basic('sin',self.varchar)
            elif self.funchar=='log':
                return Constant(1)/Variable(self.varchar)
            elif self.funchar=='-log':
                return Constant(-1)/Variable(self.varchar)
            else:
                return None
        else:
            return Constant(0)

    # Evaluaton of basic functions
    def evaluate(self,Dic={}):
        if self.varchar in Dic:
            if self.funchar=='sin':
                return Constant(math.sin(Dic[self.varchar]))
            elif self.funchar=='cos':
                return Constant(math.cos(Dic[self.varchar]))
            elif self.funchar=='log':
                return Constant(math.log(Dic[self.varchar]))
            elif self.funchar=='-sin':
                return Constant(-math.sin(Dic[self.varchar]))
            elif self.funchar=='-cos':
                return Constant(-math.cos(Dic[self.varchar]))
            elif self.funchar=='-log':
                return Constant(-math.log(Dic[self.varchar]))
            # In case of unknown function, return self, but this should be avoided
            else:
                return self
        else:
            return self
        
#---END Subclass: Basic-------------------------------------------------------------------------

 
#---Subclass: BinaryNode-----------------------------------------------------------------

# Represents a binary tree, where each internal node represents an operation        
class BinaryNode(Expression):
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol

    #---Overload: Equality (==) -------------------------------------------------------------------
        
    # Uses recursion on children of nodes
    
    def __eq__(self, other):
        if type(self) == type(other):
            
            # Checks equality of AddNodes and MultiplyNodes (commutativity and assiociativity)
            if self.op_symbol in ['+','*']:
                
                # Checks if: (a+b)+(c+d)=(x+y)+(z+p) or '*' instead of '+'
                if isinstance(self.lhs,BinaryNode) and isinstance(self.rhs,BinaryNode) and\
                   isinstance(other.lhs,BinaryNode) and isinstance(other.rhs,BinaryNode) and\
                   self.op_symbol==self.lhs.op_symbol and\
                   self.op_symbol==self.rhs.op_symbol and\
                   self.op_symbol==other.lhs.op_symbol and\
                   self.op_symbol==other.rhs.op_symbol:
                    # We check the cases respectively: (a+b),(c+d)=
                    # (x+y),(z+p); (z+p),(x+y); (x+z),(y+p); (y+p),(x+z); (x+p),(y+z); (y+z),(x+p)
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
                
                # Checks if: (a+b)+c=(x+y)+z, where c and z are not AddNodes (also '*' instead of '+')
                elif isinstance(self.lhs,BinaryNode) and isinstance(other.lhs,BinaryNode) and\
                     self.op_symbol==self.lhs.op_symbol and\
                     self.op_symbol==other.lhs.op_symbol:
                    # Checks the cases respectively: (a+b),c=
                    # (x+y),z; (x+z),y; (y+z),x
                    return (self.lhs == other.lhs and self.rhs == other.rhs) or\
                           (self.lhs == type(self)(other.lhs.lhs,other.rhs) and\
                           self.rhs == other.lhs.rhs) or\
                           (self.lhs == type(self)(other.lhs.rhs.other.rhs) and\
                           self.rhs == other.lhs.lhs)

                # Checks if: a+(b+c)=x+(y+z): 
                elif isinstance(self.rhs,BinaryNode) and isinstance(other.rhs,BinaryNode) and\
                     self.op_symbol==self.rhs.op_symbol and\
                     self.op_symbol==other.rhs.op_symbol:
                    # Checks the cases respectively: a,(b+c)=
                    # x,(y+z); z,(y+x); y,(z+x)
                    return (self.lhs == other.lhs and self.rhs == other.rhs) or\
                           (self.rhs == type(self)(other.rhs.lhs,other.lhs) and\
                           self.lhs == other.rhs.rhs) or\
                           (self.rhs == type(self)(other.rhs.rhs,other.lhs) and\
                           self.lhs == other.rhs.lhs)
                
                # Checks if: (a+b)+c=x+(y+z): 
                elif isinstance(self.lhs,BinaryNode) and isinstance(other.rhs,BinaryNode) and\
                     self.op_symbol==self.lhs.op_symbol and\
                     self.op_symbol==other.rhs.op_symbol:
                    # Checks the cases respectively: (a+b),c=
                    # (y+z),x; (y+x),z; (z+x),y
                    return (self.lhs == other.rhs and self.rhs == other.lhs) or\
                           (self.lhs == type(self)(other.rhs.lhs,other.lhs) and\
                           self.rhs == other.rhs.rhs) or\
                           (self.lhs == type(self)(other.rhs.rhs,other.lhs) and\
                           self.rhs == other.rhs.lhs)

                # Checks if: a+(b+c)=(x+y)+z:
                elif isinstance(self.rhs,BinaryNode) and isinstance(other.lhs,BinaryNode) and\
                     self.op_symbol==self.rhs.op_symbol and\
                     self.op_symbol==other.lhs.op_symbol:
                    # Checks the cases respectively: a,(b+c)=
                    # z,(x+y); y,(x+z); x,(y+z)
                    return (self.lhs == other.rhs and self.rhs == other.lhs) or\
                           (self.rhs == type(self)(other.lhs.lhs,other.rhs) and\
                           self.lhs == other.lhs.rhs) or\
                           (self.rhs == type(self)(other.lhs.rhs,other.rhs) and\
                           self.lhs == other.lhs.lhs)
                
                # Checks if: a+b=x+y
                else:
                    # We check the cases a,b=x,y and a,b=y,x
                    return (self.lhs == other.lhs and self.rhs == other.rhs) or\
                           (self.lhs == other.rhs and self.rhs == other.lhs)
                
            # Checks the other operators '-','/','**' (non-commutative and non-associative)
            else:
                return self.lhs == other.lhs and self.rhs == other.rhs
            
        # If NodeTypes are not the same, then the expressions are not equal
        else:
            return False
        
    #---END Overload: Equality ==----------------------------------------------------------------


    #---Overload: String str-------------------------------------------------------------------
        
    # Uses recursion on children of nodes

    def __str__(self):
        LS=str(self.lhs)
        RS=str(self.rhs)
        Left=''
        Right=''
        Prec={'+':1,'-':1,'*':2,'/':2,'**':3,}
        oplist = ['+','-','*','/','**']
        
        # Part 1: simplify situations where children stringify to 0, 1 or -1
        # Case: both children stringify to '0' or '0.0'
        # Note: we ignore difficulties with 0/0 and 0**0
        if isint(LS) and isint(RS) and\
           int(float(str(self.lhs)))==0 and int(float(str(self.rhs)))==0:
            # Returns '0'
            return str(0)

        # Case: only left child stringifies to '0' or '0.0'
        if isint(LS) and int(float(LS))==0:
            # Subcase: 0+a -> a
            if self.op_symbol=='+':
                return RS         
            # Subcase: 0*a,0/a,0**a -> 0
            elif self.op_symbol in ['*','/','**']: # 0*a=0/a=0**a=0
                return str(0)            
            # Subcase: 0-a -> -a
            elif self.op_symbol=='-':                
                # Subsubcase: a is not a BinaryNode (constant,variable or function)
                if not isinstance(self.rhs,BinaryNode):
                    return str(-self.rhs)                
                # Subsubcase: a is BinaryNode
                else:
                    # Subsubsubcase: a stringifies to expression
                    if isexp(RS):
                        return '-'+'('+RS+')'
                    # Subsubsubcase: a does not stringifies to expression
                    else:
                        if RS[0]=='-':
                            return RS[1:]
                        else:
                            return '-'+RS

        # Case: only right child stringifies to '0' or '0.0'
        if isint(RS) and int(float(RS))==0:
            # Subcase: a+0,a-0 -> a
            if self.op_symbol in ['+','-']:
                return LS
            # Subcase: a*0 -> 0
            elif self.op_symbol=='*':
                return str(0)
            # Subcase: a**0 -> 1
            elif self.op_symbol=='**':
                return str(1)

        # Case: left child stringifies to '1' or '1.0'
        if isint(LS) and int(float(LS))==1:
            # Subcase: 1*a -> a
            if self.op_symbol=='*': 
                return RS
            # Subcase: 1**a -> 1
            elif self.op_symbol=='**': 
                return str(1)

        # Case: (only) right child stringifies to '1' or '1.0'       
        if isint(RS) and int(float(RS))==1:
            # Subcase: a*1,a/1,a**1 -> a (only subcase)
            if self.op_symbol in ['*','/','**']:
                return LS
            
        # Case: left child stringifies to '-1' or '-1.0'
        if isint(LS) and int(float(LS))==-1:
            # Subcase: (-1)*a -> -a (only subcase)
            # Note: if a is BinaryNode, then (-1)*a -> -a -> 0-a, which is dealt with above
            if self.op_symbol=='*':
                return(str(-self.lhs))
            
        # Case: (only) right child stringifies to '-1' or '-1.0'   
        if isint(RS) and int(float(RS))==-1:
            # Subcase: a*(-1),a/(-1) -> -a
            if self.op_symbol in ['*','/']:
                return(str(-self.rhs))

        # Part 2: after dealing with 0,1,-1 we deal with brackets
        # We deal with left and right child seperately
        
        # Left child case: child is a BinaryNode
        if isinstance(self.lhs,BinaryNode):

            #Subcase: child operator has lower precedence than parent operator
            if Prec[self.lhs.op_symbol]<Prec[self.op_symbol]:
                #Subsubcase: child stringifies to expression
                if isexp(LS):
                    Left='('+LS+')'
                #Subsubcase: child stringifies to number, constant or variable
                else:
                    Left=LS                    
            # Subcase: both operators are '**'
            elif self.op_symbol=='**' and self.lhs.op_symbol=='**':
                Left='('+LS+')'
            #Subcase: child operator has higher or equal precedence than parent operator (not both '**')
            else:
                Left=LS

        # Left child case: child is not a BinaryNode
        else: 
            Left=LS

        # Right child case: child is a BinaryNode
        if isinstance(self.rhs,BinaryNode):
            # Subcase: child stringifies to expression
            if isexp(RS):                
                # Subssubcase: child operator has lower or equal precedence than parent operator
                if Prec[self.rhs.op_symbol]<Prec[self.op_symbol]:
                    Right='('+RS+')'
                # Subsubcase: child operator has equal precedence as parent operator
                elif Prec[self.rhs.op_symbol]==Prec[self.op_symbol]:
                    # Subsubsubcase: operator is '-', '/', '**'
                    if self.op_symbol in ['-','/','**']:
                        Right='('+RS+')'
                    # Subsubsubcase: operator is '+','*'
                    else:
                        Right=RS
                # Subsubcase: child operator has higher precedence than parent operator
                else:
                    Right=RS
            # Subcase: child stringifies to number, constant or variable
            else:
                # Subsubcase: child stringifies to "positive" number, constant or variable
                if ispos(RS):
                    Right=RS
                # Subsubcase: child stringifies to "negative" number, constant or variable
                else:
                    Right='('+RS+')'

        # Right child case: child is not a BinaryNode
        else:
            # Subcase: child is not positive and operator is '-' or '/'
            if not ispos(self.rhs) and self.op_symbol in ['+','-']:
                Right='('+str(self.rhs)+')'
            # Subcase: other cases
            else:
                Right=str(self.rhs)

        # Put all parts together
        return Left+' '+self.op_symbol+' '+Right
    
        #---END Overload: String str-------------------------------------------------------------------

    #---Derivative of binary tree----------------------------------------------------------------------
    
    # Uses recursion and basic differentiation rules
    # Note: at the moment we cannot deal with expressions a**x, where x is not a constant
    
    def diff(self,var):       
        # conversion python numbers to our classes.
        if type(self.lhs) == int or type(self.lhs) == float:
            self.lhs = Constant(self.lhs)
        if type(self.rhs) == int or type(self.rhs) == float:
            self.rhs = Constant(self.rhs)
        
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
        
    #---END Derivative of binary tree--------------------------------------------------------------------------


    #---Evaluation of binary tree------------------------------------------------------------------------
        
    # Evaluates the expression, values of variables are loaded through dictionary
    # Returns a new tree, where numerical constants are united where possible (e.g. 1+2->3)
    # Uses recursion on children
    
    def evaluate(self,Dic={}):
        
        # Case: children evaluate to numerical values (allowing for basic arithmetics)
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
                
        # Case: At least one child evaluates to tree or non-numerical constant
        return type(self)(self.lhs.evaluate(Dic),self.rhs.evaluate(Dic))
    
    #---END Evaluation of binary tree----------------------------------------------------------------------


#---END Subclass: BinaryNode---------------------------------------------------------------------------


#---Subclasses of BinaryNode---------------------------------------------------------------------------
        
class AddNode(BinaryNode):
    #Represents the addition operator
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

class SubtractNode(BinaryNode):
    #Represents the subtraction operator
    def __init__(self, lhs, rhs):
        super(SubtractNode, self).__init__(lhs, rhs, '-')

class MultiplyNode(BinaryNode):
    #Represents the multiplication operator
    def __init__(self, lhs, rhs):
        super(MultiplyNode, self).__init__(lhs, rhs, '*')

class DivideNode(BinaryNode):
    #Represents the division operator
    def __init__(self, lhs, rhs):
        super(DivideNode, self).__init__(lhs, rhs, '/')

class PowerNode(BinaryNode):
    #Represents the exponentiation operator
    def __init__(self, lhs, rhs):
        super(PowerNode, self).__init__(lhs, rhs, '**')
        
#---END Subclasses if BinaryNode----------------------------------------------------------------------------

