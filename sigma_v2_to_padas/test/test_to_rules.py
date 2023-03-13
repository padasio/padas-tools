#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Script works only with test_padas_rules.yml & test_sigma-padas_rules.yml files.
If you want to use your file names, change these names in getting_test_files function.

To test your own rules, you can change "test_sgima-padas_rules.yml" file.

Usage : 
    python3 test_to_rules.py path_of_the_created_padas_yml_directory path_of_the_test_directory
    
    EXAMPLE : 
        python3.9 test_to_rules.py ../test_padas_rules.yml . 
"""


def getting_test_files():
    """
    

    Returns
    -------
    Turns "input_sigma_rules.yml" file into "input_sigma_rules.json" with 
    "sigma_v2_to_padas.py" script. Also, interpret the input_sigma_rules.json
    with expected_output.json
    
    input_sigma_rules.json has to be same as expected_output.json
    
    data_padas : 
        has padas rules that was calculated with sigma_v2_to_padas.py script (json)
    data_sigma : 
        has properly converted sigma rules to padas rules (json)

    """
    import os
    import yaml
    from time import sleep
    
    os.system('python3.9 ../sigma_v2_to_padas.py input_sigma_rules.yml input_sigma_rules.json')
    sleep(2)
    
    data_padas = []
    data_sigma = []

    with open('input_sigma_rules.json') as f_yaml:
        for doc in yaml.safe_load_all(f_yaml):
            data_padas.append(doc)
            
    with open('expected_output.json') as f_yaml:
        for doc in yaml.safe_load_all(f_yaml):
            data_sigma.append(doc)
          
    return data_padas, data_sigma            

            
def check_if_they_are_same(data_padas, data_sigma): 
    """
    Checks if the converted 'data' is the same with prepeared 'data_sigma'

    Parameters
    ----------
    data_padas : 
        has padas rules that was calculated with sigma_v2_to_padas.py script
    data_sigma : 
        has properly converted sigma rules to padas rules

    Returns
    -------
    None.

    """
    
    count = 0         
    for i in range(len(data_sigma[0])):
        if data_padas[0][i]['id'] != data_sigma[0][i]['id']:
            print('Error: Same "id" or "name" can not be found in both files for test number of ' + str(count) + '!')
        else:
            if (sorted(data_padas[0][i].items()) == sorted(data_sigma[0][i].items())) == True:
                print('Same : ' + data_sigma[0][i]['name'])
            else:
                print('NOT Same : PADAS - ' + data_padas[0][i]['name'] + 'SIGMA - ' + data_sigma[0][i]['name'])
        print('---')
    
        count+=1

def main():
    """
    
    Main function.
    
    Returns
    -------
    None.

    """
    
    try:
        
        data_padas, data_sigma = getting_test_files()
        check_if_they_are_same(data_padas, data_sigma)
    except Exception as error:
        print('Error: ' + str(error))
        

if __name__ == "__main__":
    main()
