from lark import Lark, Transformer

jbon_grammar = r"""
    jbon: ( class_decl | value )*

    class_decl: CNAME "{" [ CNAME ("," CNAME)* ] "}"

    ?value: constructed
          | string
          | SIGNED_NUMBER -> number

    constructed: CNAME "(" [ value ("," value)* ] ")"
    string: ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.CNAME
    %import common.WS
    %ignore WS
    """

jbon_parser = Lark(jbon_grammar, start="jbon", parser="lalr")


class JbonTransformer(Transformer):
    def jbon(self, jbons):
        class_decls = [c for c in jbons if isinstance(c, ClassDecl)]
        values = [v for v in jbons if v not in class_decls]
        return Container(class_decls, values)

    def class_decl(self, decl):
        return ClassDecl(decl[0], [str(d) for d in decl[1:]])

    def constructed(self, values):
        return Constructed(values[0], values[1:])

    def string(self, s):
        (s,) = s
        return s[1:-1]

    def number(self, n):
        (n,) = n
        return float(n)


class Container:
    def __init__(self, classes, values):
        self.classes = classes
        self.values = values

    def __getitem__(self, idx):
        v = self.values[idx]

        try:
            v.in_container(self)
        except AttributeError:
            pass

        return v

    def class_decl(self, name):
        return next(c for c in self.classes if c.name == name)

    def __repr__(self):
        return f"Container({self.classes}, {self.values})"


class ClassDecl:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def __repr__(self):
        return f"ClassDecl({self.name}, {self.fields})"


class Constructed:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def in_container(self, container):
        self.container = container

    def __getitem__(self, field):
        class_decl = self.container.class_decl(self.name)

        return next(v for f, v in zip(class_decl.fields, self.values) if f == field)

    def __repr__(self):
        return f"Constructed({self.name}, {self.values})"


def loads(s):
    tree = jbon_parser.parse(s)
    # print(tree.pretty())
    print(JbonTransformer().transform(tree))
    return JbonTransformer().transform(tree)