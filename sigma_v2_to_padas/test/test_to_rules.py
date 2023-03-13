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
    Gets test_padas.yml & test_sigma_rules.yml to interpret each other.
    test_padas_rules.yml has to be same as test_sigma-padas_rules.yml
    
    data_padas : 
        has padas rules that was calculated with sigma_v2_to_padas.py script
    data_sigma : 
        has properly converted sigma rules to padas rules

    """
    import os
    import yaml
    import sys
    from time import sleep
    
    path = sys.argv[2]
    prev_path = sys.argv[1]
     
    os.popen('cp ' + prev_path + ' ' + path)
    
    sleep(2)
    
    data_padas = []
    data_sigma = []

    with open(path + '/test_padas_rules.yml') as f_yaml:
        for doc in yaml.safe_load_all(f_yaml):
            data_padas.append(doc)

    with open(path + '/test_sigma-padas_rules.yml') as f_yaml:
        for doc in yaml.safe_load_all(f_yaml):
            data_sigma.append(doc)
          
    return data_padas[0], data_sigma            

            
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
    
    test_vs_real_result = []  
    count_ = 0         
    for file in data_padas:
        for sigma_test_file in data_sigma[0]:
            if file['id'] == sigma_test_file['id']:
                test_vs_real_result = [file,sigma_test_file] 
            elif file['name'] == sigma_test_file['name']:
                test_vs_real_result = [file,sigma_test_file] 

                
        if len(test_vs_real_result) == 0:
            print('Error: Same "id" or "name" can not be found in both files for test number of ' + str(count_) + '!')
        else:
            count = 0
            for fields in test_vs_real_result[1]:
                if test_vs_real_result[0][fields] != test_vs_real_result[1][fields]:
                    print('Thay are NOT same : Test Sigma Result = ' + test_vs_real_result[1][fields] + \
                          " - PADAS Result = " + test_vs_real_result[0][fields])
                    count+=1
            print(' ')
            if count != 0:
                print('NOT Same : PADAS-' + test_vs_real_result[0]['name'] + ' and SIGMA-' + test_vs_real_result[1]['name'] )
            else:
                print('Same : ' + test_vs_real_result[0]['name'])
            print('---')
        count_+=1
def main():
    try:
        data_padas, data_sigma = getting_test_files()
        check_if_they_are_same(data_padas, data_sigma)
    except Exception as error:
        print('Error: ' + str(error))
        

if __name__ == "__main__":
    main()
