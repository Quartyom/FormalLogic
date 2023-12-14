# > стрелка
# () скобки
# ! галка
# / турникет
# , перечисление
# v дизъюнкция
# ^ конъюнкция

import time
import qu_print


def is_symbol_letter(letter: str):
    if len(letter) != 1:
        return False
    if ord("A") <= ord(letter) <= ord("Z"):
        return True
    if ord("a") <= ord(letter) <= ord("z") and letter != "v":
        return True
    return False


def is_in_brackets(expr: str):
    if "(" not in expr:     # obvious case
        return False
    brackets = 0            # opened brackets - closed brackets
    global_separators = 0   # () > () > () -> 2 global_separators
    for char in expr:
        if char == "(":
            brackets += 1
        elif char == ")":
            brackets -= 1
        elif char in ">v^" and brackets == 0:     # this case () > ()
            global_separators += 1

    if brackets == 0 and global_separators == 0:    # all opened brackets matched to closed and
        return True


def absolute_expr(expr: str):   # !(!(A>B)) -> A>B, is_inverted: False
    if not expr:            # basic case for no expression
        return "", False

    is_inverted = False
    while is_in_brackets(expr):     # !(something) or (something) -> something, inversion
        if expr[0] == "!":
            is_inverted = not is_inverted
            expr = expr[1:]     # bcs of case like !!!() we can't remove the last symbol and two first
        else:
            expr = expr[1: len(expr) - 1]

    if ">" in expr or "v" in expr or "^" in expr:
        return expr, is_inverted

    else:     # !!!A -> A, inversion
        if not expr:                # case for invalid input when brackets resolve to nothing
            return "", is_inverted
        if expr.count("!") % 2 == 0:
            return expr.replace("!", ""), is_inverted
        else:
            return expr.replace("!", ""), not is_inverted


def is_expr_letter(expr: str):
    return is_symbol_letter(absolute_expr(expr)[0])


def simplify(expr: str):     # !!(!(A>B)) -> !(A>B)
    if not expr:        # basic case for no expression
        return expr
    expr, is_inverted = absolute_expr(expr)
    if is_inverted:
        if len(expr) > 1:     # for complex expressions
            expr = "!(" + expr + ")"
        else:                   # for letters
            expr = "!" + expr
    return expr


def invert_and_simplify(expr: str):
    if not expr:
        return ""
    return simplify("!(" + expr + ")")


def split_expr(expr: str, show_separator=False):  # (A>B)>C  ->  (A>B) and C   (and ">")
    expr = simplify(expr)
    while True:
        brackets = 0
        for i, char in enumerate(expr):     # to find () > ()
            if char == "(":
                brackets += 1
            elif char == ")":
                brackets -= 1
            elif char in ">v^" and brackets == 0:
                if show_separator:
                    return expr[:i], expr[i + 1:], char
                else:
                    return expr[:i], expr[i + 1:]
        else:
            if show_separator:
                return expr, None, char
            else:
                return expr, None  # not splitable


def split_statement(statement: str):    # A>B/C -> A>B and C
    return statement.split("/")


def split_args(args):   # "A,B,C" -> [A, B, C]
    if not args:    # "" -> []
        return []
    else:       # because "".split(",") = ['']
        return args.split(",")


def join_args(args):    # [A, B, C] -> "A,B,C"
    return ",".join(args)


def _compare(expr: str, src: str, cmp_dict):
    if not expr:
        return not src  # if expr empty, src must be also empty
    if not src:
        return not expr # the same logic

    expr = simplify(expr)
    src = simplify(src)

    left_expr, right_expr = split_expr(expr)
    left_src, right_src = split_expr(src)

    if not right_expr and right_src:    # expr: M, src: !C>D
        return False

    if not right_src:
        abs_expr, is_expr_inverted = absolute_expr(expr)
        abs_src, is_src_inverted = absolute_expr(src)

        if len(abs_src) > 1:
            if is_expr_inverted != is_src_inverted:     # expr: !(A>B), src: (C>D)
                return False
            else:
                return _compare(abs_expr, abs_src, cmp_dict)

        else:   # expr: (C>D), src: !M
            if abs_src in cmp_dict:
                if is_expr_inverted == is_src_inverted:   # key to value
                    if cmp_dict[abs_src] != simplify(abs_expr):
                        return False
                else:
                    if cmp_dict[abs_src] != invert_and_simplify(abs_expr):    # key to !value
                        return False
                return True

            else:
                if is_expr_inverted == is_src_inverted:  # key to value
                    cmp_dict[abs_src] = simplify(abs_expr)
                else:
                    cmp_dict[abs_src] = invert_and_simplify(abs_expr)  # key to !value
                return True

    return _compare(left_expr, left_src, cmp_dict) and _compare(right_expr, right_src, cmp_dict)


