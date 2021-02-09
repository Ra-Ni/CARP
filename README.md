https://smlweb.cpsc.ucalgary.ca/start.html

## Regular Expressions

The following regular expressions supported by the lex library:
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
notation and produce, in part, the following results:

![test](img/while.png "Minimum DFA representation of a reserved word 'while'" )


![](img/float.png "Test")


![](img/total.png)
## Design Details

The lex library contains the scanner and token structures. The former reads the input character by character once the contents
of the input file stream have been stored in a buffer. If a match is found, the scanner generates a token structure and yields
its execution until the next call.

Additionally, the scanner requires a config file to generate the logic for matching lexemes to tokens.
The file is assumed to be correct in structure and logic. It is then executed using a python exec() call.


## Tool Usage

### Automata (PyPi)

The Automata library contains datastructures and logic for converting NFAs to DFAs using Thompson's Construction Algorithm and
Rabin-Scott's Powerset Algorithm. A newer version of automata adds the ability to render the finite automata using PyDot.

### re

Python's well-developed re library provides the capabilities to construct and customize tokens from regular expressions
and output the results for each character that is read. The lex library implemented in this project leverages the features present
in the re library to implement a simple parser and tokenizer.

### Shunting Algorithm

The shunting algorithm, although not necessarily a tool, was very useful throughout the project as it was used to convert
regular expressions into their posix notation during the construction of the finite automata.


