"""Classes for internal representations of mathematical expressions"""
from math import gcd, lcm
from numbers import Number

"""Undefined flyweight; default value for expressions that can not be evaluated
"""
UNDEFINED = "UNDEFINED" 

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
        return self
    
    def num(self):
        return self
    
    def denom(self):
        return Integer(1)

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
                # #thus the result of simp_eval is also rational
                # computed_rational = Power(v, operands[1]).simp_eval()
                # if isinstance(computed_rational, Integer):
                    # return 
                computed_rational = Power(v, operands[1]).simp_eval().simplify()
                return computed_rational
            else:
                w = Expression.simplify_rational_expression(operands[1])
                if w is UNDEFINED:
                    return UNDEFINED
                return type(expr)(v, w).simp_eval()
            
        else:
            raise ValueError("Expected a rational expression with 1 or 2 operands")

    def __eq__(self, other):
        """Check if two expressions are syntactically equal. For this to make sense, 
        both expressions should be ASAE (Automatically-Simplified Arithmetic Expressions)."""
        if isinstance(self, Constant) and isinstance(other, Constant):
            return self.eval() == other.eval()
        
        if isinstance(other, Expression):
            return str(self) == str(other)
        
        return NotImplemented
    
    def __gt__(self, other):
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

    def eval(self, **vars):
        return sum([term.eval(**vars) for term in self.terms])
    
    def simp_eval(self):
        total = Integer(0)
        for term in self.terms:
            total += term.simp_eval()
        return total.simplify()
    
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
            #TODO: Implement the rest of the sum simplification routine
            if u_1_sum:
                if u_2_sum:
                    return Sum.merge_sums(u_1.operands(), u_2.operands())
                else:
                    return Sum.merge_sum(u_1.operands, [u_2])
            else:
                if u_2_sum:
                    return Sum.merge_sum([u_1], u_2.operands())
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
                        S = Sum(u_1.coefficient(), u_2.coefficient())
                        P = Product(S, u_1.term())
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
        factor_repr = [str(factor) for factor in self.factors]
        return "(" + " * ".join(factor_repr) + ")"
    
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

    def eval(self, **vars):
        prod = 1
        for factor in self.factors:
            prod *= factor.eval(**vars)
        return prod
    
    def simp_eval(self):
        prod = Integer(1)
        for factor in self.factors:
            prod *= factor.simp_eval()
        return prod.simplify()

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

    def operands(self):
        return self.factors
    
    def coefficient(self):
        return self.factors[0] if isinstance(self.factors[0], Constant) else Integer(1)
    
    def term(self):
        return Product(self.factors[1::]) if isinstance(self.factors[0], Constant) else self

class Div(Expression):
    """A Div represents the quotient of two terms. 
    If both terms are integers, it is simplified to a rational number."""
    def __repr__(self):
        return f"({self.left} / {self.right})"
    
    def eval(self, **vars):
        return self.left.eval(**vars) / self.right.eval(**vars)
    
    def simp_eval(self):
        return self.left.simp_eval() / self.right.simp_eval()
    
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
    
    def eval(self, **vars):
        return self.left.eval(**vars) ** self.right.eval(**vars)
    
    def simp_eval(self):
        return self.left.simp_eval() ** self.right.simp_eval()
    
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
    
    def eval(self, **vars):
        print("factorial operation not yet implemented")
        return 1
    
    def simp_eval(self):
        print("factorial operation not yet implemented")
        return Integer(1)
    
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

    def eval(self, **vars):
        val = vars.get(self.name, None)
        if val is None:
            raise ValueError(f"Variable {self.name} was not given a value")
        return val
    
    def simp_eval(self):
        return self
    
    def simplify(self):
        return self
    
    def operands(self):
        return [self.name]

class Constant(Expression):
    """A Constant represents a constant value"""

    def __lt__(self, other):
        """Total ordering for Constants: O-1"""
        if isinstance(other, Constant):
            return self.value < other.eval()
        
        if isinstance(other, Expression):
            return True
        
        return NotImplemented
    
    def simp_eval(self):
        return self
    
    #Treat both constants as Rationals, 
    #perform the computation
    #simplify the result.
    def __add__(self, other):
        if not isinstance(other, Constant):
            return super().__add__(other)
        
        if isinstance(self, Integer):
            self = Rational(self.eval(), 1)
        if isinstance(other, Integer):
            other = Rational(other.eval(), 1)

        denom_lcm = lcm(self.denom(), other.denom())
        left_num = denom_lcm * self.num()
        right_num = denom_lcm * other.num()
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

class Special(Expression):
    """Special represents special cases"""

    def __init__(self):
        raise NotImplementedError("Special cases not yet implemented")
    
    def __repr__(self):
        raise NotImplementedError("Special cases not yet implemented")