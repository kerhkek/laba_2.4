def deserialize_xml(s):

    class ParseError(Exception):
        def __init__(self, message, line):
            super().__init__(f"Line {line}: {message}")
            self.line = line

    index = 0
    line = 1

    def skip_whitespace():
        nonlocal index, line
        while index < len(s) and s[index] in ' \t\n\r':
            if s[index] == '\n':
                line += 1
            index += 1

    def parse_until(chars):
        nonlocal index, line
        start = index
        while index < len(s) and s[index] not in chars:
            if s[index] == '\n':
                line += 1
            index += 1
        if index >= len(s):
            raise ParseError(f"Expected one of '{chars}'", line)
        return s[start:index], index

    def parse_tag():
        nonlocal index, line
        skip_whitespace()
        if s[index] != '<':
            raise ParseError("Ожидался '<'", line)
        index += 1
        skip_whitespace()

        if s[index] == '/':
            index += 1
            name, index = parse_until('>')
            return {'type': 'close', 'name': name.strip()}

        start = index
        while index < len(s) and s[index] not in [' ', '>', '/', '\n', '\t', '\r']:
            index += 1
        tag_name = s[start:index].strip()

        attrs = {}
        while True:
            skip_whitespace()
            if s[index] in ['>', '/', '\n', '\t', '\r']:
                break
            attr_name, index = parse_until('=')
            attr_name = attr_name.strip()
            skip_whitespace()
            if s[index] != '=':
                raise ParseError("Ожидался '=' после атрибута", line)
            index += 1
            skip_whitespace()
            if s[index] not in ['"', "'"]:
                raise ParseError("Атрибут должен начинаться с кавычки", line)
            quote_char = s[index]
            index += 1
            attr_value_start = index
            attr_value = ''
            while index < len(s):
                ch = s[index]
                if ch == quote_char:
                    index += 1
                    break
                if ch == '&':
                    pass
                if ch == '\n':
                    line += 1
                attr_value += ch
                index += 1
            attrs[attr_name] = attr_value

        skip_whitespace()
        if s[index] == '/':
            index += 1
            if s[index] != '>':
                raise ParseError("Ожидался '>' после '/'", line)
            index += 1
            return {'type': 'selfclose', 'tag': tag_name, 'attributes': attrs}
        elif s[index] == '>':
            index += 1
            return {'type': 'open', 'tag': tag_name, 'attributes': attrs}
        else:
            raise ParseError("Ожидался '>' или '/>'", line)

    def parse_element():
        nonlocal index, line
        skip_whitespace()
        if index >= len(s):
            raise ParseError("Достигнут конец файла, ожидается тег", line)

        tag_info = parse_tag()
        if tag_info['type'] == 'close':
            raise ParseError("Неправильный вызов, ожидается открывающий тег", line)

        tag_name = tag_info['tag']
        attrs = tag_info['attributes']
        children = []
        text_content = ''

        while True:
            skip_whitespace()
            if index >= len(s):
                raise ParseError("Достигнут конец файла, ожидается закрывающий тег", line)
            if s[index] == '<':
                if index + 1 < len(s) and s[index+1] == '/':
                    index += 2
                    close_name, index = parse_until('>')
                    if close_name.strip() != tag_name:
                        raise ParseError(f"Несовпадение закрывающего тега: {close_name}", line)
                    index += 1
                    return {'tag': tag_name, 'attributes': attrs, 'children': children, 'text': text_content.strip()}
                else:
                    child = parse_element()
                    children.append(child)
            else:
                start_text = index
                while index < len(s) and s[index] != '<':
                    if s[index] == '\n':
                        line += 1
                    index += 1
                text_piece = s[start_text:index].strip()
                if text_piece:
                    text_content += text_piece + ' '

    skip_whitespace()
    result = parse_element()
    return result