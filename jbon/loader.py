from lark import Lark, Token, Transformer

jbon_grammar = r"""
    jbon: ( class_decl | value )*

    class_decl: CNAME "{" [ CNAME ("," CNAME)* ] "}"

    ?value: constructed
          | obj
          | array
          | pair
          | string
          | SIGNED_NUMBER -> number
          | "true"        -> true
          | "false"       -> false

    constructed: CNAME [ ":" CNAME ] "(" [ value ("," value)* ] ")"
    obj: "{" [ obj_entry ("," obj_entry)* ] "}"
    obj_entry: CNAME "=" value
    array: "[" [ value ("," value)* ] "]"
    pair: "<" value "," value ">"
    string: ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.CNAME
    %import common.WS
    %ignore WS
    """

jbon_parser = Lark(jbon_grammar, start="jbon", parser="lalr")


def loads(s):
    tree = jbon_parser.parse(s)
    print(tree.pretty())
    print(JbonTransformer().transform(tree))
    return JbonTransformer().transform(tree)


class JbonTransformer(Transformer):
    def jbon(self, jbons):
        class_decls = [c for c in jbons if isinstance(c, ClassDecl)]
        values = [v for v in jbons if v not in class_decls]
        return Container(class_decls, values)

    def class_decl(self, decl):
        return ClassDecl(str(decl[0]), [str(d) for d in decl[1:]])

    def constructed(self, values):
        if isinstance(values[1], Token) and values[1].type == "CNAME":
            return Constructed(values[0], values[2:], str(values[1]))
        else:
            return Constructed(values[0], values[1:])

    def string(self, s):
        (s,) = s
        return s[1:-1]

    def number(self, n):
        (n,) = n
        return float(n)

    def obj_entry(self, e):
        return (str(e[0]), e[1])

    obj = dict
    array = list
    pair = tuple

    true = lambda self, _: True
    false = lambda self, _: False


class Container:
    def __init__(self, classes, values):
        self.classes = classes
        self.values = values

    def __getitem__(self, idx):
        try:
            v = self.values[idx]
        except TypeError:
            v = next(v for v in self.values if v.identifier == idx)

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
    def __init__(self, name, values, identifier=None):
        self._name = name
        self._values = values
        self.identifier = identifier

    def in_container(self, container):
        self.container = container

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, field):
        class_decl = self.container.class_decl(self._name)

        return next(v for f, v in zip(class_decl.fields, self._values) if f == field)

    def __repr__(self):
        return f"Constructed({self._name}, {self._values})"