def compare(expr: str, src: str):   # (X>Y)>(Z>(X>Y)) equals A>(B>A)
    cmp_dict = dict()
    result = _compare(expr, src, cmp_dict)
    return result, cmp_dict


def modus_ponens(expr1, expr2):     # A, A>B -> B
    expr1_left, expr1_right = split_expr(expr1)
    expr2_left, expr2_right = split_expr(expr2)

    if simplify(expr1) == simplify(expr2_left):
        return expr2_right
    elif simplify(expr2) == simplify(expr1_left):
        return expr1_right
    else:
        return None


def is_modus_ponens(expr1, expr2, conclusion):  # A, A>B, B -> True
    mp_result = modus_ponens(expr1, expr2)
    if not mp_result:
        return False
    return simplify(mp_result) == simplify(conclusion)


def theorem1(conclusion):   # /F>F -> True
    return compare(conclusion, "A>A")[0]


def theorem6(arg1, arg2, conclusion):   # A>B,B>C/A>C
    if ">" in arg1 and ">" in arg2 and ">" in conclusion:

        arg1_left, arg1_right = split_expr(arg1)
        arg2_left, arg2_right = split_expr(arg2)
        conclusion_left, conclusion_right = split_expr(conclusion)

        if simplify(arg1_right) == simplify(arg2_left):     # A>B, B>C / A>C
            if simplify(arg1_left) == simplify(conclusion_left):
                if simplify(arg2_right) == simplify(conclusion_right):
                    return True
        if simplify(arg1_left) == simplify(arg2_right):     # B>C, A>B / A>C
            if simplify(arg2_left) == simplify(conclusion_left):
                if simplify(arg1_right) == simplify(conclusion_right):
                    return True

    return False


def theorem6_forward(arg1, arg2):   # A>B, B>C -> A>C
    arg1_left, arg1_right = split_expr(arg1)
    arg2_left, arg2_right = split_expr(arg2)

    if arg1_right and arg2_right:
        if simplify(arg1_right) == simplify(arg2_left):     # A>B, B>C / A>C
            if is_expr_letter(arg1_left) or is_in_brackets(arg1_left):
                added_left = arg1_left
            else:
                added_left = "(" + arg1_left + ")"
            if is_expr_letter(arg2_right) or is_in_brackets(arg2_right):
                added_right = arg2_right
            else:
                added_right = "(" + arg2_right + ")"
            return added_left + ">" + added_right

        if simplify(arg1_left) == simplify(arg2_right):     # B>C, A>B / A>C
            if is_expr_letter(arg2_left) or is_in_brackets(arg2_left):
                added_left = arg2_left
            else:
                added_left = "(" + arg2_left + ")"
            if is_expr_letter(arg1_right) or is_in_brackets(arg1_right):
                added_right = arg1_right
            else:
                added_right = "(" + arg1_right + ")"
            return added_left + ">" + added_right
    return None


def theorem7(arg1, arg2):       # A,!A / everything
    return simplify(arg1) == invert_and_simplify(arg2)


def theorem11(arg, conclusion):     # A>B = !B>!A
    arg_left, arg_right = split_expr(arg)
    conclusion_left, conclusion_right = split_expr(conclusion)

    if simplify(arg_left) == invert_and_simplify(conclusion_right):
        if simplify(arg_right) == invert_and_simplify(conclusion_left):
            return True
    return False


def theorem15(arg, conclusion):      # F=F -> True
    return simplify(arg) == simplify(conclusion)


def anti_theorem16(arg):    # A,B -> A^B    (reversed rule for guesser)
    result, cmp_dict = compare(arg, "!(A>!B)")   # = A^B
    if result:
        left_expr, right_expr = split_expr(invert_and_simplify(arg))
        return left_expr, invert_and_simplify(right_expr)
    return None, None


