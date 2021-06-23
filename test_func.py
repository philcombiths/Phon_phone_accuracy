"""
Test_func.py Version 1.0
Updated 6/22/2021

This script contains a function, test_func(), which batch executes a function
for testing purposes. Prints function parameter and output to console. 
Cannot test a function with zero parameters. 

Example use:
    from test_func import test_func
    test_func(my_function, param_list)
"""

def test_func(function, parameters, single_param=True):
    """
    Batch execute a function with given parameters.
    
    Parameters
    ----------
    function : function
        Function to be tested. Do not include (). Do not enclose in "".
    
    parameters : list
        Pass a list sets of parameter values for function testing. As in the
        following: [(param_value_1a, param_value_2a), param_value_1b,
                    param_value_2b)].
        
    Returns
    -------
    test_return_list : list
        List of output returned from each function call.
        
    """
    test_list = []
    test_return_list = []
    # Test function using parameter values passed to function
    if parameters:
        test_list = parameters
    else:
        print("No parameters given. Retry,")       
    # Batch execute function
       
    
    for n, t in enumerate(test_list):
        if single_param:
            num_parameters = 1
            print("\n***********")
            print(f"Test {n}:")
            print(f"\tNum. parameters: {num_parameters}")
            print(f"\t\t{t}")
            print("\tFunction result:")
            print('\t\tPrintout:')
            print('\t\t*****')            
            func_result = function(t)
            print('\t\t*****')
            test_return_list.append(func_result)
            print(f"\t\tReturn:\n\t\t\t{func_result}")
            continue
        else:
            if type(t) is str:
                num_parameters = 1
                print("\n***********")
                print(f"Test {n}:")
                print(f"\tNum. parameters: {num_parameters}")
                print(f"\t\t{t}")
                print("\tFunction result:")
                print('\t\tPrintout:')
                print('\t\t*****')            
                func_result = function(t)
                print('\t\t*****')
                test_return_list.append(func_result)
                print(f"\t\tReturn:\n\t\t\t{func_result}")
                continue
            else:
                num_parameters = len(t)
                print("\n***********")
                print(f"Test {n}:")
                print(f"\tNum. parameters: {num_parameters}")
                for param in t:
                    print(f"\t\t{param}")
                print("\tFunction result:")  
                print('\t\tPrintout:')
                print('\t\t*****')
                try:
                    func_result = function(*t)
                except TypeError:
                    raise Exception("Multiple parameters identified when 1 parameter expected. You can change single_param to True.")
                test_return_list.append(func_result)
                print('\t\t*****')
                print(f"\t\tReturn:\n\t\t\t{func_result}")            
        print(f"End Test {n}")
    # Return dictionary of output of each function call
    return test_return_list
