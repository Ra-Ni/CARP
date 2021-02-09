# LexMe

LexMe is a lexical analyzer that accepts any regular expressions in a config file and produces tokens by leveraging python's
re library. LexMe is simple and intuitive. While not as performant as other lexical analyzers (especially those that utilize a finite state machine table),
it does allow one to easily transform lexemes into tokens.

## Prerequisites

- Python 3.7+

## Configuration File

1. Run the editor for the config file included:
```shell
vim config
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
## Command Line Arguments

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

## Regular Expressions

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
The regular expressions for operators and reserved words have been omitted in this document since they are trivial.

## Finite State Machine

A lexical analyzer utilizing finite state machines would convert the previously mentioned regular expressions into their posix
notation and produce the corresponding minimum DFA in the automata library. The final finite state machine is a unification of all
sub finite state machines. The figures below show the DFA representations of the 'while' reserved word, the float, and the
entire lexical specification respectively. Other images may be viewed in the 'img' folder.

![](img/while.png "Minimum DFA representation of a reserved word 'while'" )


![](img/float.png "Minimum DFA representation of a float")


![](img/total.png "Minimum DFA representation of every token in the lexical specification")
## Design Details

The lex library contains the scanner and token structures. The former reads the input character by character once the contents
of the input file stream have been stored in a buffer. If a match is found, the scanner generates a token structure and yields
its execution until the next call.

Additionally, the scanner requires a config file to generate the logic for matching lexemes to tokens.
The file is assumed to be correct in structure and logic. It is then executed using a python exec() call. We note that the config
file is a fragment of a program, whose purpose is to allow customizations to the current specifications.

The follow figure shows the relation between each object:
![](img/design.png)

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


## Contributors

[Rani Rafid](github.com/ra-ni) - 26975852
