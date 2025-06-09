"""Classes for internal representations of mathematical expressions"""
from math import gcd, lcm, comb 
from numbers import Number

#TODO: Deal with **symbols dictionary. It should ideally be global
#to avoid conflicts with the simplify function

#TODO: Deal with redefinition of functions.
# Recursion works (correctly raises error), but now we should store functions
# in the symbol table differently, or copy them over differently
# no need to copy the definition over, if the sym_eval will just 
# get the global definition first 

#TODO: Make note of the following behavior:
#1: f(x) = x
#2: x = 2
#3: f(x) -> 2, but intended would be: f(x) -> x
#No way to avoid overwriting parameters? Except manually when parsing.
#Causes the following error:
#1: f(x, y) = x + y
#2: f(0, x) -> 0 (incorrect), the names of the param args shouldn't matter.
#Possible solution, change the internal representations of the parameters
#in a function definition so that they don't matter?
#NOTE: More complicated, consider:
#1: f(x) = x
#2: g(x) = f(x)
#3: g(1) -> Should return 1

#TODO: Deal with errors in the following:
#1: f(x) = x
#2: g(y) = y
#3: simplify f(x) + g(y) -> Error??

#TODO: Parse error? 
#1: g(x, y) = g(0, 0) + g(0, 1)
#"None is not a valid function definition"

#TODO: Fix algebraic expand: Elementary Algorithms page 253
#Use example: (x + 1)(x + 2) -> (x^2) + (3*x) + 2


"""Undefined flyweight; default value for expressions that can not be evaluated
"""
UNDEFINED = "UNDEFINED" 

class CAS_ENV:
    """An environment class that specifies a symbol and function table"""
    def __init__(self):

        #A dictionary of symbols and their definitions.
        self.symbols = dict()

class Expression:
    """An Expression is a general mathematical object.
    In this case, it is used to represent binary operations
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    """The following four methods allow us to treat arbitrary expressions as powers/products/rationals. 
    This is useful for automatic simplification and total ordering of expressions.
    """
    def base(self):
        return self
    
    def exponent(self):
        return Integer(1)
    
    def coefficient(self):
        return Integer(1)
    
    def term(self):
        return Product(self)
    
    def num(self):
        return self
    
    def denom(self):
        return Integer(1)

    def algebraic_expand(self):
        return self

    @staticmethod
    def simplify_rational_expression(expr):
        """Recursively simplifies a rational expression into lowest terms."""
        if isinstance(expr, Integer):
            return expr
        
        if isinstance(expr, Rational):
            return expr.simplify()
        
        operands = expr.operands()
        if len(operands) == 1:
            return Expression.simplify_rational_expression(operands[0])
        
        elif len(operands) == 2:
            v = Expression.simplify_rational_expression(operands[0])
            if v is UNDEFINED:
                return UNDEFINED
            
            if isinstance(expr, Power):
                #We are guaranteed a Power with rational base and integer exponent
                # #thus the result of sym_eval is also rational
                # computed_rational = Power(v, operands[1]).sym_eval()
                # if isinstance(computed_rational, Integer):
                    # return 
                computed_rational = Power(v, operands[1]).sym_eval().simplify()
                return computed_rational
            else:
                w = Expression.simplify_rational_expression(operands[1])
                if w is UNDEFINED:
                    return UNDEFINED
                return type(expr)(v, w).sym_eval()
            
        else:
            raise ValueError("Expected a rational expression with 1 or 2 operands")

    """The following dunder methods allow us to treat python statements as AST's"""
    def __eq__(self, other):
        """Check if two expressions are syntactically equal. For this to make sense, 
        both expressions should be ASAE (Automatically-Simplified Arithmetic Expressions)."""
        if isinstance(self, Constant) and isinstance(other, Constant):
            return self.eval() == other.eval()
        
        if isinstance(other, Expression):
            return str(self) == str(other)
        
        return NotImplemented
    
    def __hash__(self):
        hash(str(self))

    def __gt__(self, other):
        #This method is called as the "inverse" of the lt method
        #i.e: if (a < b) returns NotImplemented, this ensures that
        # (not b < a) is returned
        return not (self < other)
    
    def __add__(self, other):
        return Sum(self, other) if isinstance(other, Expression) else NotImplemented
    
    def __sub__(self, other):
        return Sum(self, Product(Integer(-1), other)) if isinstance(other, Expression) else NotImplemented
    
    def __mul__(self, other):
        return Product(self, other) if isinstance(other, Expression) else NotImplemented
    
    def __truediv__(self, other):
        return Div(self, other) if isinstance(other, Expression) else NotImplemented
    
    def __pow__(self, other):
        return Power(self, other) if isinstance(other, Expression) else NotImplemented

