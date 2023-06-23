# SIGMA V2 Rules to PADAS
This is one of the padas-tool for transforming **SIGMA V2** rules (**SIMPLE**, **META**) into json format that **PADAS** can understand. Also, there are two main field to understand if the rule is SIMPLE or META rule in this tool as mantioned in the SIGMA documentations ([SIMPLE](https://github.com/SigmaHQ/sigma-specification/blob/main/Sigma_specification.md). [META](https://github.com/SigmaHQ/sigma-specification/blob/main/Sigma_specification.md))

- Requirement Fields for SIGMA V2 - SIMPLE Rules to PADAS conversion :
	> "id" OR/AND "title", "detection"
	
- Requirement Fields for SIGMA V2 - META Rules to PADAS conversion :
	> "id" OR/AND "title", "action"
        
    If one of them is missing it will raise below error.
        => `Requirement fields are missing: MISSING_FIELD, ... `

## Tool Parts
It is a tool that we can divide into 2 parts, the main part and the test part. While the main part contains only the `sigma_v2_to_padas.py` script, the test section under the `test/` directory contains the `test_to_rules.py` main test script and `input_sigma_rules.yml` and `expected_output.json` file.

### MAIN :
**`sigma_v2_to_padas.py`** : Main script that transforms **SIGMA V2** rules into **PADAS** rules. It will be enough to convert data, if there is only this script. If input yaml file added other than directory that contains `sigma_v2_to_padas.py` file, path of the file also has to be given in the command.

#### Usage 
`python3` `sigma_v2_to_padas.py` `path_for_sigma2_yml_input_file` `path_for_padas_json_output_file`

##### example : `python3 sigma_v2_to_padas.py input_sigma_rules.yml input_sigma_rules.json`
 

### TEST :
**`test/test_to_rules.py`** :   This script is mostly produced to test the changes made on the `sigma_v2_to_padas` script. It can test whether the **SIGMA V2** rules specified in the `input_sigma_rules.yml` file are converted in accordance with the **PADAS** rules as in the `expected_output.json` file with the main script.

**`test/input_sigma_rules.yml`** :  This file contains **SIGMA V2** rules that are desired to convert them into **PADAS** rules. By default, it contains 22 tests consisting of both SIMPLE and META rules as below. 
  
* **Test1_AND**
	-- *Description* : Test for using AND condition in the field selections - Simple.

* **Test2_OR-Str-Numeric**
	-- *Description* : Test for using both numeric and string numbers in the same field selection - Simple.

* **Test3_Contains**
	-- *Description* : Test for using contains argument in the field selection - Simple.

* **Test4_GT**
	-- *Description* : Test for using GT (greater than) argument in the field selection - Simple.

* **Test5_LT**
	-- *Description* : Test for using LT (less than) argument in the field selection - Simple.

* **Test6_AND-GT-LT**
	-- *Description* : Test for using both GT (greater than) AND LT (less than) argument in the same field selection - Simple.

* **Test7_OR-GT**
	-- *Description* : Test for using 2 GT (greater than) argument with OR connector in the same field selection - This may produce an illogical result - Simple.

* **Test8_OR-LT**
	-- *Description* : Test for using 2 LT (less than) argument with OR connector in the same field selection - This may produce an illogical result - Simple.

* **Test9_AND-GTE-LTE**
	-- *Description* : Test for using both GTE (greater than or equals) AND LTE (less than or equals) argument in the same field selection - Simple.

* **Test10_Startswith**
	-- *Description* : Test for using startswith argument in the field selection - Simple.

* **Test11_Endswith**
	-- *Description* : Test for using endswith argument in the field selection - Simple.

* **Test12_AND-Startswith-Endswith**
	-- *Description* : Test for using both startswith AND endswith argument in the same field selection - Simple.

* **Test13_Null**
	-- *Description* : Test for seraching NULL data in the field selection - Simple.

* **Test14_Contains-Endswith-AND NOT-Null**
	-- *Description* : Test for using both contains AND endswith argument in the same field selection but not with NULL data - Simple.

* **Test15_Contains-Endswith-AND NOT-Null**
	-- *Description* : Test for using both contains AND endswith argument in the same field selection but not with both NULL data and startswith argument - Simple.

* **Test16_event_count & range**
	-- *Description* : Test to use event_count argument - Meta 
    
* **Test17_value_count & GTE**
	-- *Description* : Test to use temporal argument - Meta 
      
* **Test18_select**
	-- *Description* : Give condition rules for `Test20_temporal & aliases` test - Simple

* **Test19_select**
	-- *Description* : Give condition rules for `Test20_temporal & aliases` test - Simple

* **Test20_temporal & aliases**
	-- *Description* : Test to using conditional fields using `internal_error` and `new_network_connection` rules - Meta

* **Test21_1 of & all of**
	-- *Description* : Test for selection of have same pattern as selection* fields and exclude 1 of the filter field - Simple.

* **Test22_mod1 & mod2**
	-- *Description* : Test for using two different argument together (Ex : Directory has to CONTAINS and have ALL values) - Simple


**`test/expected_output.json`** :  This file contains **PADAS** rules that are converted from **SIGMA V2** rules. 

#### Usage  - Test
      - If you want to test your data to see if script will convert properly Sigma V2 rules to PADAS rules;
          1. add properly converted "expected_output.json" file & "test_sigma-padas_rules.yml" file that contains original SIGMA rules, into "test" directory.
          2. run test_to_rules.py script as example from terminal. This script automatically will convert and test the data. 

##### example : `python3 test_to_rules.py`

