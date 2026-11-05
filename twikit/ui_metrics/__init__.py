import re

from .dom import MockDocument

FUNCTION_PATTERN = re.compile(r'function [a-zA-Z]+\(\) ({.+})')
EQUAL_PATTERN = re.compile(r'(![a-zA-Z]{5}\|\|[a-zA-Z]{5})==([a-zA-Z]{5})')


def solve_ui_metrics(ui_metrics: str) -> str:
    try:
        import js2py_
    except ImportError:
        raise ImportError(
            'js2py_ is required for ui_metrics but not installed. '
            'This is only needed for the obfuscated login flow; '
            'cookie-based auth does not require it.'
        )
    match = FUNCTION_PATTERN.search(ui_metrics)
    if not match:
        raise ValueError('No function pattern found in ui_metrics input')
    inner_function = match.group(1)
    inner_function = EQUAL_PATTERN.sub(r'\1===\2', inner_function)
    context = js2py_.EvalJs()
    context.document = MockDocument()
    function = 'function main()' + inner_function
    context.eval(function)
    return str(context.main()).replace('\'', '"')
