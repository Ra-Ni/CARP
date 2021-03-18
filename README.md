# Compiling Another Random Program (CARP)

![](doc/other/logo.png)

CARP is a compiler written in Python. It is simple, intuitive, and customizable. CARP can be configured to accept any language or pattern. 


## Dependencies

- Python 3.7+
- Pandas
- Pydot


## Lexical Analyzer 

### Configuration File

1. Run a text editor on `lex.conf`:
```shell
vim lex.conf
```

2. Add or remove token-regex pairs in tokens:
```shell
tokens = [('token1': 'regex'),
          ('token2': '\.html')]
```

3. Add or remove reserved keywords in reserved:
```shell
reserved = {'hello',
            'world', 
            'if', 
            'else'}
```


### Command Line Arguments

```shell
lexdriver.py <file> [config]

    <file>:
        Source code file ending with the extension .src
    [config]:
        Segment of program containing the tokens and regular expressions
        
        Must contain variables "reserved" and "tokens", where:
            type(reserved) -> list(str(phrase))
            type(tokens) -> list(tuple(str(id), str(regex))
```

### Regular Expressions


The following regular expressions supported by default in LexMe:
```regexp
digit:
 [0-9]
nonzero:
 [1-9]
letter:
 [a-zA-Z]
alphanum:
 [0-9A-Za-z_]
 [{digit}{letter}_]
character:
 [0-9a-zA-Z_ ]
 [{alphanum}_]
id: 
 [a-zA-Z][0-9a-zA-Z_]*
 {letter}{alphanum}* 
intnum
 [1-9][0-9]* | 0
 ({nonzero}{digit}*)|0 
fraction 
 [.]([0-9]*[1-9] | 0) 
 [.]({digit}*nonzero | 0)
floatnum
 ([1-9][0-9]* | 0)([.]([0-9]*[1-9] | 0))(e[+-]?([1-9][0-9]* | 0))?
 {integer}{fraction}(e[+-]?{integer})?
stringlit
 "[0-9a-zA-Z_ ]*"
 "{character}*"
inline_comment:
 //.*
block_comment:
 /[*](?:.|\s)*?[*]/' 

```

### Finite State Machine

A lexical analyzer utilizing finite state machines would convert the previously mentioned regular expressions into their posix
notation and produce the corresponding minimum DFA in the automata library. The final finite state machine is a unification of all
sub finite state machines. The figures below show the DFA representations of the 'while' reserved word, the float, and the
entire lexical specification respectively. Other images may be viewed in the 'img' folder.

![](doc/assets/while.png "Minimum DFA representation of a reserved word 'while'" )


![](doc/assets/float.png "Minimum DFA representation of a float")


![](doc/assets/total.png "Minimum DFA representation of every token in the lexical specification")


The regular expressions for operators and reserved words have been omitted in this document since they are trivial.

### Design Details

The lex library contains the scanner and token structures. The former reads the input character by character once the contents
of the input file stream have been stored in a buffer. If a match is found, the scanner generates a token structure and yields
its execution until the next call.

Additionally, the scanner requires a config file to generate the logic for matching lexemes to tokens.
The file is assumed to be correct in structure and logic. It is then executed using a python exec() call. We note that the config
file is a fragment of a program, whose purpose is to allow customizations to the current specifications.

The follow figure shows the relation between each object:
![](doc/assets/design.png)


## Syntax Analyzer


### Configuration File

1. Run a text editor on `grammar.conf`:
```shell
vim grammar.conf
```

2. Add, edit, or remove entries into the file


```shell
Start -> Prog .
Prog -> NEW_Prog ClassList UNARY FuncDefList UNARY main FuncBody UNARY .

ClassList -> NEW_ClassList ClassList2 .
ClassList2 -> ClassDecl UNARY ClassList2
	| .
ClassDecl -> class PUSH id PUSH UNARY InheritList UNARY lcurbr MembList UNARY rcurbr semi .
```

### Command Line Arguments

The directories have been hard coded in the main function for testing purposes. A future version of the driver will be provided with this feature.

For now, use:

```shell
syntaxdriver.py
```

### Rules and Formats

