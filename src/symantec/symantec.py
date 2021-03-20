"""
Symbol table contains entries for IDENTIFIERS (classes, variables, functions) defined in its OWN scope

CONCEPTS
    2 pass:
        before a free function is allowed to be bound to a member, it must be in the symbol table

        1.  construct the symbol table for that function
            you can't bind it if it's not built

        2.  use the information gathered by that symbol table
            this binds the free function to the member


SCOPES
    global: classes | variables | functions
        for functions, there must be one main function

    classes: data-types (user-defined) and member functions
        two pass if function refers to another class that is after it
        - Does a class have an inherits label?
            Yes:
                Does it have a circular dependency?
                    Yes:
                        Symantec error and don't go forward.
                    No:
                        Nothing

                Link the symbol table of the class that is 'inherited' to the current symbol table
                    This allows the current symbol table to access all entries within the inherited symbol table

                Does the current class have members that are the same as the class it inherited?
                *Def same: name and type (func or var)
                    - a warning should be reported in this case.

                    Yes:
                        Shadow the inherited class' member
                    No:
                        Nothing

            No:
                Construct symbol table



    function: member | free
        member: functions that are bound to a class
            - identified by their scope-resolution operator
            - Follow the logic:
                Does it exist already in the symbol table?
                    Yes:
                        Done
                    No:
                        2 Pass (build free, then bind but check the bounded scope) <- recursive 2 pass possible

        free: functions that are not bound to a class


OTHER
    - no need to check index out of bounds
    - members of different classes or functions can have the same names (they're obv in a different scope)
    - variables inside functions or classes are local (diff scope again)
        "This raises the need for a nested symbol table structure"
    - data members can be used in all member functions of their respective class
    - global table is always present
    - local symbol table created at the beginning of the processing of any function or class
    - "Make sure you can change the record structure with minimal changes to your symbol table manipulating functions."
    - Invalid to have operands of arithmetic operators to be of different types.
        For the same reason, both operands of an assignment must be of the same type.

"""
import pandas as pd

from syntax import AST

