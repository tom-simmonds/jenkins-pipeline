def calculate(a, b, op):
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        return a / b
    raise ValueError(f"Unsupported operator: {op}")

def main():
    print("Basic Calculator")
    try:
        a = float(input("Enter first number: "))
        op = input("Enter operator (+, -, *, /): ").strip()
        b = float(input("Enter second number: "))
        result = calculate(a, b, op)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    except ZeroDivisionError:
        print("Error: division by zero")
        return

    print(f"Result: {result}")


if __name__ == '__main__':
    main()