The following rules are supported by default in LexMe:
```text
<START>        ::= <prog>
<prog>         ::= {{<classDecl>}} {{<funcDef>}} 'main' <funcBody>
<classDecl>    ::= 'class' 'id' [['inherits' 'id' {{',' 'id'}}]] '{' {{<visibility> <memberDecl>}} '}' ';'
<visibility>   ::= 'public' | 'private' | EPSILON
<memberDecl>   ::= <funcDecl> | <varDecl>  
<funcDecl>     ::= 'func' 'id' '(' <fParams> ')' ':' <type> ';' 
                |  'func' 'id' '(' <fParams> ')' ':' 'void' ';' 
<funcHead>     ::= 'func' [['id' 'sr']] 'id' '(' <fParams> ')' ':' <type> 
                |  'func' [['id' 'sr']] 'id' '(' <fParams> ')' ':' 'void'
<funcDef>      ::= <funcHead> <funcBody> 
<funcBody>     ::= [[ 'var' '{' {{<varDecl>}} '}' ]] {{<statement>}}
<varDecl>      ::= <type> 'id' {{<arraySize>}} ';'
<statement>    ::= <assignStat> ';'
                |  'if'     '(' <relExpr> ')' 'then' <statBlock> 'else' <statBlock> ';'
                |  'while'  '(' <relExpr> ')' <statBlock> ';'
                |  'read'   '(' <variable> ')' ';'
                |  'write'  '(' <expr> ')' ';'
                |  'return' '(' <expr> ')' ';'
                |  'break' ';'
                |  'continue' '; '
                |  <functionCall> ';'
<assignStat>   ::= <variable> <assignOp> <expr>
<statBlock>    ::= '{' {{<statement>}} '}' | <statement> | EPSILON  
<expr>         ::= <arithExpr> | <relExpr>
<relExpr>      ::= <arithExpr> <relOp> <arithExpr>
<arithExpr>    ::= <arithExpr> <addOp> <term> | <term> 
<sign>         ::= '+' | '-'
<term>         ::= <term> <multOp> <factor> | <factor>
<factor>       ::= <variable>
                |  <functionCall>
                |  'intLit' | 'floatLit' | 'stringLit' 
                |  '(' <arithExpr> ')'
                |  'not' <factor>
                |  <sign> <factor>
                |  'qm' '[' <expr> ':' <expr> ':' <expr> ']' 
<variable>     ::= {{<idnest>}} 'id' {{<indice>}}
<functionCall> ::= {{<idnest>}} 'id' '(' <aParams> ')'
<idnest>       ::= 'id' {{<indice>}} '.'
                |  'id' '(' <aParams> ')' '.'
<indice>       ::= '[' <arithExpr> ']'
<arraySize>    ::= '[' 'intNum' ']' | '[' ']'
<type>         ::= 'integer' | 'float' | 'string' | 'id'
<fParams>      ::= <type> 'id' {{<arraySize>}} {{<fParamsTail>}} | EPSILON  
<aParams>      ::= <expr> {{<aParamsTail>}} | EPSILON 
<fParamsTail>  ::= ',' <type> 'id' {{<arraySize>}}
<aParamsTail>  ::= ',' <expr>
<assignOp>     ::= '='
<relOp>        ::= 'eq' | 'neq' | 'lt' | 'gt' | 'leq' | 'geq' 
<addOp>        ::= '+' | '-'
<multOp>       ::= '*' | '/'
```

### Abstract Syntax Tree (AST)

The syntax library contains operators which are defined within the library itself. The user can simply edit the order of the operators in
```_config/grammar.conf``` if they wish to change the behavior of the program for the production of the abstract syntax tree. Some operators include:

1. **PUSH**: Creates a node labelled by the previous terminal and pushes it onto the stack:
```shell
Type -> integer PUSH
	| float PUSH
	| string PUSH
	| id PUSH .
```

2. **UNARY**: Pops two nodes from the stack and makes the second popped node the parent of the other. Pushes it back onto the stack:
```shell
Factor -> not PUSH Factor UNARY .
```

3. **BIN**: Pops three nodes from the stack and makes the middle node the parent of the others. Pushes it back onto the stack:
```shell
Example -> 1 PUSH assign PUSH 2 PUSH BIN .
```

4. **NOP**: Pushes an ε (epsilon) labelled node onto the stack:
```shell
Intnum -> intnum PUSH
	| NOP .
```

5. **NEW_X**: Pushes a new node labelled 'X' onto the stack:
```shell
ClassList -> NEW_ClassList ClassList2 .
```

6. **CHK**: If the node at the top of the stack has no children, re-labels the node as ε (epsilon):
```shell
DimList -> NEW_DimList DimList2 CHK .
```

Using the default rules in the grammar configuration file, we can construct a tree for a non-erroneous versions of ```examples/polynomial.src``` and
```examples/bubblesort.src```: 

![](doc/syntax/polynomial.png)

![](doc/syntax/bubblesort.png)

### Design Details

The syntax library uses objects defined in the scanner library to produce an abstract tree. It relies on the rules defined in
the configuration file (see ```/_config/grammar.conf```). The parsing table from the grammar is either constructed during run-time
or loaded from disk. This decision is made by comparing the modification times of the configuration file and the compressed table files.
If the modification time is later, then the compressed table files must be updated. A query is sent to Ucalgary's website containing the grammar
as the payload. The response is then parsed using Pandas and the table is stored locally for future use. When modifying the grammar, it is important to note
that the modifications must adhere to the rules defined by the Ucalgary online tool (otherwise it will result in errors).

The parser object generates an abstract syntax tree only if such a tree can be constructed from the stack. Otherwise, the tree is simply
empty.  


![](doc/syntax/design.png)


## Tools

### Automata (PyPi)

The [Automata](https://github.com/caleb531/automata) library contains datastructures and logic for converting NFAs to DFAs using Thompson's Construction Algorithm and
Rabin-Scott's Powerset Algorithm. A newer version of automata adds the ability to render the finite automata using PyDot.

### re

Python's well-developed [re](https://docs.python.org/3/library/re.html) library provides the capabilities to construct and customize tokens from regular expressions
and output the results for each character that is read. The lex library implemented in this project leverages the features present
in the re library to implement a simple parser and tokenizer.

### Shunting Algorithm

The [shunting](https://en.wikipedia.org/wiki/Shunting-yard_algorithm) algorithm, although not necessarily a tool, was very useful throughout the project as it was used to convert
regular expressions into their posix notation during the construction of the finite automata.

### UCalgary

[Ucalgary's](https://smlweb.cpsc.ucalgary.ca/) grammar tool was used to verify that the generated grammar in `grammar.conf` fulfilled LL1 conditions.

### AtoCC

The [AtoCC](http://www.atocc.de/cgi-bin/atocc/site.cgi?lang=de&site=main) software was used to test and validate that the grammar defined in `grammar.conf` was outputting the proper results.


## Contributors

[Rani Rafid](github.com/ra-ni) - 26975852