def guesser_rtl(statement: str):        # /A>B -> A/B
    args, conclusion = split_statement(statement)
    conclusion_left, conclusion_right = split_expr(conclusion)

    if conclusion_right:     # /A>B -> A/B
        result = simplify(conclusion_left) + "/" + simplify(conclusion_right)
        # theorem_type = 1
        description = f"Theorem 5 if {result} then /{conclusion}"

    elif conclusion_left:   # /A -> !A/
        result = invert_and_simplify(conclusion_left) + "/"
        # theorem_type = 2
        description = f"Theorem 9 if {result} then /{conclusion_left}"
    else:
        return False, None

    if args:
        result = args + "," + result
    return result, description # theorem_type


def guesser_ltr(statement: str):        # A/B -> /A>B
    args, conclusion = split_statement(statement)
    args = split_args(args)

    statements = list()
    descriptions = list()

    for i in range(len(args)):      # sort through all the combinations of args
        new_args = list(args)
        del new_args[i]
        new_args_str = join_args(new_args)

        if conclusion:      # A/B -> /A>B
            added_arg = args[i] if is_expr_letter(args[i]) else "(" + args[i] + ")"     # to simplify redundant brackets
            added_conclusion = conclusion if is_expr_letter(conclusion) else "(" + conclusion + ")"
            new_statement = new_args_str + "/" + added_arg + ">" + added_conclusion
            statements.append(new_statement)
            descriptions.append(f"Theorem 3 if /{added_arg}>{added_conclusion} then {added_arg}/{added_conclusion}")

        else:               # A/ - > /!A
            inverted_arg_i = invert_and_simplify(args[i])
            new_statement = new_args_str + "/" + inverted_arg_i
            statements.append(new_statement)
            descriptions.append(f"Theorem 8 if /{inverted_arg_i} then {args[i]}/")
    return statements, descriptions


def derive_formulas(statement: str, derived_args):    # args/something -> args,something/conclusion
    args, conclusion = split_statement(statement)
    args = split_args(args)

    statements = list()
    derived = list()
    descriptions = list()

    if len(args) > 1:   # two args theorems
        i = 0
        while i < len(args):
            k = i + 1
            while k < len(args):
                result = theorem6_forward(args[i], args[k])
                if result and result not in args and result not in derived_args:
                    statements.append(result + "," + statement)
                    derived.append(result)
                    descriptions.append(f"Removed derived argument {result}, Theorem 6 {args[i]},{args[k]}/{result}")
                result = modus_ponens(args[i], args[k])
                if result and result not in args and result not in derived_args:
                    statements.append(result + "," + statement)
                    derived.append(result)
                    descriptions.append(f"Removed derived argument {result}, Modus ponens {args[i]},{args[k]}/{result}")
                k += 1
            i += 1

    return statements, derived, descriptions


def split_conclusion(statement):    # A,B/C^D -> A,B/C and A,B/D
    args, conclusion = split_statement(statement)

    result, cmp_dict = compare(conclusion, "!(A>!B)")  # = A^B
    if result:
        left_conclusion, right_conclusion = split_expr(invert_and_simplify(conclusion))
        left_statement = args + "/" + left_conclusion
        right_statement = args + "/" + invert_and_simplify(right_conclusion)
        return left_statement, right_statement
    return None, None


