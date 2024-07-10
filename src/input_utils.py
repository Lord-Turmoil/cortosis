def get_multiline_input(prompt=None) -> str:
    """
    Get user input until Ctrl-D is pressed.
    """
    if prompt is not None:
        print(prompt)
    lines = []
    try:
        while True:
            lines.append(input())
    except EOFError:
        pass

    return "\n".join(lines)