class Sum(Expression):
    """A Sum is the sum of two terms"""
    def __init__(self, *terms):
        self.terms = list(terms)
        
    def __repr__(self):
        term_repr = [str(term) for term in self.terms]
        return "(" + " + ".join(term_repr) + ")"
    
    def __lt__(self, other):
        """Total ordering for Sums: O-3"""
        if isinstance(other, Sum):
            #O-3 (1 & 2) Compare terms from most significant (last term) to least.
            num_left = len(self.terms)
            num_right = len(other.terms)
            min_length = min(num_left, num_right)
            for i in range(min_length - 1, -1, -1):
                if self.terms[i] == other.terms[i]:
                    continue
                return self.terms[i] < other.terms[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        if isinstance(other, Expression) and not isinstance(other, Constant) and not isinstance(other, Power):
            #O-10 (Unary Sum)
            test_other = Sum(other)
            return self < test_other
        
        return NotImplemented
    
    def __add__(self, other):
        #Overrides parent method to denest the addition of two sums
        #example: x + y + z should be Sum(x, y, z), not Sum(Sum(x, y), z)
        if isinstance(other, Sum):
            self.terms += other.operands
            return self
        
        if isinstance(other, Expression):
            self.terms.append(other)
            return self

        return NotImplemented

    def copy(self) -> Expression:
        """Return a copy of this sum

        Returns:
            Expression: A copy of the sum
        """
        copied_sums = [term.copy() for term in self.terms]
        return Sum(*copied_sums)

    def sym_eval(self, **symbols):
        total = Integer(0)
        for term in self.terms:
            total += term.sym_eval(**symbols)
        return total.simplify()
    
    def algebraic_expand(self):
        if len(self.terms) == 1:
            return self.terms[0].algebraic_expand()
        v = self.terms[0]
        u_minus_v = Sum(*self.terms[1::])
        return (v.algebraic_expand() + u_minus_v.algebraic_expand())

    def simplify(self):
        L = [term.simplify() for term in self.terms]
        
        #S-SUM (1)
        if UNDEFINED in L:
            return UNDEFINED
        
        #S-SUM (3)
        if len(L) == 1:
            return L[0]
        
        #S-SUM (4)
        v = Sum.simplify_sum_rec(L)
        if len(v) == 0:
            return Integer(0)
        elif len(v) == 1:
            return v[0]
        else:
            return Sum(*v)

    @staticmethod
    def simplify_sum_rec(terms):
        assert len(terms) >= 2

        u_1 = terms[0]
        u_2 = terms[1]
        u_1_sum = isinstance(u_1, Sum)
        u_2_sum = isinstance(u_2, Sum)
        if len(terms) == 2:
            if u_1_sum:
                if u_2_sum:
                    return Sum.merge_sums(u_1.operands(), u_2.operands())
                else:
                    return Sum.merge_sums(u_1.operands(), [u_2])
            else:
                if u_2_sum:
                    return Sum.merge_sums([u_1], u_2.operands())
                else:
                    #Neither operand is a sum
                    if isinstance(u_1, Number):
                        u_1 = Rational(u_1).simplify()
                    
                    if isinstance(u_2, Number):
                        u_2 = Rational(u_2).simplify()

                    if isinstance(u_1, Constant) and isinstance(u_2, Constant):
                        P = Expression.simplify_rational_expression(Sum(u_1, u_2))
                        if P == Integer(0):
                            return list()
                        return [P]

                    if u_1 == Integer(0):
                        return [u_2]
                    
                    if u_2 == Integer(0):
                        return [u_1]
                    
                    if u_1.term() == u_2.term():
                        S = Sum(u_1.coefficient(), u_2.coefficient()).simplify()
                        P = Product(S, u_1.term()).simplify()
                        if P == Integer(0):
                            return list()
                        return [P]
                    
                    if u_2 < u_1:
                        return [u_2, u_1]
                    return terms

        elif len(terms) > 2:
            w = Sum.simplify_sum_rec(terms[1::])
            if u_1_sum:
                return Sum.merge_sums(u_1.operands(), w)
            else:
                return Sum.merge_sums([u_1], w)
            
    @staticmethod
    def merge_sums(p, q):
        if len(q) == 0:
            return p
        if len(p) == 0:
            return q
        
        p_1 = p[0]
        q_1 = q[0]
        h = Sum.simplify_sum_rec([p_1, q_1])

        if len(h) == 0:
            return Sum.merge_sums(p[1::], q[1::])
        if len(h) == 1:
            return h + Sum.merge_sums(p[1::], q[1::])
        if h[0] == p_1:
            assert h[1] == q_1
            return [p_1] + Sum.merge_sums(p[1::], q)
        else:
            assert h[0] == q_1 and h[1] == p_1
            return [q_1] + Sum.merge_sums(p, q[1::])
        
    def operands(self):
        return self.terms

class Product(Expression):
    """A Product is the product of two factors"""
    def __init__(self, *factors):
        self.factors = list(factors)

    def __repr__(self):
        if len(self.factors) == 2 and isinstance(self.factors[0], Integer) and isinstance(self.factors[1], Variable):
            return f"{self.factors[0]}{self.factors[1]}" #Implicit multiplication is easier on the eyes
        
        factor_repr = [str(factor) for factor in self.factors]
        return "(" + " \u00B7 ".join(factor_repr) + ")" #\u00b7 -> \cdot
    
    def __lt__(self, other):
        """Total ordering for Products: O-3"""
        if isinstance(other, Product):
            #O-3 (1 & 2) Compare factors from most significant (last factor) to least.
            num_left = len(self.factors)
            num_right = len(other.factors)
            min_length = min(num_left, num_right)
            for i in range(min_length - 1, -1, -1):
                if self.factors[i] == other.factors[i]:
                    continue
                return self.factors[i] < other.factors[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        if isinstance(other, Expression) and not isinstance(other, Constant):
            #Rule O-8; test against unary product
            test_other = Product(other)
            return self < test_other

        return NotImplemented 
    
    def copy(self):
        copied_factors = [factor.copy() for factor in self.factors]
        return Product(*copied_factors)

    def sym_eval(self, **symbols):
        prod = Integer(1)
        for factor in self.factors:
            prod *= factor.sym_eval(**symbols)
        return prod.simplify()

    def algebraic_expand(self):
        if len(self.factors) == 1:
            return self.factors[0].algebraic_expand()
        
        v = self.factors[0]
        u_div_v = Product(*self.factors[1::])
        return Product.expand_product(v.algebraic_expand(), u_div_v.algebraic_expand())

    def simplify(self):
        self.factors = [factor.simplify() for factor in self.factors]

        #S-PRD (1)
        if UNDEFINED in self.factors:
            return UNDEFINED
        
        #S-PRD (2)
        if Integer(0) in self.factors:
            return Integer(0)
        
        #S-PRD (3)
        if len(self.factors) == 1:
            return self.factors[0]
        
        #S-PRD (4)
        v = Product.simplify_product_rec(self.factors)
        if len(v) == 0:
            return Integer(1)
        elif len(v) == 1:
            return v[0]
        else:
            return Product(*v)

    @staticmethod
    def simplify_product_rec(factors):
        assert len(factors) >= 2
        u_1 = factors[0]
        u_2 = factors[1]
        u_1_prod = isinstance(u_1, Product)
        u_2_prod = isinstance(u_2, Product)

        if len(factors) == 2:
            if u_1_prod:
                #S-PRD-REC (2)
                if u_2_prod:
                    return Product.merge_products(u_1.factors, u_2.factors)
                
                #S-PRD-REC (2)
                else:
                    return Product.merge_products(u_1.factors, [u_2])

            else:
                #S-PRD-REC (2)
                if u_2_prod:
                    return Product.merge_products([u_1], u_2.factors)
                
                #S-PRD-REC (1)
                else: 
                    #Neither operand is a product
                    if isinstance(u_1, Number):
                        u_1 = Rational(u_1).simplify()

                    if isinstance(u_2, Number):
                        u_2 = Rational(u_2).simplify()

                    if (isinstance(u_1, Constant) and isinstance(u_2, Constant)):
                        P = Expression.simplify_rational_expression(Product(u_1, u_2))
                        if P == Integer(1):
                            return list()
                        return [P]
                    
                    if u_1 == Integer(1):
                        return [u_2]
                    if u_2 == Integer(1):
                        return [u_1]
                    
                    if u_1.base() == u_2.base():
                        S = Sum(u_1.exponent(), u_2.exponent()).simplify()
                        P = Power(u_1.base(), S).simplify()
                        if P == Integer(1):
                            return list()
                        return [P]
                    
                    if u_1 < u_2:
                        return [u_1, u_2]
                    
                    return [u_2, u_1]
                
        if len(factors) > 2:
            #S-PRD-REC (3)
            w = Product.simplify_product_rec(factors[1::])
            if u_1_prod:
                return Product.merge_products(u_1.operands(), w)
            else:
                return Product.merge_products([u_1], w)
            
    @staticmethod 
    def merge_products(p, q):

        assert p is not None
        assert q is not None

        #M-PRD (1)
        if len(q) == 0:
            return p
        
        #M-PRD (2)
        if len(p) == 0:
            return q
        
        p_1 = p[0]
        q_1 = q[0]

        #M-PRD (3)
        h = Product.simplify_product_rec([p_1, q_1])
        if len(h) == 0:
            return Product.merge_products(p[1::], q[1::])
        elif len(h) == 1:
            return h + Product.merge_products(p[1::], q[1::])
        else:
            assert len(h) == 2
            if h[0] == p_1:
                assert h[1] == q_1
                return [p_1] + Product.merge_products(p[1::], q)
            
            assert h[0] == q_1
            assert h[1] == p_1
            return [q_1] + Product.merge_products(p, q[1::])

    @staticmethod
    def expand_product(r: Expression, s: Expression):
        if isinstance(r, Sum):
            if len(r.terms) == 1: 
                return (r.terms[0] * s).algebraic_expand()
            
            f = r.terms[0]
            r_minus_f = Sum(*r.terms[1::])
            return Product.expand_product(f, s) + Product.expand_product(r_minus_f, s)
        
        if isinstance(s, Sum):
            return Product.expand_product(s, r)
        
        return r * s

    def operands(self):
        return self.factors
    
    def coefficient(self):
        return self.factors[0] if isinstance(self.factors[0], Constant) else Integer(1)
    
    def term(self):
        return Product(*self.factors[1::]) if isinstance(self.factors[0], Constant) else self
    
    def __mul__(self, other):
        if isinstance(other, Product):
            self.factors += other.operands()
            return self
        
        if isinstance(other, Expression):
            self.factors.append(other)
            return self
        
        return NotImplemented

class Div(Expression):
    """A Div represents the quotient of two terms. 
    If both terms are integers, it is simplified to a rational number."""
    def __repr__(self):
        return f"({self.left} / {self.right})"
    
    def copy(self):
        return Div(self.left.copy(), self.right.copy())
    
    def sym_eval(self, **symbols):
        new_div = self.left.sym_eval(**symbols) / self.right.sym_eval(**symbols)
        return new_div.simplify()
    
    def simplify(self):
        #If both left and right are integers, return a simplified fraction
        if isinstance(self.left, Integer) and isinstance(self.right, Integer):
            return Rational(self.left.value, self.right.value).simplify()
        
        else:
            return Product(self.left, Power(self.right, Integer(-1).simplify())).simplify()
        
    def num(self):
        return self.left
    
    def denom(self):
        return self.right

    def operands(self):
        return [self.left, self.right]

class Power(Expression):
    """A Power represents exponentiation"""
    def __repr__(self):
        return f"({self.left} ^ {self.right})"
    
    def copy(self):
        return Power(self.left.copy(), self.right.copy())
    
    def sym_eval(self, **symbols):
        new_pow = self.left.sym_eval(**symbols) ** self.right.sym_eval(**symbols)
        return new_pow.simplify()
    
    def __lt__(self, other):
        if isinstance(other, Expression):
            if self.base() == other.base():
                return self.exponent() < other.exponent()
            return self.base() < other.base()
        return NotImplemented

    def base(self):
        return self.left
    
    def exponent(self):
        return self.right
    
    def algebraic_expand(self):
        #TODO: Implement for non-integer exponents. See Elementary Algorithms page 253
        ###Original algorithm:
        # if isinstance(self.right, Integer) and self.right.value >= 1: #Textbook requires exponent > 1, but this modification allows x(x + 1)^1 -> x^2 + x as required
        #     return Power.expand_power(self.left.algebraic_expand(), self.right)
        
        # return self #Expand base whether or not integer exponent

        ###Modification from original algorithm: Special cases for exponents 0 and 1
        if isinstance(self.right, Integer):
            if self.right.value == 0:
                return Integer(1)
            
            if self.right.value == 1:
                return self.left.algebraic_expand()
            
            return Power.expand_power(self.left.algebraic_expand(), self.right)
        
        return self 

    def simplify(self):
        #S-POW (1)
        self.left = self.left.simplify()
        if self.left is UNDEFINED:
            return UNDEFINED
        
        self.right = self.right.simplify()
        if self.right is UNDEFINED:
            return UNDEFINED
        
        #S-POW (2)
        if self.left == Integer(0):
            if isinstance(self.right, Constant) and self.right.is_positive():
                return Integer(0)
            return UNDEFINED
        
        #S-POW (3)
        if self.left == Integer(1):
            return Integer(1)
        
        #S-POW (5)
        if isinstance(self.right, Integer):
            #SINT-POW (1)
            if isinstance(self.left, Constant):
                ret = Expression.simplify_rational_expression(self)
                return ret
            
            #SINT-POW (2)
            if self.right == Integer(0):
                return Integer(1)
            
            #SINT-POW (3)
            if self.right == Integer(1):
                return self.left
            
            #SINT-POW (4)
            if isinstance(self.left, Power):
                r = self.left.base()
                s = self.left.exponent()
                p = Product(s, self.right).simplify()
                if isinstance(p, Integer):
                    return Power(r, p).simplify()
                else:
                    return Power(r, p)
                
            #SINT-POW (5)
            if isinstance(self.left, Product):
                distributed_factors = [Power(factor, self.right) for factor in self.left.factors]
                return Product(*distributed_factors).simplify() 

        #S-POW (5)
        return self
    
    def operands(self):
        return [self.left, self.right]
    
    @staticmethod
    def expand_power(u, n):
        assert isinstance(n, Integer) and int(n) >= 0, f"Expand_power only implemented for non_negative integers"

        if isinstance(u, Sum):
            n = int(n)
            f = u.terms[0]
            if n == 1:
                return f.algebraic_expand()
            if len(u.terms) == 1:
                return (f ** Integer(n)).algebraic_expand()
            r = Sum(*u.terms[1::])
            s = Integer(0)
            for k in range(n + 1): #Binomial theorem
                c = Integer(comb(n, k)) #{n \choose k}
                s += Product.expand_product((c * f ** Integer(n-k)), Power.expand_power(r, Integer(k)))
            return s.algebraic_expand()
        
        return u ** n
        
        
class Factorial(Expression):
    """A Factorial represents the factorial of a number"""
    def __init__(self, value: Expression):
        """Create a new Factorial object"""
        self.value = value

    def __repr__(self):
        return f"({self.value}!)"
    
    def __lt__(self, other):
        if isinstance(other, Factorial):
            return self.value < other.value
        if isinstance(other, Variable):
            if self.value == other:
                return False
            return self.value < other
        return NotImplemented
    
    def copy(self):
        return Factorial(self.value.copy())
    
    def sym_eval(self, **symbols):
        if isinstance(self.value, Integer):
            if self.value == Integer(0):
                return Integer(1)
            elif self.value.is_positive():
                computed = self.value.copy()
                for i in range(1, self.value.eval()):
                    computed *= Integer(i)
                return computed.simplify()

        raise NotImplementedError("Factorial is defined for non-negative integers")
    
    def operands(self):
        return [self.value]
    
    def simplify(self):
        return Factorial(self.value.simplify())

class Variable(Expression):
    """A Variable represents a variable"""

    def __init__(self, name: str):
        """Create a new Variable object"""
        self.name = name

    def __repr__(self) -> str:
        """Return the name of the variable"""
        return self.name
    
    def __lt__(self, other):
        """Total ordering for Variables: O-2"""
        if isinstance(other, Variable):
            return self.name < other.name
        return NotImplemented

    def copy(self):
        return Variable(self.name)
    
    def sym_eval(self, **symbols):
        definition = symbols.get(self.name, None)
        if definition is None:
            return self
        if definition == self:
            return self
        return definition.sym_eval(**symbols).simplify()
    
    def simplify(self):
        return self
    
    def operands(self):
        return [self.name]

class Function(Expression):
    def __init__(self, name):
        self.name = name
        self.args = None
        self.parameters = None
        self.definition = None

    def add_args(self, *arguments, **symbols):
        self.args = list(arguments)
        assert len(self.args) == len(self.parameters), f"Number of arguments does not match number of parameters for {self}"

    def set_parameters(self, parameters: list[Variable]):
        self.parameters = parameters

    def set_definition(self, definition: Expression):
        self.definition = definition

    def sym_eval(self, **symbols):
        if not self.args:
            return self
        
        for i in range(len(self.parameters)):
            param = str(self.parameters[i])
            param_def = self.args[i].sym_eval(**symbols)
            symbols[param] = param_def
        
        definition = symbols.get(self.name, None).definition
        assert definition is not None, f"Function {self.name} was cleared?"
        return definition.sym_eval(**symbols)

    def simplify(self):
        if self.args and UNDEFINED in self.args:
            return UNDEFINED
        return self

    def __repr__(self):
        if self.args:
            args_repr = [str(arg) for arg in self.args]
            return f"{self.name}({', '.join(args_repr)})"
        return f"{self.definition}"
        
    def __lt__(self, other):
        if isinstance(other, Function):
            if self.name < other.name:
                return True
            
            num_left = len(self.args)
            num_right = len(other.args)
            min_num = min(num_left, num_right)
            for i in range(min_num):
                if self.factors[i] == other.factors[i]:
                    continue
                return self.factors[i] < other.factors[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        return NotImplemented
    
    def copy(self):
        copied = Function(self.name)
        copied.set_definition(self.definition.copy())
        copied.set_parameters(self.parameters) #Parameters not copied.
        if self.args:
            copied.add_args(*self.args)
        return copied
                
class Trig(Expression):
    """Trig functions represent the trigonometric functions"""
    orderings = ['Sin', 'Cos', 'Tan', 'Csc', 'Sec']

    def __init__(self, arg):
        self.arg = arg
        
    def __lt__(self, other):

        #If they are the same type, compare values
        if isinstance(other, type(self)): 
            return self.arg < other.arg
        
        #If they are both trig functions, compare via precedence rules
        if isinstance(other, Trig):
            self_precedence = Trig.orderings.index(type(self).__name__)
            other_precedence = Trig.orderings.index(type(other).__name__)
            return self_precedence < other_precedence
        
        #Otherwise, return false
        if isinstance(other, Expression):
            return False
        
        return NotImplemented
    
    def simplify(self):
        #Trig simplify not yet implemented
        return self
    
    def __repr__(self):
        return f"{type(self).__name__}({self.arg})"

class Sin(Trig):
    pass

class Cos(Trig):
    pass

class Tan(Trig):
    pass

class Csc(Trig):
    pass

class Sec(Trig):
    pass

class Cot(Trig):
    pass

class Constant(Expression):
    """A Constant represents a constant value"""

    def __lt__(self, other):
        """Total ordering for Constants: O-1"""
        if isinstance(other, Constant):
            return self.eval() < other.eval()
        
        if isinstance(other, Expression):
            return True
        
        return NotImplemented
    
    def sym_eval(self, **symbols):
        return self.simplify()

    def __add__(self, other):
        if not isinstance(other, Constant):
            return super().__add__(other)
        
        denom_lcm = lcm(self.denom(), other.denom())
        left_num = other.denom() * self.num()
        right_num = self.denom() * other.num()
        new_num = left_num + right_num
        return Rational(new_num, denom_lcm).simplify()

    def __sub__(self, other):
        if not isinstance(other, Constant):
            return super().__sub__(other)
        
        if isinstance(self, Integer):
            self = Rational(self.eval(), 1)
        if isinstance(other, Integer):
            other = Rational(other.eval(), 1)

        denom_lcm = lcm(self.denom(), other.denom())
        left_num = denom_lcm * self.num()
        right_num = denom_lcm * other.num()
        new_num = left_num - right_num
        return Rational(new_num, denom_lcm).simplify()
           
    def __mul__(self, other):
        if not isinstance(other, Constant):
            return super().__mul__(other)
        
        if isinstance(self, Integer):
            self = Rational(self.eval(), 1)
        if isinstance(other, Integer):
            other = Rational(other.eval(), 1)

        new_num = self.num() * other.num()
        new_denom = self.denom() * other.denom()
        return Rational(new_num, new_denom).simplify()

    def __pow__(self, other):
        if not isinstance(other, Integer):
            return super().__pow__(other)
        
        if other.is_negative():
            new_num = self.denom() ** -other.eval()
            new_denom = self.num() ** -other.eval()
        else:
            new_num = self.num() ** other.eval()
            new_denom = self.denom() ** other.eval()
        return Rational(new_num, new_denom).simplify()
    
class Rational(Constant):
    """A rational expression is a constant; a fraction of two integers"""
    def __init__(self, *args):
        for arg in args:
            assert isinstance(arg, int), f"arg {arg} is {type(arg)}"

        if len(args) == 1:
            self.left = args[0]
            self.right = 1
        else:
            super().__init__(*args)

    def __repr__(self):
        return f"({self.left} / {self.right})"
    
    def copy(self):
        return Rational(self.left, self.right)

    def eval(self, **vars):
        return self.left / self.right

    def is_positive(self):
        return (self.left < 0) if (self.right < 0) else (self.left > 0)
    
    def is_negative(self):
        return (self.left < 0) if (self.right < 0) else (self.left > 0)
    
    def num(self):
        return self.left
    
    def denom(self):
        return self.right

    def simplify(self):
        """Simplifies a fraction into lowest terms"""
        n = self.left
        d = self.right
        if d == 0:
            return UNDEFINED
        
        if n % d == 0:
            return Integer(n // d)
        
        g = gcd(n, d)
        if  d > 0:
            return Rational(n // g, d // g)
        
        else:
            return Rational(-n // g, -d // g)
        
    def operands(self):
        return [self.left, self.right]

class Integer(Constant):
    """An Integer represents a decimal integer"""

    def __init__(self, value: int):
        """Creates a new Integer object"""
        self.value = value

    def __repr__(self):
        """Returns the value of the integer"""
        return str(self.value)

    def eval(self, **vars):
        return self.value
    
    def copy(self):
        return Integer(self.value)

    def is_positive(self):
        return self.value > 0
    
    def is_negative(self):
        return self.value < 0

    def simplify(self):
        return self
    
    def operands(self):
        return [self.value]
    
    def num(self):
        return self.value
    
    def denom(self):
        return 1
    
    def __int__(self):
        return self.value

class Special(Expression):
    """Special represents special cases"""

    def __init__(self):
        raise NotImplementedError("Special cases not yet implemented")
    
    def __repr__(self):
        raise NotImplementedError("Special cases not yet implemented")