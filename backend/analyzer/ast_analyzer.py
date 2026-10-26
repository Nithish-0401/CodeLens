import ast


def analyze_code(code: str):
    """
    Analyze Python source code using AST.
    """

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "valid_python": False,
            "syntax_error": {
                "line": e.lineno,
                "column": e.offset,
                "message": e.msg
            }
        }

    result = {
        "valid_python": True,
        "imports": [],
        "functions": [],
        "classes": [],
        "control_structures": [],
        "function_calls": []
    }

    for node in ast.walk(tree):

        # Imports
        if isinstance(node, ast.Import):
            for name in node.names:
                result["imports"].append(name.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module

            for name in node.names:
                result["imports"].append(
                    f"{module}.{name.name}"
                )

        # Functions
        elif isinstance(node, ast.FunctionDef):
            result["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "arguments": [
                    arg.arg for arg in node.args.args
                ]
            })

        # Classes
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({
                "name": node.name,
                "line": node.lineno
            })

        # Control structures
        elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
            result["control_structures"].append({
                "type": type(node).__name__,
                "line": node.lineno
            })

        # Function calls
        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                function_name = node.func.id

            elif isinstance(node.func, ast.Attribute):
                function_name = node.func.attr

            else:
                function_name = "unknown"

            result["function_calls"].append({
                "name": function_name,
                "line": node.lineno
            })

    return result