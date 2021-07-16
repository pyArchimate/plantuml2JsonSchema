# Copyright 2018 Pedro Cuadra - pjcuadra@gmail.com
# https://github.com/pjcuadra/plantuml-parser
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
#    see: https://lark-parser.readthedocs.io/_/downloads/en/latest/pdf/
#


import logging
from lark import Lark
from sys import argv
import os
from lark import Transformer


class Trsf(Transformer):

    def __init__(self):
        super().__init__()
        self.cl_name = {}
        self.cl_doc = ''
        self.cl_attr = {}
        self.cl = {}
        self.classes = []

    def new_cl(self):
        self.cl_name = {}
        self.cl_doc = ''
        self.cl_attr = {}
        self.cl = {}

    def var(self, s):
        (s,) = s
        return s[:]

    def type(self, s):
        (s,) = s
        return s[:]

    def variable(self, s):
        return (s[0],s[1])

    def attribute(self, s):
        doc = s[2] if (len(s) > 2) else ''
        self.cl_attr[s[1][0]] = {"type": s[1][1], "description": doc}
        self.cl = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": self.cl_name,
            "type": "object",
            "description": self.cl_doc,
            "properties": self.cl_attr
        }
        return s[1]

    def class_name(self, s):
        self.classes.append(self.cl)
        self.new_cl()
        self.cl_name = '.'.join([s[0][:],s[1][:]])
        return {"class": self.cl_name}

    def bcomment(self, s):
        (s,) = s
        return s[:].strip()

    def ccomment(self, s):
        (s,) = s
        self.cl_doc = s[:].strip()
        return s[:].strip()

    def _class(self, s):
        return s

    def package(self, s):
        return

    def alias(self, s):
        return

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False

    start = list


def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] is '-':  # Found a "-name value" pair.
            if len(argv) > 1:
                if argv[1][0] != '-':
                    opts[argv[0]] = argv[1]
                else:
                    opts[argv[0]] = True
            elif len(argv) == 1:
                opts[argv[0]] = True

        # Reduce the argument list by copying it starting from index 1.
        argv = argv[1:]
    return opts


if __name__ == '__main__':
    myargs = getopts(argv)

    dir_path = os.getenv('USERPROFILE')
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    grammar_file_path = os.path.join(dir_path, "grammar", "grammar.ebnf")
    f = open(grammar_file_path)

    parser = Lark(f.read())

    if '-i' in myargs:
        f = open(myargs['-i'])
    else:
        exit(1)

    if '-v' in myargs:
        logging.basicConfig(level=logging.INFO)

    tree = parser.parse(f.read())
    # print(tree.pretty())
    tr = Trsf()
    tree1 = tr.transform(tree)
    # print(yaml.dump(tr.cl))
    tr.classes.append(tr.cl)
    tr.classes.pop(0)
    print(tr.classes)

