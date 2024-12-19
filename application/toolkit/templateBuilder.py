from dataclasses import dataclass
import re
from enum import Enum

# ops
compare_ops = {
    'equals': '=', 
    'unequals': '!=',
    'greater than': '>',
    'less than': '<',
    'greater than or equals': '>=', 
    'less than or equals': '<='
}

# patterns
order_patterns = {
    'descending': 'DESC', 
    'ascending': 'ASC'
}


class Operation(Enum):
    """template of simple select"""
    SIMPLE_SELECT = "find $attrs in $table" # SELECT $attr FROM $table

    """template of simple select all"""
    SIMPLE_SELECT_ALL = "find all in $table" # SELECT * FROM $table

    """template of simple where"""
    SELECT_WHERE = "find $attrs in $table where $w_attr $w_op $w_value" # SELECT $attr FROM $table WHERE $condition

    """template of group by"""
    GROUP_BY = "find $attrs in $table where $w_attr $w_op $w_value group by $g_attr" # SELECT $attr FROM $table WHERE $condition GROUP BY $g_attr

    """template of order by"""
    ORDER_BY = "find $attrs in $table where $w_attr $w_op $w_value with $o_attr in $pattern order" # SELECT $attr FROM $table WHERE $condition ORDER BY $pattern

    """template of group by having"""
    GROUP_BY_HAVING = "find $attrs in $table where $w_attr $w_op $w_value group by $g_attr having $h_attr $h_op $h_value" # SELECT $attr FROM $table WHERE $condition GROUP BY $g_attr HAVING $h_condition

    """template of join"""
    JOIN = "find $attrs_t1 from $table_1 and $attrs_t2 from $table_2 where they match on $j_attr"

@dataclass
class SIMPLE_SELECT:
    pattern = re.compile(Operation.SIMPLE_SELECT.value \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>\S+)"))

@dataclass
class SIMPLE_SELECT_ALL:
    pattern = re.compile(Operation.SIMPLE_SELECT_ALL.value \
                         .replace("$table", r"(?P<table>\S+)"))

@dataclass
class SELECT_WHERE:
    pattern = re.compile(Operation.SELECT_WHERE.value \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>.+)") \
                         .replace("$w_attr", r"(?P<w_attr>\S+)") \
                         .replace("$w_op", r"(?P<w_op>.+)") \
                         .replace("$w_value", r"(?P<w_value>\S+)"))

class SELECT_NO_WHERE(SELECT_WHERE):
    pattern = SIMPLE_SELECT.pattern

@dataclass
class GROUP_BY:
    pattern = re.compile(Operation.GROUP_BY.value \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>.+)") \
                         .replace("$w_attr", r"(?P<w_attr>\S+)") \
                         .replace("$w_op", r"(?P<w_op>.+)") \
                         .replace("$w_value", r"(?P<w_value>\S+)") \
                         .replace("$g_attr", r"(?P<g_attr>\S+)"))
    
class GROUP_BY_NO_WHERE(GROUP_BY):
    template = "find $attrs in $table group by $g_attr"
    pattern = re.compile(template \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>.+)") \
                         .replace("$g_attr", r"(?P<g_attr>\S+)"))

@dataclass
class ORDER_BY:
    pattern = re.compile(Operation.ORDER_BY.value \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>.+)") \
                         .replace("$w_attr", r"(?P<w_attr>\S+)") \
                         .replace("$w_op", r"(?P<w_op>.+)") \
                         .replace("$w_value", r"(?P<w_value>\S+)") \
                         .replace("$o_attr", r"(?P<o_attr>\S+)") \
                         .replace("$pattern", r"(?P<pattern>\S+)"))   

class ORDER_BY_NO_WHERE(ORDER_BY):
    template = "find $attrs in $table with $o_attr in $pattern order"
    pattern = re.compile(template \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>.+)") \
                         .replace("$o_attr", r"(?P<o_attr>\S+)") \
                         .replace("$pattern", r"(?P<pattern>\S+)")) 

@dataclass
class GROUP_BY_HAVING:
    pattern = re.compile(Operation.GROUP_BY_HAVING.value \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>.+)") \
                         .replace("$w_attr", r"(?P<w_attr>\S+)") \
                         .replace("$w_op", r"(?P<w_op>.+)") \
                         .replace("$w_value", r"(?P<w_value>\S+)") \
                         .replace("$g_attr", r"(?P<g_attr>\S+)")
                         .replace("$h_attr", r"(?P<h_attr>\S+)") \
                         .replace("$h_op", r"(?P<h_op>.+)") \
                         .replace("$h_value", r"(?P<h_value>\S+)")) \

class GROUP_BY_HAVING_NO_WHERE(GROUP_BY_HAVING):
    template = "find $attrs in $table group by $g_attr having $h_attr $h_op $h_value"
    pattern = re.compile(template \
                         .replace("$attrs", r"(?P<attrs>.+)") \
                         .replace("$table", r"(?P<table>.+)") \
                         .replace("$g_attr", r"(?P<g_attr>\S+)")
                         .replace("$h_attr", r"(?P<h_attr>\S+)") \
                         .replace("$h_op", r"(?P<h_op>.+)") \
                         .replace("$h_value", r"(?P<h_value>\S+)")) \


class GROUP_BY_HAVING_NO_HAVING(GROUP_BY_HAVING):
    pattern = GROUP_BY.pattern

class GROUP_BY_HAVING_NO_ALL(GROUP_BY_HAVING):
    pattern = GROUP_BY_NO_WHERE.pattern

