#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

SIGMA V2 Rules to PADAS

    PADAS Requirements in SIGMA V2 - Simple YML Files: 
        required = ['id', 'title', 'detection']
        
         
    PADAS Requirements in SIGMA V2 - Meta YML Files:
        required = ['id', 'title', 'action']

        If one of them is missing it will raise below error
            => Requirement fields are missing: MISSING_FIELD 

Usage : 
    python3 sigma_v2_to_padas.py path_for_sigma2_yml_input_file path_for_padas_yml_output_file
    EXAMPLE : 
        python3.9 sigma_v2_to_padas.py input_sigma_rules.yml input_sigma_rules.json       
 
    If you want to test your data; 
        first add properly converted "test_sigma-padas_rules.yml" file into "test" director with naming

	
"""

import sys
path_for_sigma2_yml_input_file = sys.argv[1]
path_for_padas_json_output_file = sys.argv[2]
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
    data : 
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
    Gives appropriate PADAS-SIGMA scheme depending on which one it is.
    Simple SIGMA or META Rule ;
    
        - simple sigma rule 
                         {'id':'id', \
                         'name':'title', \
                         'description':'description', \
                         'datamodel':'logsource', \
                         'annotations':'tags', \
                         'pdl':'detection'}
        
    
        - meta rule
                         {'id':'id', \
                         'name':'title', \
                         'description':'description', \
                        'datamodel':'logsource', \
                        'annotations':'tags', \
                        'pdl':'action'} 

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
    
    if ('title' not in data.keys()):
        data['title'] = data['name'].replace(' ','_').lower()
    
    if ('id' not in data.keys()):
        data['id'] = data['title'].replace(' ','_').lower()

    if ('id' not in data.keys()):
        if ('title' not in data.keys()):
            raise Exception('There is no unique id, title or name!!')
           

    if 'action' in data.keys():
        no_required_fields = [field for field in ['id', 'title'] if field not in data.keys()]
        if no_required_fields:
            raise Exception('Requirement fields are missing: "' + ', "'.join(no_required_fields) + '"')
            
        padas_scheme =  {'id':'id', \
                         'name':'title', \
                         'description':'description', \
                        'datamodel':'logsource', \
                        'annotations':'tags', \
                        'pdl':'action'}
            
    elif 'detection' in data.keys():
        
        if 'name' in data.keys():
            padas_scheme =  {'id':'id', \
                              'name':'name', \
                              'description':'description', \
                              'datamodel':'logsource', \
                              'annotations':'tags', \
                              'pdl':'detection'}
        else:
            padas_scheme =   {'id':'id', \
                              'name':'title', \
                              'description':'description', \
                              'datamodel':'logsource', \
                              'annotations':'tags', \
                              'pdl':'detection'}         
    return padas_scheme

          
    


def padas_rule_converter(data):
    """
    Converts SIGMA V2 simple rules to PADAS Rule.

    Parameters
    ----------
    data : 
        SIGMA V2 data from yaml file (dict)

    Returns
    -------
    pdl : 
        Converted SIGMA V2 Simple Rule to PADAS Language (dict)

    """
    from copy import deepcopy as dc
    import re
    
    def allAsteriks(pdl):
        """
        

        Parameters
        ----------
        pdl : 
            condition field from Sigma Rule (str)

        Returns
        -------
        Fields with "*" (list)

        """
        return [[pdl.split()[i-2], star[:-1]] for i, star in enumerate(pdl.split()) if star.find('*') > -1]
    
    
    def detection_field_rules(key2, values, mod):
        
        value = dc(values)
        if (mod in modifs):
            parity = modifs[mod]
            return parity, value
        elif (mod == 'startswith'):
            if (isinstance(value[key2], int) | isinstance(value[key2], str)):
                value[key2]=str(value[key2]).replace('\\\\','\\') + '*'
            else:                        
                value[key2]=[str(value[key2][val]).replace('\\\\','\\') + '*' for val in range(len(value[key2]))]
            parity = '='
            return parity, value
        elif (mod == 'endswith'):
            if (isinstance(value[key2], int) | isinstance(value[key2], str)):
                value[key2]='*'  + str(value[key2]).replace('\\\\','\\')
            else:
               value[key2]=['*' + str(value[key2][val]).replace('\\\\','\\') for val in range(len(value[key2]))]

            parity = '='  
            return parity, value
        else:
            if mod != 'all':
                return mod, values
            else:
                return '', values

   
    modifs = {'contains':'?=',
              'gt':'>',
              'gte':'>=',
              'lt':'<',
              'lte':'<='}
     
    padas_rule = dc(data)
    pdl = padas_rule['detection'].pop('condition')
    
    pdl_asteriks = allAsteriks(pdl)   
  
    for i in range(len(pdl_asteriks)):    
        pdl = pdl.replace(pdl_asteriks[i][1] + '*', '(' + pdl_asteriks[i][1] + '*)')
    
    for key, values in padas_rule['detection'].items():
        key_query = ['pdl']
        key_asteriks = [[pdl_asteriks[i][0], pdl_asteriks[i][1]] for i in range(len(pdl_asteriks)) if key.find(pdl_asteriks[i][1]) > -1]        
        
        for key2 in values.keys():
            # print(key2)
            
            splitted_key2 = key2.split('|')
            
            try:
                mod1 = splitted_key2[1]
                field = splitted_key2[0]
                try:
                    mod2 = splitted_key2[2]
                except:
                    mod2 = ''
            except:
                mod1 = '='
                mod2 = ''
                field = splitted_key2[0]  #key3
          
            try:
                del(parity1, parity2, value1, value2)
            except:
                pass

            parity1, value1 = detection_field_rules(key2, values, mod1)
            parity2, value2 = detection_field_rules(key2, values, mod2)

            part_query = []            
            if parity2 != '':
                if isinstance(value1[key2], (int, float, str, bool))|(value1[key2] is None):
                    lens = 1
                else:
                    lens = len(value1[key2])
                for vals in range(lens):
                    try:
                        val1 = value1[key2][vals]
                    except:
                        val1 = value1[key2]
                    try:
                        val2 = value2[key2][vals]
                    except:
                        val2 = value2[key2]

                    if isinstance(val1, str):
                        val1 = '\"' + val1 + '\"'               
                    if isinstance(val2, str):
                        val2 = '\"' + val2 + '\"' 
                    
                    sentence = '(' + field + parity1 + str(val1).replace('None', '!=\"*\"') + ') AND (' + field + parity2 + str(val2).replace('None', '!=\"*\"') + ')'
                    part_query.append(sentence.replace('=!=', '!='))
            else:
                if isinstance(value1[key2], (int, float, str, bool))|(value1[key2] is None):
                    lens = 1
                else:
                    lens = len(value1[key2])
                for vals in range(lens):
                    if lens != 1:
                        val1 = value1[key2][vals]
                    else:
                        val1 = value1[key2]
                    if isinstance(val1, str):
                        val1 = '\"' + val1 + '\"'
                    sentence = field + parity1 + str(val1).replace('None', '!=\"*\"')
                    part_query.append(sentence.replace('=!=', '!='))
            
            if mod2 == 'all':
                join_val = ' AND ('
            else:
                join_val = ' OR ('
                
            if lens != 1:
                if len(values.keys()) != 1:
                    key_query.append('((' + join_val.join([str(x) + ')' for x in part_query]) + ')')   
                else:
                    key_query.append('(' + join_val.join([str(x) + ')' for x in part_query])) 
            else:    
                key_query.append('(' + join_val.join([str(x) + ')' for x in part_query])) 
    
        if isinstance(key_query[1::], str):   
            pdl = pdl.replace('="None"', '!="*"')
        else:
            key_query = ' AND '.join(key_query[1::])
            
            if len(key_asteriks) > 0:
                parity2 = ['OR' if key_asteriks[0][0] == '1' else 'AND'][0]
                pdl = pdl.replace(key_asteriks[0][1] + '*', '(' + key_query +') ' + parity2 + ' ' + key_asteriks[0][1] + '*')
            else:
                pdl = pdl.replace(key, '(' + key_query +')')
        
        if len(re.findall('\(', pdl)) <= 2:
            pdl = pdl.replace('((', '').replace('))','')
            
    pdl = pdl.replace('all of ', '').replace('1 of ', '')
    for i, j in pdl_asteriks:
        parity2 = ['OR' if i == '1' else 'AND'][0]
        pdl = pdl.replace(' ' + parity2 + ' ' + j + '*','')
    
    return pdl.replace('"', '\"').replace('\\','\\\\')


def padas_rule_converter_correlation(data):
    """
    Converts SIGMA V2 META rules to PADAS Rule.

    Parameters
    ----------
    data : SIGMA V2 data from yaml file (dict)

    Returns
    -------
    correlation_pdl : Converted SIGMA V2 META Rule to PADAS Language (dict)

    """
    
    modifs = {'gt':'>',
              'gte':'>=',
              'lt':'<',
              'lte':'<='}
    
    correlation_pdl = ''
 
    # Rules for event_count & value_count
    if ('rules' in data.keys()):
        if (data['type'] in ['event_count', 'value_count']):
            correlation_pdl = 'padas_rule IN ' + '[\"' + '\", \"'.join(data['rules']) + '\"] | '
    
    # Rules for every rule type
    if 'aliases' in data.keys():
        for i in range(len(data['aliases'].keys())):
            field_ = list(data['aliases'].items())[i][0]
            rules_values_ = list(data['aliases'].items())[i][1]
        
            test=''
            for j in reversed(range(len(list(rules_values_)))):
                if j == len(list(rules_values_)) - 1 :
                    test = test + 'if(padas_rule=\"' + list(rules_values_)[j] + \
                        '\", ' + list(rules_values_.values())[j] + ', \"\")'
                else:
                    test = 'if(padas_rule=\"' + list(rules_values_)[j] + \
                        '\", ' + list(rules_values_.values())[j] + ', ' + test + ')'
		
            correlation_pdl = correlation_pdl + 'eval ' + field_ + '='  + test + ' | '   
    
    # Specific rules for each rule type (event_count, value_count, temporal)
    if ('event_count' in data['type']):
        where_condition = 'padasAggregation.eventCount'
        correlation_pdl = correlation_pdl + 'event_count timespan=' + \
            data['timespan'] + ' group_by ' + ', '.join(data['group-by'])
    elif ('value_count' in data['type']):
        where_condition = 'padasAggregation.valueCount'
        correlation_pdl = correlation_pdl + 'value_count(' +data['field'] + ') timespan=' + \
            data['timespan'] + ' group_by ' + ', '.join(data['group-by']) 
    elif ('temporal' in data['type']):
        if data.get('ordered') == None:
             data['ordered'] = True
         
        correlation_pdl = correlation_pdl + 'temporal(ordered=' + \
            str(data['ordered']).lower()  +') [padasRule=\"' + \
             '\" || padasRule="'.join(data['rule']) + '\"] ' + 'timespan=' + \
             data['timespan'] + ' group_by ' + ', '.join(data['group-by'])

    # Rules for every rule type
    if 'condition' in data.keys():
        for i in list(data['condition'].keys()):
            if 'range' == i:     
                ranges_ = data['condition']['range'].split('..')
                correlation_pdl = correlation_pdl + ' where ' + where_condition + '>=' + ranges_[0] + \
                    ' AND ' + where_condition + '<=' + ranges_[1]
            else:
                correlation_pdl = correlation_pdl + ' where ' + where_condition + modifs[i] + ' ' + \
                    str(data['condition'][i])


    return correlation_pdl


def sigma_to_padas(data, padas_scheme):
    """
    Turns SIGMA V2 rules into PADAS rules

    Parameters
    ----------
    data : 
        SIGMA V2 data from yaml file (dict)
    padas_scheme : 
        Proper SIGMA-PADAS scheme (dict)
    
    Raises
    ------
    Exception
        If pdl field is empty,
        it will raise below error

        => There is unrecognized value modifer!
        

    Returns
    -------
    padas_scheme : 
        Converted PADAS rules (dict)

    """
   
    for key, value in padas_scheme.items():
        try:
            if padas_scheme[key] == 'detection':
                padas_scheme[key] = padas_rule_converter(data)
              
            elif padas_scheme[key] == 'logsource':
                # check category, product and services fields are exists under logsource
                values_ = [data['logsource'][i] for i in ['category', 'product', 'service'] if i in data['logsource']]
                
                padas_scheme[key] = '_'.join(values_).replace(' ','_')
            elif padas_scheme[key] == 'tags':
                if 'tags' not in data.keys():
                    padas_scheme[key] = ['']
                else:
                    padas_scheme[key] = [data[value]]
            elif padas_scheme[key] == 'action':
                padas_scheme[key] = padas_rule_converter_correlation(data)
            else:
                padas_scheme[key] = data[value] 
        except:
            padas_scheme[key] = ''
    
    if padas_scheme['pdl'] == '':
        raise Exception('There is unrecognized value modifer in id : ' + padas_scheme['id'] )    
    
    if  ('action' in data.keys()):
        padas_scheme['datamodel'] = 'padas_alert'

    padas_scheme['enabled'] = False
    return padas_scheme


def padas_rule_to_json(all_padas_rules, path_for_padas_yml_output_file):
    """
    Writes PADAS rules into json file (json)

    Parameters
    ----------
    all_padas_rules : 
        Converted PADAS rules (dict)
    path_for_padas_yml_output_file : 
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
    """
    
    Main function.
    
    Returns
    -------
    None.

    """

    try:
        data_ = get_value_and_check_required_fields(path_for_sigma2_yml_input_file)
        
        all_padas_rules = []
        for i in range(len(data_)):
            padas_scheme = get_padas_scheme(data_[i])
            padas_rules = sigma_to_padas(data_[i], padas_scheme)
            
            all_padas_rules.append(padas_rules)

                
        padas_rule_to_json(all_padas_rules, path_for_padas_json_output_file)
        print('Converting SIGMA Rules to PADAS Rules is Done!')
        print(' ')
    except Exception as error:
        print('Error: ' + str(error))
        print(' ')

if __name__ == "__main__":
    main()
