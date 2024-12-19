def transform_operation(op1, op2):
    """
    Transform operation1 against operation2.
    Returns transformed operation1.
    """
    if op1['type'] == 'insert' and op2['type'] == 'insert':
        if op1['position'] <= op2['position']:
            return op1
        return {
            'type': 'insert',
            'position': op1['position'] + len(op2['text']),
            'text': op1['text']
        }
    # Add other transformation cases...
    return op1

def apply_operation(content, operation):
    """
    Apply operation to content and return new content.
    """
    if operation['type'] == 'insert':
        pos = operation['position']
        return content[:pos] + operation['text'] + content[pos:]
    elif operation['type'] == 'delete':
        start = operation['position']
        end = start + operation['length']
        return content[:start] + content[end:]
    return content