def is_solved(statement: str):
    args, conclusion = split_statement(statement)
    args = split_args(args)

    axioms = ["A>(B>A)",
              "(A>(B>C))>((A>B)>(A>C))",
              "(!B>!A)>((!B>A)>B)"]

    theorems12_14 = ["!A>(A>B)",
                     "A>(!B>!(A>B))",
                     "(A>B)>((!A>B)>B)"]

    for i, axiom in enumerate(axioms, 1):
        result, cmp_dict = compare(conclusion, axiom)
        if result:
            return True, f"Axiom {i}:\t" + axiom + "\n" + str(cmp_dict)

    if theorem1(conclusion):
        return True, f"Theorem 1: /{conclusion}"

    for arg in args:        # one arg theorems
        if theorem15(arg, conclusion):
            return True, f"Theorem 15: {arg}={conclusion}"
        if theorem11(arg, conclusion):
            return True, f"Theorem 11: {arg}={conclusion}"

    for i, theorem in enumerate(theorems12_14, 12):     # no args theorems
        result, cmp_dict = compare(conclusion, theorem)
        if result:
            return True, f"Theorem {i}:\t" + theorem + "\n" + str(cmp_dict)

    if len(args) > 1:   # two args theorems
        i = 0
        while i < len(args):
            k = i + 1
            while k < len(args):
                if is_modus_ponens(args[i], args[k], conclusion):
                    return True, f"Modus ponens: {args[i]},{args[k]}/{conclusion}"
                elif theorem6(args[i], args[k], conclusion):
                    return True, f"Theorem 6: {args[i]},{args[k]}/{conclusion}"
                elif theorem7(args[i], args[k]):
                    return True, f"Theorem 7: {args[i]},{args[k]}/{conclusion}"

                k += 1
            i += 1

    return False, None


def check_state(state: str, states):    # to solve forward only
    args, conclusion = split_statement(state)
    sorted_args = join_args(sorted(split_args(args)))  # unifies args order
    state = sorted_args + "/" + conclusion

    if state in states:
        return False
    else:
        states.add(state)
        return True


# calls moving theorems backwards in a recursion
# on each step analyses the statement by means of checking theorems, modus ponens and axioms in is_solved()
# if solution is found, traces the steps back and prints the solution in the valid order
# else it's unsolvable
# if recursion depths is exceeded, the exception is caught in solve function


def _solve(statement: str, states, timeout, derived_args):
    if not is_statement_tautology(statement):
        return False, None
    if time.time_ns() > timeout:
        return False, "The solution takes too much time"
    result, description = is_solved(statement)
    if description:
        return result, description
    else:
        # Derived theorems
        new_statements, derived, guesser_descriptions = derive_formulas(statement, derived_args)
        for i, new_statement in enumerate(new_statements):
            if check_state(new_statement, states):
                # change
                result, description = _solve(new_statement, states, timeout, set(derived_args) | {derived[i]})
                if result:
                    to_print = f"{description}\n{new_statement}\n"
                    return True, to_print + guesser_descriptions[i]

        # Theorem if /A then /B>A
        args, conclusion = split_statement(statement)
        conclusion_left, conclusion_right = split_expr(conclusion)
        if conclusion_right:
            new_statement = args + "/" + simplify(conclusion_right)
            if check_state(new_statement, states):
                result, description = _solve(new_statement, states, timeout, derived_args)
                if result:
                    to_print = f"{description}\n{new_statement}\n"
                    return True, to_print + f"Theorem 4 if /{conclusion_right} then /{conclusion_left}>{conclusion_right}"

        # Theorem A^B/C -> A,B/C
        args_list = split_args(args)
        for i, arg in enumerate(args_list):
            left_arg, right_arg = anti_theorem16(arg)
            if left_arg and right_arg:
                new_args = args_list[:i] + [left_arg, right_arg] + args_list[i + 1:]
                new_args = join_args(new_args)
                new_statement = new_args + "/" + conclusion
                if check_state(new_statement, states):
                    result, description = _solve(new_statement, states, timeout, derived_args)
                    if result:
                        to_print = f"{description}\n{new_statement}\n"
                        return True, to_print + f"Theorem 16 if {left_arg},{right_arg}/{conclusion} " \
                                                f"then {left_arg}^{right_arg}/{conclusion} which is {arg}/{conclusion}"

        # Theorem A/B == /A>B
        new_statement, guesser_description = guesser_rtl(statement)
        if new_statement and check_state(new_statement, states):
            result, description = _solve(new_statement, states, timeout, derived_args)
            if result:
                to_print = f"{description}\n{new_statement}\n"
                return True, to_print + guesser_description

        # Theorem /A>B == A/B
        new_statements, guesser_descriptions = guesser_ltr(statement)
        for i, new_statement in enumerate(new_statements):
            if check_state(new_statement, states):
                result, description = _solve(new_statement, states, timeout, derived_args)
                if result:
                    to_print = f"{description}\n{new_statement}\n"
                    return True, to_print + guesser_descriptions[i]

        # Theorem if /A and /B then /A^B
        left_statement, right_statement = split_conclusion(statement)
        if left_statement and right_statement:
            if check_state(left_statement, states) and check_state(right_statement, states):
                left_result, left_description = _solve(left_statement, states, timeout, derived_args)
                if left_result:
                    right_result, right_description = _solve(right_statement, states, timeout, derived_args)
                    if right_result:
                        to_print = f"{left_description}\n{left_statement}\n{right_description}\n{right_statement}\n"
                        return True, to_print + f"Theorem if /A and /B then A^B which is " \
                                                f"{left_statement} and {right_statement} then {statement}"

        return False, None


