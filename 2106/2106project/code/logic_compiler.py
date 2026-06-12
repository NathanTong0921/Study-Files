import re
import sys
import json

# PHASE 1: LEXER
class LexerError(Exception):
    # Raised when the lexer encounters an error, including line number where a failure occurs
    def __init__(self, message, line_num = None):
        super().__init__(message)
        self.line_num = line_num

    def __str__(self):
        if self.line_num is not None:
            return f"Lexical Error on line {self.line_num}: {super().__str__()}"
        return f"Lexical Error: {super().__str__()}"

class Lexer:
    def __init__(self):
        # Initialize the lexer with patterns for keywords, operators, symbols, variables, and whitespace
        self.KEYWORDS_BOOLEANS_OPERATORS = {
            'let': 'LET', 'if': 'IF', 'then': 'THEN', 'print': 'PRINT',
            'T': 'TRUE', 'F': 'FALSE',
            'AND': 'AND', 'OR': 'OR', 'NOT': 'NOT', 'IMPLIES': 'IMPLIES',
        }

        self.SYMBOLS = {
            '=': 'EQ',
            '(': 'L_PAREN',
            ')': 'R_PAREN'
        }

        # Construct regex patterns to identify different token classes
        keyword_pattern = r'\b(' + '|'.join(re.escape(k) for k in self.KEYWORDS_BOOLEANS_OPERATORS.keys()) + r')\b'
        symbol_pattern = '|'.join(re.escape(s) for s in sorted(self.SYMBOLS.keys(), key=len, reverse=True))
        variable_pattern = r'\b[a-z]\b' 
        whitespace_pattern = r'\s+'
        unknown_pattern = r'.'

        # Compile a single regex that prioritizes matching in order
        self.token_regex = re.compile(
            rf'(?P<KEYWORD>{keyword_pattern})|'
            rf'(?P<SYMBOL>{symbol_pattern})|'
            rf'(?P<VARIABLE>{variable_pattern})|'
            rf'(?P<WHITESPACE>{whitespace_pattern})|'
            rf'(?P<UNKNOWN>{unknown_pattern})'
        )
    
    def tokenize(self, source_lines):
        # Scan the source code line by line and translate strings into flat token lists
        all_tokens_by_line = []
        for line_num, line_content in enumerate(source_lines, 1):
            line_tokens = []
            pos = 0 
            
            # Iterate through the characters of the current line
            while pos < len(line_content):
                match = self.token_regex.match(line_content, pos)
                
                if not match:
                    raise LexerError(
                        f"Unexpected character '{line_content[pos]}' at column {pos + 1}.",
                        line_num,
                    )
                
                lexeme = match.group(0)
                pos = match.end()
                
                # Route the matched substring to the appropriate token category
                if match.group('WHITESPACE'):
                    continue
                elif match.group('KEYWORD'):
                    line_tokens.append(self.KEYWORDS_BOOLEANS_OPERATORS[lexeme])
                elif match.group('SYMBOL'):
                    line_tokens.append(self.SYMBOLS[lexeme])
                elif match.group('VARIABLE'):
                    line_tokens.append(f"VAR_{lexeme.upper()}")
                elif match.group('UNKNOWN'):
                    raise LexerError(
                        f"Unrecognized token '{lexeme}'.",
                        line_num,
                    )
                else:
                    raise LexerError(
                        f"Internal lexer error: unhandled match type for '{lexeme}'.",
                        line_num,
                    )
            
            if line_tokens:
                all_tokens_by_line.append({"line": line_num, "tokens": line_tokens})
        
        return all_tokens_by_line
    


# PHASE 2: PARSER
class ParserError(Exception):
    # Raised when the parser encounters a syntax error, including line number where a failure occurs
    def __init__(self, message, line_num = None):
        super().__init__(message)
        self.line_num = line_num

    def __str__(self):
        if self.line_num is not None:
            return f"Syntax Error on line {self.line_num}: {super().__str__()}"
        return f"Syntax Error: {super().__str__()}"

