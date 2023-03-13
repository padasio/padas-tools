#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

SIGMA V2 Rules to PADAS

    PADAS Requirements in SIGMA V2 - Simple YML Files: 
        required = ['id', 'title', 'detection']
        
        If one of them is missing it will raise below error
            => Requirement fields are missing: MISSING_FIELD
         
 
Usage : 
    python3 sigma_v2_to_padas.py path_for_sigma2_yml_input_file path_for_padas_yml_output_file
    EXAMPLE : 
        python3.9 sigma_v2_to_padas.py test_sigma_rule.yml test_padas_rule.yml       
 
    If you want to test your data; 
        first add properly converted "test_sigma-padas_rules.yml" file into "test" director with naming

	
"""


import sys
path_for_sigma2_yml_input_file = sys.argv[1]
path_for_padas_yml_output_file = sys.argv[2]

def get_value_and_check_required_fields(path_for_sigma2_yml_input_file):
    """
    Gets input data from yaml file & if there is no "id" area, 
    gives instead of "title" as "id" 

    Parameters
    ----------
    path_for_sigma2_yml_input_file : 
        Full path of SIGMA V2 yaml file - input (str)

    Returns
    -------
    data : S
        SIGMA V2 data from yaml file (dict)

    """
    import yaml

    data_ = []
    with open(path_for_sigma2_yml_input_file) as f_yaml:
        for doc in yaml.safe_load_all(f_yaml):
            data_.append(doc)
        
    return data_

def get_padas_scheme(data):       
    """
    Gives properly scheme to if it is simple sigma rule or meta rule

    Parameters
    ----------
    data : 
        SIGMA V2 data from yaml file (dict)

    Raises
    ------
    Exception
        If at least one of the PADAS requirement area is missing, 
        it will raise below error

        => Requirement fields are missing: MISSING_FIELDS
        
    Returns
    -------
    padas_scheme : 
        Proper SIGMA-PADAS scheme (dict)

    """
    
         
    if ('id' not in data.keys()):
        data['id'] = data['title'].replace(' ','_').lower()

    no_required_fields = [field for field in ['id', 'title', 'detection'] if field not in data.keys()]
    if no_required_fields:
        raise Exception('Requirement fields are missing: "' + ', "'.join(no_required_fields) + '"')
    
    if 'logsource' in data.keys():
        padas_scheme =  {'id':'id', \
                         'name':'title', \
                        'description':'description', \
                        'datamodel':'logsource', \
                        'annotations':'tags', \
                        'pdl':'detection'}
    else:
       padas_scheme =  {'id':'id', \
                        'title':'name', \
                        'description':'detection', \
                        'padas_rule':'rules', \
                        'type':'type', \
                        'field':'field',\
                        'group_by':'group-by', \
                        'timespan':'timespan', \
                        'condition':'condition'}       

    return padas_scheme


def pdl_converter(data):
    """
    Converts SIGMA V2 rules to PADAS Rule.

    Parameters
    ----------
    data : 
        SIGMA V2 data from yaml file (dict)

    Returns
    -------
    condition : 
        Converted SIGMMA V2 Rule to PADAS Language (dict)

    """
    from copy import deepcopy as copy
    
    modifs = {'contains':'?=',
              'gt':'>',
              'gte':'>=',
              'lt':'<',
              'lte':'<='}
    
    # key = 'filter'
    # value ={'File': None, 'File|startswith': ['file', 44]}
    # key2 = 'File|startswith'
    
    
    
    pdl = copy(data)
    condition = pdl['detection'].pop('condition')
    for key, value in pdl['detection'].items():
        key_query = ['pdl']
        for key2 in value.keys():
            
            try:
                if (key2[key2.find('|')+1::] in modifs):
                    parity = modifs[key2[key2.find('|')+1::]]
                    key3 = key2[0:key2.find('|')]
                else:
                    if (key2[key2.find('|')+1::] == 'startswith'):
                        if (isinstance(value[key2], int) | isinstance(value[key2], str)):
                            value[key2]=str(value[key2]).replace('\\\\','\\') + '*'
                        else:                        
                            value[key2]=[str(value[key2][val]).replace('\\\\','\\') + '*' for val in range(len(value[key2]))]
                        key3 = key2[0:key2.find('|')]
                        parity = '='
                    elif (key2[key2.find('|')+1::] == 'endswith'):
                        if (isinstance(value[key2], int) | isinstance(value[key2], str)):
                            value[key2]='*' + str(value[key2]).replace('\\\\','\\')
                        else:
                           value[key2]=['*' + str(value[key2][val]).replace('\\\\','\\') for val in range(len(value[key2]))]
                        key3 = key2[0:key2.find('|')]
                        parity = '='
                    else:
                        parity = '='
                        key3 = key2
            except:
                parity = '='
                key3 = key2

            
            if value[key2] is None:
                key_query.append('(' + key2 + '!=\"*\")')
            else: 
                if isinstance(value[key2], str):
                    key_query.append('(' + key3 + parity +'\"' + str(value[key2]) + '\")')
                    
                elif (isinstance(value[key2], int) | isinstance(value[key2], bool)):
                    key_query.append('(' + key3 + parity + str(value[key2]) + ')')
                else:
                    
                    strs = []
                    for i in range(len(value[key2])):
                        if (isinstance(value[key2][i], str)):
                            strs.append([key3 +'=' + value[key2][i], key3 +'=\"' + value[key2][i] + '\"'])
                        
                    
                    
                    # join_val = ' OR ' + key3 + parity + '\"'
                    # key_query.append('(' + key3 + parity + '\"' + join_val.join([str(x) for x in value[key2]]) + '\"')                           
                    
                    
                    join_val = ' OR ' + key3 + parity 
                    condition_as_str = '(' + key3 + parity + join_val.join([str(x) for x in value[key2]]) + ')'
                    
                    for i in range(len(strs)):
                        condition_as_str = condition_as_str.replace(strs[i][0], strs[i][1])
                    
                    key_query.append(condition_as_str)                  
    
            
        key_query = ' AND '.join(key_query[1::]) 
        condition = condition.replace(key, '(' + key_query +')').replace('="None"', '!="*"')
        
    # print(data['title'])
    # print(condition)
    return condition.replace('\\','\\\\')


def sigma_to_padas(data, padas_scheme):
    """
    Turns SIGMA V2 rules into PADAS rules

    Parameters
    ----------
    data : 
        SIGMA V2 data from yaml file (dict)
    padas_scheme : 
        Proper SIGMA-PADAS scheme (dict)

    Returns
    -------
    padas_scheme : 
        Converted PADAS rules (dict)

    """
    for key, value in padas_scheme.items():
        try:
            if padas_scheme[key] == 'detection':
                padas_scheme[key] = pdl_converter(data)
              
            elif padas_scheme[key] == 'logsource':
                padas_scheme[key] = '_'.join(data['logsource'].values()).replace(' ','_')
            else:
                padas_scheme[key] = data[value] 
        except:
            padas_scheme[key] = ''
    
    padas_scheme['enabled'] = False
    

    return padas_scheme


def pdl_to_json(all_padas_rules, path_for_padas_yml_output_file):
    """
    Writes PADAS rules into yaml file (json)

    Parameters
    ----------
    padas_rules : 
        Converted PADAS rules (dict)
    output_file : 
        Full path of PADAS yaml file - output (str)

    Returns
    -------
    None.

    """
    
    import json

    out_file = open(path_for_padas_yml_output_file, "w")
    json.dump(all_padas_rules, out_file, indent = 4, sort_keys = False)
    out_file.close()
        
def main():

    try:
        data_ = get_value_and_check_required_fields(path_for_sigma2_yml_input_file)
        
        all_padas_rules = []
        for i in range(len(data_)):
            padas_scheme = get_padas_scheme(data_[i])
            padas_rules = sigma_to_padas(data_[i], padas_scheme)
            # print(padas_rules)
            all_padas_rules.append(padas_rules)
            
        pdl_to_json(all_padas_rules, path_for_padas_yml_output_file)
        print('Done!')
    except Exception as error:
        print('Error: ' + str(error))


if __name__ == "__main__":
    main()