def solve(statement: str):  # calls hidden solve function with valid input, analyses output
    if not validate_statement(statement):
        # print("invalid statement, syntax error")
        qu_print.add("invalid statement, syntax error")
    else:                                   # finally solve
        states = {statement}    # each state is a solution step, they must be all unique in solution
        derived_args = set()

        if not is_statement_tautology(statement):
            # print("Unsolvable statement")
            qu_print.add("Unsolvable statement")
        else:
            try:
                timeout = time.time_ns() + 100 * 10**9
                result, description = _solve(statement, states, timeout, derived_args)
                if result or description:
                    # print(description)
                    qu_print.add(description)
                    # print(statement)
                    qu_print.add(statement)
                    return

            except RecursionError:
                # print("The solution takes too many steps")
                qu_print.add("The solution takes too many steps")
                return

            # print("Tautology, but it can't solve it by theorems")
            qu_print.add("Tautology, but it can't solve it by theorems")


def solve_equation(equation: str):
    if not validate_equation(equation):
        # print("invalid equation, syntax error")
        qu_print.add("invalid equation, syntax error")
        return

    eq_left, eq_right = equation.split("=")

    if theorem15(eq_left, eq_right):        # check theorems
        # print(f"Theorem 1: {eq_left}={eq_right}")
        qu_print.add(f"Theorem 1: {eq_left}={eq_right}")
    elif theorem11(eq_left, eq_right):
        # print(f"Theorem 11: {eq_left}={eq_right}")
        qu_print.add(f"Theorem 11: {eq_left}={eq_right}")

    else:                                   # solve A/B and B/A
        statement1 = eq_left + "/" + eq_right
        # print(f"Step 1: prove {statement1}")
        qu_print.add(f"Step 1: prove {statement1}")
        solve(statement1)
        statement2 = eq_right + "/" + eq_left
        # print()
        qu_print.add("")
        # print(f"Step 2: prove {statement2}")
        qu_print.add(f"Step 2: prove {statement2}")
        solve(statement2)


def validate_expression(expr: str, called_inside=False):
    if not expr:        # base case
        return True

    if ">" not in expr:     # primitive function case
        return is_expr_letter(expr)

    if called_inside:     # all inner expressions must be in brackets
        if not is_in_brackets(expr):
            return False

    expr_left, expr_right = split_expr(absolute_expr(expr)[0])  # resolve outer brackets and inversion

    if not expr_left or not expr_right:  # cases "A>" ">" ">A"
        return False

    return validate_expression(expr_left, True) and validate_expression(expr_right, True)   # validate both sides


def validate_statement(statement: str):
    args, conclusion = split_statement(statement)
    if not conclusion:
        return False
    args = split_args(args)
    for arg in args:            # each argument and conclusion must be valid expressions
        if not validate_expression(arg):
            return False
    return validate_expression(conclusion)


def validate_equation(equation: str):
    args = equation.split("=")

    if len(args) == 2:
        return validate_expression(args[0]) and validate_expression(args[1])    # both sides must be valid expressions
    else:
        return False