class Parser:
    def __init__(self):
        self.all_tokens_by_line = [] 
        self.current_line_tokens = [] 
        self.current_line_num = 0    
        self.pos = 0                  

    def parse(self, all_tokens_by_line_input):
        # Convert flat token lists into Abstract Syntax Trees (prefix notation)
        self.all_tokens_by_line = all_tokens_by_line_input
        parsed_statements = []
        for line_data in self.all_tokens_by_line:
            self.current_line_tokens = line_data['tokens']
            self.current_line_num = line_data['line']
            self.pos = 0 
            try:
                ast_for_line = self.parse_statement()
                # Ensure no dangling tokens exist after a complete statement is parsed
                if self.pos < len(self.current_line_tokens):
                    unexpected_token = self.current_token()
                    raise ParserError(f"Unexpected token '{unexpected_token}' after statement. "
                                      f"Check for missing operators or malformed expressions.", self.current_line_num)           
                parsed_statements.append({"line": self.current_line_num, "ast": ast_for_line})
            except ParserError as e:
                raise e 
        return parsed_statements

    def current_token(self):
        # Checks the current token without consuming it
        if self.pos < len(self.current_line_tokens):
            return self.current_line_tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        # Validate and advance the token pointer
        current_token = self.current_token()
        if current_token is None:
            raise ParserError(f"Unexpected end of input. Expected {expected_type if expected_type else 'a token'}.", self.current_line_num)

        if expected_type and current_token != expected_type:
            if expected_type == 'R_PAREN':
                raise ParserError("Mismatched parentheses: missing right parenthesis.", self.current_line_num)     
            raise ParserError(f"Expected '{expected_type}', found '{current_token}'.", self.current_line_num)
        
        self.pos += 1
        return current_token

    def parse_statement(self):
        # Route to specific statement parsers based on the starting keyword
        token_type = self.current_token()
        if token_type is None:
            raise ParserError("Unexpected end of input: expecting a statement.", self.current_line_num)

        if token_type == 'LET':
            return self.parse_let()
        if token_type == 'IF':
            return self.parse_if()
        if token_type == 'PRINT':
            return self.parse_print()

        raise ParserError(
            f"Invalid statement start '{token_type}'. A statement must begin with LET, IF, or PRINT.",
            self.current_line_num,
        )

    def parse_let(self):
        self.consume('LET')
        var_name_token = self.current_token()
        if var_name_token is None or not var_name_token.startswith('VAR_'):
            raise ParserError(f"Expected a variable name (e.g., VAR_P) after 'LET', found '{var_name_token}'.", self.current_line_num)
        var_name = self.consume()       
        self.consume('EQ')
        expr = self.parse_expression()
        return ['LET', var_name, expr]

    def parse_if(self):
        self.consume('IF')
        condition = self.parse_expression()
        self.consume('THEN')
        consequent = self.parse_statement() 
        return ['IF', condition, consequent]

    def parse_print(self):
        self.consume('PRINT') 
        var_to_print_token = self.current_token()
        if var_to_print_token is None or not var_to_print_token.startswith('VAR_'):
            raise ParserError(f"Expected a variable name (e.g., VAR_P) after 'PRINT', found '{var_to_print_token}'.", self.current_line_num)
        var_name = self.consume() 
        return ['PRINT', var_name]

    def parse_expression(self):
        # Recursively builds the prefix notation AST, completely removing parentheses
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input: missing expression or operand.", self.current_line_num)
        if token.startswith('VAR_') or token in {'TRUE', 'FALSE'}:
            return self.consume()
        if token != 'L_PAREN':
            raise ParserError(
                f"Expected an expression (variable, boolean, or parenthesized recursive expression), found '{token}'.",
                self.current_line_num,
            )
        self.consume('L_PAREN')
        if self.current_token() == 'NOT':
            self.consume('NOT')
            operand = self.parse_expression()
            self.consume('R_PAREN')
            return ['NOT', operand]     
        left = self.parse_expression()
        op = self.current_token()
        if op not in {'AND', 'OR', 'IMPLIES'}:
            raise ParserError(
                f"Expected a binary operator 'AND', 'OR', or 'IMPLIES' inside parentheses, found '{op}'.",
                self.current_line_num,
            )
        self.consume()
        right = self.parse_expression()
        self.consume('R_PAREN')
        # Returns prefix list structure, ensuring implicit order of operations
        return [op, left, right]
    


