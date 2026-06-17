def process_numbers_in_file(filename):
    divisor = 73 ** 2 + 29

    with open(filename, 'r') as file:
        for line in file:
            number_str = ''
            for ch in line:
                if ch.isdigit() or (ch == '-' and not number_str):
                    number_str += ch
                elif number_str:
                    x = int(number_str)
                    if x % 7 == 0:
                        result = x * 100 / divisor
                        print(f'Число {x} кратно 7. Результат операции: {result}')
                    number_str = ''
            if number_str:
                x = int(number_str)
                if x % 7 == 0:
                    result = x * 100 / divisor
                    print(f'Число {x} кратно 7. Результат операции: {result}')