'''
File name: mysqlQueryBuilder
Function: phrase_attrs, generate_sql
Comment: Use to generate sql query.
'''

from application.toolkit.templateBuilder import compare_ops, order_patterns, Result

def phrase_attrs(attrs):
    if not attrs:
        attrs = None
    else:
        if len(attrs) == 1 and attrs[0] == 'all':
            attrs = "*"
        else:
            attrs = ', '.join(attrs)

    return attrs

def generate_sql(result: Result): #生成查询
    format_sql = ""
    
    attrs = result.attrs
    if not attrs:
        attrs = None
    else:
        if len(attrs) == 1 and attrs[0] == 'all':
            attrs = "*"
        else:
            attrs = ', '.join(attrs)

    match result.keyword:
        case "SIMPLE_SELECT":
            format_sql = f'SELECT {attrs} FROM {result.table}' 
            
        case "SIMPLE_SELECT_ALL":    
            format_sql = f'SELECT * FROM {result.table}' 

        case "SELECT_WHERE":
            format_sql = f'SELECT {attrs} FROM {result.table} ' +\
                         ("" if not result.w_attr or not result.w_op or not result.w_value else \
                         f'WHERE {result.w_attr} {compare_ops.get(result.w_op, None)} {result.w_value}') 
                          

        case "GROUP_BY":  
            format_sql = f'SELECT {attrs} FROM {result.table} ' +\
                         ("" if not result.w_attr or not result.w_op or not result.w_value else \
                         f'WHERE {result.w_attr} {compare_ops.get(result.w_op, None)} {result.w_value} ') +\
                         f'GROUP BY {result.g_attr}'

        case "ORDER_BY":
            format_sql = f'SELECT {attrs} FROM {result.table} ' +\
                         ("" if not result.w_attr or not result.w_op or not result.w_value else \
                         f'WHERE {result.w_attr} {compare_ops.get(result.w_op, None)} {result.w_value} ') +\
                         f'ORDER BY {result.o_attr} {order_patterns.get(result.pattern, None)}'

        case "GROUP_BY_HAVING":  
            format_sql = f'SELECT {attrs} FROM {result.table} ' +\
                         ("" if not result.w_attr or not result.w_op or not result.w_value else \
                         f'WHERE {result.w_attr} {compare_ops.get(result.w_op, None)} {result.w_value} ') + \
                         f'GROUP BY {result.g_attr} ' +\
                         ("" if not result.h_attr or not result.h_op or not result.h_value else \
                         f'HAVING {result.h_attr} {compare_ops.get(result.h_op, None)} {result.h_value}')
            
        case "JOIN":  
            format_sql = f"SELECT " +\
                         ("" if not result.attrs_t1 or not result.table_1 else \
                         f"{ ', '.join(result.table_1+'.'+attr for attr in result.attrs_t1)}") + \
                         (', ' if result.attrs_t1 and result.table_1 and result.attrs_t2 and result.table_2 else "") + \
                         ("" if not result.attrs_t2 or not result.table_2 else \
                         f"{ ', '.join(result.table_2+'.'+attr for attr in result.attrs_t2)}") + \
                         f" FROM {result.table_1} " \
                         f"INNER JOIN {result.table_2} " \
                         f"ON {result.table_1}.{result.j_attr} = {result.table_2}.{result.j_attr}"
        
    return format_sql