# PHASE 3: OPTIMIZER
class Optimizer:
    def optimize_expression(self, expr):
        # Return if it's a variable or boolean constant
        if isinstance(expr, str):
            return expr

        op = expr[0]
        if op == 'NOT':
            # Recursively optimize the inner operand first
            operand = self.optimize_expression(expr[1])

            # Double negation law
            if isinstance(operand, list) and operand and operand[0] == 'NOT':
                return self.optimize_expression(operand[1]) 
            
            # not true -> false, not false -> true
            if operand == 'TRUE':
                return 'FALSE'
            if operand == 'FALSE':
                return 'TRUE'

            # De Morgan's laws
            if isinstance(operand, list) and len(operand) == 3:
                inner_op = operand[0]
                left = operand[1]
                right = operand[2]

                if inner_op == 'AND':
                    return self.optimize_expression(['OR', ['NOT', left], ['NOT', right]])
                if inner_op == 'OR':
                    return self.optimize_expression(['AND', ['NOT', left], ['NOT', right]])
            
            return ['NOT', operand]

        else: # op in {'AND', 'OR', 'IMPLIES'}
            # Recursively optimize left and right subtrees for binary operators
            left = self.optimize_expression(expr[1])
            right = self.optimize_expression(expr[2])

            # Implication law
            if op == 'IMPLIES':
                return self.optimize_expression(['OR', ['NOT', left], right])

            if op == 'AND':
                if left == 'FALSE' or right == 'FALSE':
                    return 'FALSE' # Universal bound law
                if left == 'TRUE':
                    return right # Identity law
                if right == 'TRUE':
                    return left # Identity law
                if left == right:
                    return left # Idempotent law
                if left == ['NOT', right] or right == ['NOT', left]:
                    return 'FALSE' # Negation law
                # Absorption law
                if isinstance(right, list) and right[0] == 'OR':
                    if left == right[1] or left == right[2]:
                        return left
                if isinstance(left, list) and left[0] == 'OR':
                    if right == left[1] or right == left[2]:
                        return right
                return ['AND', left, right]

            if op == 'OR':
                if left == 'TRUE' or right == 'TRUE':
                    return 'TRUE' # Universal bound law
                if left == 'FALSE':
                    return right # Identity law
                if right == 'FALSE':
                    return left # Identity law
                if left == right:
                    return left # Idempotent law
                if left == ['NOT', right] or right == ['NOT', left]:
                    return 'TRUE' # Negation law
                # Absorption law
                if isinstance(right, list) and right[0] == 'AND':
                    if left == right[1] or left == right[2]:
                        return left
                if isinstance(left, list) and left[0] == 'AND':
                    if right == left[1] or right == left[2]:
                        return right
                return ['OR', left, right]

    def optimize_statement(self, ast):
        # Handle LET, IF, PRINT statements
        stmt_type = ast[0]
        if stmt_type == 'LET':
            return ['LET', ast[1], self.optimize_expression(ast[2])]
        if stmt_type == 'IF':
            return ['IF', self.optimize_expression(ast[1]), self.optimize_statement(ast[2])]
        if stmt_type == 'PRINT':
            return ['PRINT', ast[1]]

    def optimize(self, parsed_statements):
        optimized_statements = []
        for line in parsed_statements:
            optimized_ast = self.optimize_statement(line['ast'])
            optimized_statements.append({"line": line['line'], "ast": optimized_ast})
        return optimized_statements



