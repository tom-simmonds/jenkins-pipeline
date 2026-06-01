from app import calculate

def test_add():
    assert calculate(10,5, '+') == 15
    print("test_add passed")

def test_subtract():
    assert calculate(10,5, '-') == 5
    print("test_subtract passed")

def test_multiply():
    assert calculate(10,5, '*') == 50
    print("test_multiply passed")

def test_divide():
    assert calculate(10,5, '/') == 2
    print("test_divide passed")

def test_invalid_operator():
    try:
        calculate(10,5, '%')
        print("test_invalid_operator failed") # This should not be reached
    except ValueError: # Expected exception
        print("test_invalid_operator passed") 

def test_division_by_zero():
    try:
        calculate(10,0, '/')
        print("test_division_by_zero failed") # This should not be reached
    except ZeroDivisionError: # Expected exception
        print("test_division_by_zero passed")

def run_tests():
    test_add()
    test_subtract()
    test_multiply()
    test_divide()
    test_invalid_operator()
    test_division_by_zero()
    print("All tests passed!")

if __name__ == '__main__':
    run_tests()
