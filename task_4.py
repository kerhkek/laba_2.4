def serialize_json(obj, indent=0):
    space = ' ' * indent
    if obj is None:
        return 'null'
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
        return '"' + obj.replace('"', '\\"') + '"'
    elif isinstance(obj, list):
        items = [serialize_json(item, indent + 2) for item in obj]
        return '[\n' + ',\n'.join(space + '  ' + item for item in items) + '\n' + space + ']'
    elif isinstance(obj, dict):
        items = []
        for key, value in obj.items():
            key_str = '"' + str(key).replace('"', '\\"') + '"'
            val_str = serialize_json(value, indent + 2)
            items.append(space + '  ' + key_str + ': ' + val_str)
        return '{\n' + ',\n'.join(items) + '\n' + space + '}'
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


def deserialize_json(s):
    def skip_whitespace(s, index):
        while index < len(s) and s[index] in ' \t\n\r':
            index += 1
        return index

    def parse_value(s, index, line):
        index = skip_whitespace(s, index)
        if index >= len(s):
            raise ValueError(f"Unexpected end of JSON at line {line}")
        ch = s[index]
        if ch == '"':
            return parse_string(s, index, line)
        elif ch == '{':
            return parse_object(s, index, line)
        elif ch == '[':
            return parse_array(s, index, line)
        elif s.startswith('true', index):
            return True, index + 4
        elif s.startswith('false', index):
            return False, index + 5
        elif s.startswith('null', index):
            return None, index + 4
        elif ch in '-0123456789':
            return parse_number(s, index, line)
        else:
            raise ValueError(f"Invalid character '{ch}' at line {line}")

    def parse_string(s, index, line):
        if s[index] != '"':
            raise ValueError(f"Expected '\"' at line {line}")
        index += 1
        result = ''
        while index < len(s):
            ch = s[index]
            if ch == '"':
                return result, index + 1
            elif ch == '\\':
                index += 1
                if index >= len(s):
                    raise ValueError(f"Invalid escape at line {line}")
                esc_char = s[index]
                if esc_char == '"':
                    result += '"'
                elif esc_char == '\\':
                    result += '\\'
                elif esc_char == '/':
                    result += '/'
                elif esc_char == 'b':
                    result += '\b'
                elif esc_char == 'f':
                    result += '\f'
                elif esc_char == 'n':
                    result += '\n'
                elif esc_char == 'r':
                    result += '\r'
                elif esc_char == 't':
                    result += '\t'
                elif esc_char == 'u':
                    if index + 4 >= len(s):
                        raise ValueError(f"Invalid unicode escape at line {line}")
                    hex_str = s[index+1:index+5]
                    try:
                        result += chr(int(hex_str, 16))
                    except:
                        raise ValueError(f"Invalid unicode escape at line {line}")
                    index += 4
                else:
                    raise ValueError(f"Invalid escape character '{esc_char}' at line {line}")
            else:
                result += ch
            index += 1
        raise ValueError(f"Unterminated string at line {line}")

    def parse_number(s, index, line):
        start_idx = index
        num_str = ''
        if s[index] == '-':
            num_str += '-'
            index += 1
        while index < len(s) and s[index] in '0123456789':
            num_str += s[index]
            index += 1
        if index < len(s) and s[index] == '.':
            num_str += '.'
            index += 1
            while index < len(s) and s[index] in '0123456789':
                num_str += s[index]
                index += 1
        if index < len(s) and s[index] in 'eE':
            num_str += s[index]
            index += 1
            if index < len(s) and s[index] in '+-':
                num_str += s[index]
                index += 1
            while index < len(s) and s[index] in '0123456789':
                num_str += s[index]
                index += 1
        try:
            if '.' in num_str or 'e' in num_str or 'E' in num_str:
                return float(num_str), index
            else:
                return int(num_str), index
        except:
            raise ValueError(f"Invalid number at line {line}")

    def parse_array(s, index, line):
        if s[index] != '[':
            raise ValueError(f"Expected '[' at line {line}")
        index += 1
        array = []
        index = skip_whitespace(s, index)
        if index < len(s) and s[index] == ']':
            return array, index + 1
        while True:
            val, index = parse_value(s, index, line)
            array.append(val)
            index = skip_whitespace(s, index)
            if index >= len(s):
                raise ValueError(f"Unterminated array at line {line}")
            if s[index] == ']':
                return array, index + 1
            elif s[index] == ',':
                index += 1
            else:
                raise ValueError(f"Expected ',' or ']' at line {line}")

    def parse_object(s, index, line):
        if s[index] != '{':
            raise ValueError(f"Expected '{{' at line {line}")
        index += 1
        obj = {}
        index = skip_whitespace(s, index)
        if index < len(s) and s[index] == '}':
            return obj, index + 1
        while True:
            key, index = parse_string(s, index, line)
            index = skip_whitespace(s, index)
            if index >= len(s) or s[index] != ':':
                raise ValueError(f"Expected ':' after key at line {line}")
            index += 1
            value, index = parse_value(s, index, line)
            obj[key] = value
            index = skip_whitespace(s, index)
            if index >= len(s):
                raise ValueError(f"Unterminated object at line {line}")
            if s[index] == '}':
                return obj, index + 1
            elif s[index] == ',':
                index += 1
            else:
                raise ValueError(f"Expected ',' or '}}' at line {line}")

    index = 0
    line = 1
    def count_lines(s, up_to):
        return s[:up_to].count('\n') + 1

    def parse_with_line(s, index, line):
        index = skip_whitespace(s, index)
        if index >= len(s):
            raise ValueError(f"Unexpected end of JSON at line {line}")
        value, index = parse_value(s, index, line)
        index = skip_whitespace(s, index)
        if index != len(s):
            raise ValueError(f"Extra data after JSON at line {line}")
        return value

    return parse_with_line(s, 0, line)


def print_json(obj, indent=0):
    space = ' ' * indent
    if obj is None:
        print('null')
    elif isinstance(obj, bool):
        print('true' if obj else 'false')
    elif isinstance(obj, (int, float)):
        print(obj)
    elif isinstance(obj, str):
        print('"' + obj.replace('"', '\\"') + '"')
    elif isinstance(obj, list):
        print('[')
        for item in obj:
            print(space + '  ', end='')
            print_json(item, indent + 2)
        print(space + ']')
    elif isinstance(obj, dict):
        print('{')
        for key, value in obj.items():
            print(space + '  ' + '"' + str(key) + '": ', end='')
            print_json(value, indent + 2)
        print(space + '}')
    else:
        print(f"Unsupported type: {type(obj)}")