# PHASE 4: VERIFICATION & EXECUTION
class ExecutorError(Exception):
    # Raised when the executor encounters an error during expression evaluation or statement execution, including line number where a failure occurs
    def __init__(self, message, line_num=None):
        super().__init__(message)
        self.line_num = line_num

    def __str__(self):
        if self.line_num is not None:
            return f"Executor Error on line {self.line_num}: {super().__str__()}"
        return f"Executor Error: {super().__str__()}"

class Executor:
    def collect_variables(self, expr):
        # Traverses the AST to extract a unique set of variables required for generating the truth tables
        if isinstance(expr, str):
            if expr.startswith('VAR_'):
                return {expr}
            return set()
        
        op = expr[0]
        if op == 'NOT':
            return self.collect_variables(expr[1])
        left_vars = self.collect_variables(expr[1])
        right_vars = self.collect_variables(expr[2])
        return left_vars.union(right_vars)
    
    def generate_truth_assignments(self, variables):
        # Recursively generates all 2^n possible truth value permutations
        sorted_vars = sorted(variables)
        if not sorted_vars:
            return [{}]

        first_var = sorted_vars[0]
        rest_vars = sorted_vars[1:]
        smaller_assignments = self.generate_truth_assignments(rest_vars)
        assignments = []
        for assignment in smaller_assignments:
            true_case = assignment.copy()
            true_case[first_var] = 'TRUE'
            assignments.append(true_case)

        for assignment in smaller_assignments:
            false_case = assignment.copy()
            false_case[first_var] = 'FALSE'
            assignments.append(false_case)
        return assignments

    def evaluate_expression(self, expr, state, line_num=None):
        # Recursively calculates the boolean value of an expression based on a given State Dictionary
        if isinstance(expr, str):
            if expr == 'TRUE' or expr == 'FALSE':
                return expr
            if expr.startswith('VAR_'):
                # If the variable is not defined in the current state, raise an executor error
                if expr not in state:
                    raise ExecutorError(f"Variable '{expr}' is not defined in the current state.", line_num)
                return state[expr]
        
        op = expr[0]
        if op == 'NOT':
            operand_value = self.evaluate_expression(expr[1], state, line_num)
            if operand_value == 'TRUE':
                return 'FALSE'
            return 'TRUE'
        left_value = self.evaluate_expression(expr[1], state, line_num)
        right_value = self.evaluate_expression(expr[2], state, line_num)
        if op == 'AND':
            if left_value == 'TRUE' and right_value == 'TRUE':
                return 'TRUE'
            return 'FALSE'
        if op == 'OR':
            if left_value == 'TRUE' or right_value == 'TRUE':
                return 'TRUE'
            return 'FALSE'
        if op == 'IMPLIES':
            if left_value == 'TRUE' and right_value == 'FALSE':
                return 'FALSE'
            return 'TRUE'
    
    def verify_equivalence(self, original_expr, optimized_expr, line_num):
        # Generates truth columns for both AST versions across all variable permutations
        variables = sorted(self.collect_variables(original_expr).union(self.collect_variables(optimized_expr)))
        assignments = self.generate_truth_assignments(variables)
        original_column = []
        optimized_column = []
        for state in assignments:
            original_column.append(self.evaluate_expression(original_expr, state, line_num))
            optimized_column.append(self.evaluate_expression(optimized_expr, state, line_num))

        return {
            'line': line_num,
            'variables_tested': variables,
            'ast_original_column': original_column,
            'ast_optimized_column': optimized_column,
            'is_equivalent': 'TRUE' if original_column == optimized_column else 'FALSE'
        }

    def execute_statement(self, ast, state, printed_output, line_num):
        # Line-by-line sequential execution mapping variables to truth values in the State Dictionary
        stmt_type = ast[0]
        if stmt_type == 'LET':
            var_name = ast[1]
            expr = ast[2]
            state[var_name] = self.evaluate_expression(expr, state, line_num)
            return
        if stmt_type == 'IF':
            condition = ast[1]
            consequent = ast[2]
            if self.evaluate_expression(condition, state, line_num) == 'TRUE':
                self.execute_statement(consequent, state, printed_output, line_num)
            return
        if stmt_type == 'PRINT':
            var_name = ast[1]
            # If the variable to print is not defined in the current state, raise an executor error
            if var_name not in state:
                raise ExecutorError(f"Variable '{var_name}' is not defined in the current state.", line_num)
            printed_output.append({'line': line_num, 'output': state[var_name]})
            return
        
    def collect_changed_expression_pairs(self, original_ast, optimized_ast, line_num):
        # Analyzes phase 2 and phase 3 outputs to isolate expressions that were modified for verification
        changed_pairs = []
        stmt_type = original_ast[0]
        if stmt_type == 'LET':
            original_expr = original_ast[2]
            optimized_expr = optimized_ast[2]
            if original_expr != optimized_expr:
                changed_pairs.append((original_expr, optimized_expr, line_num))
            return changed_pairs
        if stmt_type == 'IF':
            original_condition = original_ast[1]
            optimized_condition = optimized_ast[1]
            if original_condition != optimized_condition:
                changed_pairs.append((original_condition, optimized_condition, line_num))
            # Recursively check the consequent statements for changes as well
            original_consequent = original_ast[2]
            optimized_consequent = optimized_ast[2]
            changed_pairs.extend(self.collect_changed_expression_pairs(original_consequent, optimized_consequent, line_num))
            return changed_pairs
        if stmt_type == 'PRINT':
            return changed_pairs
        
    def verify_and_execute(self, phase_2, phase_3):
        verifications = []
        state = {} # State Dictionary
        printed_output = []

        # First verify every changed expression before executing any statement
        for original_line, optimized_line in zip(phase_2, phase_3):
            original_ast = original_line['ast']
            optimized_ast = optimized_line['ast']
            line_num = optimized_line['line']
            changed_pairs = self.collect_changed_expression_pairs(original_ast, optimized_ast, line_num)
            for original_expr, optimized_expr, expr_line_num in changed_pairs:
                verifications.append(self.verify_equivalence(original_expr, optimized_expr, expr_line_num))

        # Then execute the optimized program after verification is complete
        for optimized_line in phase_3:
            optimized_ast = optimized_line['ast']
            line_num = optimized_line['line']
            self.execute_statement(optimized_ast, state, printed_output, line_num)

        return {
            'verifications': verifications,
            'final_state_dictionary': state,
            'printed_output': printed_output
        }
        
        

