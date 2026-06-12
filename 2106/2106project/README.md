# Discrete-Mathematics-Project
## Run Instructions

From the project root:

```bash
cd project_root
python logic_compiler.py <input_file> <output_file>
```

Example:

```bash
cd Discrete-Mathematics-Project
python logic_compiler.py program.txt compiler_trace.json
```

## Example Input

```plaintext
let p = T
let q = F
let r = (NOT ((NOT p) AND q))
if r then print p
```

## Output Format

On success, the JSON includes:

- `phase_1_lexer`
- `phase_2_parser`
- `phase_3_optimizer`
- `phase_4_execution`

On failure, the JSON includes phases that succeeded and an `error` object:

- `phase`: failing stage (`phase_1_lexer`, `phase_2_parser`, or `phase_4_execution`)
- `line`: source line number