@dataclass
class JOIN:
    pattern = re.compile(Operation.JOIN.value \
                         .replace("$attrs_t1", r"(?P<attrs_t1>.+)") \
                         .replace("$table_1", r"(?P<table_1>\S+)") \
                         .replace("$attrs_t2", r"(?P<attrs_t2>.+)") \
                         .replace("$table_2", r"(?P<table_2>\S+)") \
                         .replace("$j_attr", r"(?P<j_attr>\S+)"))


@dataclass
class Result:
    keyword: str = None
    attrs: list = None
    table: str = None
    w_attr: str = None
    w_op: str = None
    w_value: str = None
    g_attr: str = None
    o_attr: str = None
    pattern: str = None
    h_attr: str = None
    h_op: str = None
    h_value: str = None
    attrs_t1: list = None
    table_1: str = None
    attrs_t2: list = None
    table_2: str = None
    j_attr: str = None

def transfer(match_attrs):
    if match_attrs:
        return re.split(r"[,\s]+", match_attrs)
    else:
        return None
    
def adjust_condition(op, value, is_mysql: bool = True):
    temp_str = op + " " + value
    temp_list = temp_str.split()
    n = len(temp_list)
    num = 4 if n > 4 else n
    while num > 0:
        target_str = " ".join(temp_list[:num])
        if target_str in compare_ops:
            new_op = target_str
            new_value = " ".join(temp_list[num:])
            return new_op, add_quotes_if_missing(new_value) if is_mysql else new_value
        num -= 1
    return None, None

def type_normalize(value):
    try:
        if value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit() and value.count('.') == 1:
            value = float(value)
        elif value.startswith('[') and value.endswith(']'):
            value = eval(value)

        return value
    except Exception as e:
        print(e)
        return value

def add_quotes_if_missing(s):
    # check if digit num
    s = type_normalize(s)
    type_s = type(s)
    
    # check ""
    if type_s == str:
        if s.startswith(("'", '"')) and s.endswith(("'", '"')):
            return s 
        return f"'{s}'"
    else:
        return str(s)

def key_pharse(match, query_type: str, query_type_check:str, is_mysql: bool = True): #set values
    result = Result()
    result.keyword = query_type
    print(query_type_check)
    try:
        match query_type_check:
            case "SIMPLE_SELECT" | "SELECT_NO_WHERE":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')
                
            case "SIMPLE_SELECT_ALL":    
                result.table = match.group('table')

            case "SELECT_WHERE":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')
                result.w_attr = match.group('w_attr')
                result.w_op, result.w_value = adjust_condition(match.group('w_op'), match.group('w_value'), is_mysql)

            case "GROUP_BY" | "GROUP_BY_HAVING_NO_HAVING":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')
                result.w_attr = match.group('w_attr')
                result.w_op, result.w_value = adjust_condition(match.group('w_op'), match.group('w_value'), is_mysql)
                result.g_attr = match.group('g_attr')  

            case "GROUP_BY_NO_WHERE" | "GROUP_BY_HAVING_NO_ALL":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')
                result.g_attr = match.group('g_attr')                  

            case "ORDER_BY":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')
                result.w_attr = match.group('w_attr')
                result.w_op, result.w_value = adjust_condition(match.group('w_op'), match.group('w_value'), is_mysql)    
                result.o_attr = match.group('o_attr')
                result.pattern = match.group('pattern') 
            
            case "ORDER_BY_NO_WHERE":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')
                result.o_attr = match.group('o_attr')
                result.pattern = match.group('pattern') 

            case "GROUP_BY_HAVING":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')
                result.w_attr = match.group('w_attr')
                result.w_op, result.w_value = adjust_condition(match.group('w_op'), match.group('w_value'), is_mysql)    
                result.g_attr = match.group('g_attr')  
                result.h_attr = match.group('h_attr')
                result.h_op, result.h_value = adjust_condition(match.group('h_op'), match.group('h_value'), is_mysql)  
            
            case "GROUP_BY_HAVING_NO_WHERE":
                result.attrs = transfer(match.group('attrs'))
                result.table = match.group('table')   
                result.g_attr = match.group('g_attr')  
                result.h_attr = match.group('h_attr')
                result.h_op, result.h_value = adjust_condition(match.group('h_op'), match.group('h_value'), is_mysql)  
            
            case "JOIN":
                result.attrs_t1 = transfer(match.group('attrs_t1'))
                result.table_1 = match.group('table_1')        
                result.attrs_t2 = transfer(match.group('attrs_t2'))
                result.table_2 = match.group('table_2')
                result.j_attr = match.group('j_attr')             

    except Exception as e:
        print("Error: ", e)

    finally:
        return result
    
    
def keywords_match(query_type: Operation, inputs: str, is_mysql: bool = True): #combine
    if query_type in Operation: #pattern check

        query_type_check = query_type_switch(query_type, inputs)

        cls = globals()[query_type_check]
        match = re.search(cls.pattern, inputs) #OPERATER class -> pattern
        return key_pharse(match, query_type.name, query_type_check, is_mysql)
    else:
        print("error")
        return None


def query_type_switch(query_type: Operation, inputs) -> str:
    temp_type = query_type.name
    match query_type:
        case Operation.SELECT_WHERE:
            if 'where' not in inputs:
                temp_type = "SELECT_NO_WHERE"
        
        case Operation.GROUP_BY:
            if 'where' not in inputs:
                temp_type = "GROUP_BY_NO_WHERE"            

        case Operation.GROUP_BY_HAVING:
            if 'having' not in inputs:
                temp_type = "GROUP_BY_HAVING_NO_HAVING"

            if 'where' not in inputs:
                temp_type = "GROUP_BY_HAVING_NO_ALL"

            if 'where' not in inputs and 'having' in inputs: 
                temp_type = "GROUP_BY_HAVING_NO_WHERE"

        case Operation.ORDER_BY:
            if 'where' not in inputs:
                temp_type = "ORDER_BY_NO_WHERE"

    return temp_type