def main():
    if len(sys.argv) != 3:
        print("Usage: python logic_compiler.py <input_file> <output_file>")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    lexer = Lexer()
    parser = Parser()
    optimizer = Optimizer()
    executor = Executor()

    pipeline_results = {}

    try:
        with open(input_filename, 'r') as file:
            source_lines = file.readlines()

        # Execute Pipeline Phases
        phase_1 = lexer.tokenize(source_lines)
        pipeline_results['phase_1_lexer'] = phase_1

        phase_2 = parser.parse(phase_1)
        pipeline_results['phase_2_parser'] = phase_2

        phase_3 = optimizer.optimize(phase_2)
        pipeline_results['phase_3_optimizer'] = phase_3

        phase_4 = executor.verify_and_execute(phase_2, phase_3)
        pipeline_results['phase_4_execution'] = phase_4

    # Graceful Error Catching
    except LexerError as e:
        pipeline_results['error'] = {
            'phase': 'phase_1_lexer',
            'line': e.line_num,
        }
    except ParserError as e:
        pipeline_results['error'] = {
            'phase': 'phase_2_parser',
            'line': e.line_num,
        }
    except ExecutorError as e:
        pipeline_results['error'] = {
            'phase': 'phase_4_execution',
            'line': e.line_num,
        }

    with open(output_filename, 'w') as out_file:
        json.dump(pipeline_results, out_file, indent=2)

if __name__ == "__main__":
    main()