def _transform_expr(expr: str):
    if "v" not in expr and "^" not in expr:     # base case
        return expr

    abs_expr, is_inverted = absolute_expr(expr)     # to resolve outer brackets and inversion
    left_expr, right_expr, char = split_expr(abs_expr, show_separator=True)     # split with separator
    if not right_expr:
        return expr

    left_expr = _transform_expr(left_expr)
    right_expr = _transform_expr(right_expr)

    if char == "v":     # AvB -> !A>B but complicated with brackets and inversion
        if is_expr_letter(left_expr) or is_in_brackets(left_expr):
            added_left = "!" + left_expr
        else:
            added_left = "!(" + left_expr + ")"
        if is_expr_letter(right_expr) or is_in_brackets(right_expr):
            added_right = right_expr
        else:
            added_right = "(" + right_expr + ")"
        if is_inverted:
            return "!(" + added_left + ">" + added_right + ")"
        else:
            return added_left + ">" + added_right

    elif char == "^":   # A^B -> !(A>!B)
        if is_expr_letter(left_expr) or is_in_brackets(left_expr):
            added_left = left_expr
        else:
            added_left = "(" + left_expr + ")"
        if is_expr_letter(right_expr) or is_in_brackets(right_expr):
            added_right = "!" + right_expr
        else:
            added_right = "!(" + right_expr + ")"
        if is_inverted:
            return added_left + ">" + added_right
        else:
            return "!(" + added_left + ">" + added_right + ")"

    else:               # just join transformed parts
        return left_expr + ">" + right_expr


def transform_expr(expr: str):      # calls hidden transform function and analyses the result
    new_statement = _transform_expr(expr)
    if new_statement != expr:
        print(f"{expr} resolved by definition to {new_statement}")
    if "!!" in new_statement:
        new_statement = new_statement.replace("!!", "")
        print(f"simplified to {new_statement}")
    return new_statement


def transform_st(statement: str):
    args, conclusion = split_statement(statement)
    args = split_args(args)

    for i in range(len(args)):              # transforms each argument and then conclusion
        args[i] = transform_expr(args[i])

    return join_args(args) + "/" + transform_expr(conclusion)


def transform_eq(equation: str):
    args = equation.split("=")

    if len(args) == 2:
        return transform_expr(args[0]) + "=" + transform_expr(args[1])  # transforms each side of equation
    else:
        return equation     # or just leaves as is


def find_letters(expr: str):    # "A<B=C<A" -> {A,B,C}
    letters = set()
    for char in expr:
        if is_symbol_letter(char):
            letters.add(char)
    return letters


def replace_letters(expr, letters):     # A<B -> {0}<{1}
    for i, letter in enumerate(letters):
        expr = expr.replace(letter, "{"+str(i)+"}")     # making a template for formatting
    return expr


def iterate_through_expression(expr, values, i):
    if i >= len(values):    # base case when all the values are defined for a single state
        ex = expr.format(*values)
        return eval(ex)
    else:       # checks all the states of given expression to define if this is always true
        for x in 0, 1:
            values[i] = x
            if not iterate_through_expression(expr, values, i + 1):
                return False
        else:
            return True


def is_statement_tautology(statement: str):
    letters = find_letters(statement)
    statement = replace_letters(statement, letters)

    statement = statement.replace(">", "<=")
    statement = statement.replace("!", " 1- ")
    statement = statement.replace("v", " or ")      # this is not used
    statement = statement.replace("^", " and ")     # and this
    statement = statement.replace(",", " and ")

    args, conclusion = split_statement(statement)
    args = "1" if not args else f"({args})"
    conclusion = "0" if not conclusion else f"({conclusion})"
    statement = args + "<=" + conclusion

    values = [0 for item in letters]
    return iterate_through_expression(statement, values, 0)


def main():
    while True:
        statement = input(":").replace(" ", "")

        if "=" in statement:
            statement = transform_eq(statement)
            print(f"got: {statement}")
            solve_equation(statement)
        else:
            if "/" not in statement:  # add / if needed
                statement = "/" + statement
            statement = transform_st(statement)
            print(f"got: {statement}")
            solve(statement)

        print()     # for separation


# main()


def solve_input(statement):
    qu_print.clear()
    statement = statement.strip().replace(" ", "")

    if "=" in statement:
        statement = transform_eq(statement)
        # print(f"got: {statement}")
        qu_print.add(f"got: {statement}")
        solve_equation(statement)
    else:
        if "/" not in statement:  # add / if needed
            statement = "/" + statement
        statement = transform_st(statement)
        # print(f"got: {statement}")
        qu_print.add(f"got: {statement}")
        solve(statement)

    # print()  # for separation
    qu_print.add("")
    return qu_print.get_text()