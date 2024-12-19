from typing import Dict, List, Optional
from application.toolkit.templateBuilder import Operation, Result
from application.constant import NUM
from string import Template
from dataclasses import dataclass

import numpy as np
import pandas as pd
import random

@dataclass
class RandomSimple:
    """class of simple query"""
    table: str
    sentence: str
    condition: Dict = None
    projection: Optional[Dict] = None

@dataclass(frozen=True)
class RandomSentence:
    """class of simple query"""
    query_type: Operation
    sentence: str

@dataclass
class Table:
    """class of table object"""
    tableName: str
    fields_str: Optional[List[str]] = None # save string fields
    fields_num: Optional[List[str]] = None # save number fields
    df: Optional[pd.DataFrame] = None # save df obtained in app

compare_ops = [ 'equals', 'unequals', 'greater than', 'less than',
               'greater than or equals', 'less than or equals'
               ]
compare_ops_str = ['equals', 'unequals']

order_patterns = ['descending','ascending']

class SampleBuilder:
    def __init__(self):
        # 用于存储查询条件
        self.tables: Optional[List[Table]] = None # All upload tables info as Table Class

    def randomSampleSenteces(self, query_type: Operation) -> List[RandomSentence]:
        """Return list of RandomSentence"""
        #k = 3 and len(pairs) > 3 are all -> need to define sample generate constant
        sentences : List[RandomSentence] = []

        if query_type == Operation.JOIN:
            random_attrs = self.randomJoinAttrs()
            # tables have no relation
            if random_attrs == []:
                return []
            
        else:
            random_tables = random.choices(self.tables, k=NUM) # random table obj
            random_attrs = self.randomResultAttrs(random_tables, query_type)
        for result in random_attrs:
            sentences.append(RandomSentence(query_type, self.generateSentence(result, query_type)))

        unique_sentences = list(set(sentences))
        #print(random_attrs)
        #print(sentences)
        return unique_sentences     

    def randomJoinAttrs(self) -> List[Result]:
        pairs: Dict[tuple, List] = {}
        results: List[Result] = []
        for i, tb in enumerate(self.tables):
            if len(pairs) > NUM:
                break

            for j in range(i + 1, len(self.tables)):
                inter = [] 
                if (i, j) not in pairs:
                    pairs[(i, j)] = []
                inter.extend(list(set(tb.fields_str) & set(self.tables[j].fields_str)))
                inter.extend(list(set(tb.fields_num) & set(self.tables[j].fields_num)))
                if inter:
                    pairs[(i, j)].extend(inter)
                if len(pairs) > NUM:
                    break

        # print(pairs)
        #clean empty pairs
        del_pair_keys = [ key for key, value in pairs.items() if value == [] ]
        for key in del_pair_keys:
            del pairs[key]

        #tables has no relation
        if len(pairs) == 0:
            return []
        
        random_tables = random.choices(list(pairs.keys()), k=min(NUM, len(pairs))) # radom table obj
        for k, v in random_tables: 
            result = Result(keyword="JOIN", table_1=self.tables[k].tableName, table_2=self.tables[v].tableName)
            flt_k = set(self.tables[k].fields_str) | set(self.tables[k].fields_num)
            flt_v = set(self.tables[v].fields_str) | set(self.tables[v].fields_num)
            flt_k.discard(None)
            flt_v.discard(None)

            attr1 = [random.choice(list(flt_k))]
            attr2 = [random.choice(list(flt_v))]

            j_attr = random.choice(pairs[(k, v)])
            result.attrs_t1, result.attrs_t2, result.j_attr = attr1, attr2, j_attr
            results.append(result)
            #print(result)
        #print(results)
        return results # the same type with random_attrs from randomResultAttrs

    def randomResultAttrs(self, tables: List[Table], query_type: Operation) -> List[Result]:
        """Return 3 random attrs in Result class"""
        random_attrs: List[Result] = []
        for i, table in enumerate(tables):
            random_attrs.append(self.singleResultAttr(i, table, query_type))
        return random_attrs
    

    def singleResultAttr(self, num: int, table: Table, query_type: Operation) -> Result:
        """
        build onr Result based on query_type
        Given: table obj, # of samples (0: all, 1: str_fields, 2: num_fields)
        Return Result
        """
        result = Result(keyword=query_type.name, table=table.tableName)
   
        # random idx and choose the value from df
        # also choose specific projection attrs
        df = table.df
        random_index = np.random.randint(0, len(df))
        
        #Since we only show 3, there are three types
        match(num):
            case 0: # select all
                result.attrs = ['all']
            case 1: # select num(if not, str) attrs
                if not table.fields_num:
                    result.attrs = random.sample(table.fields_str, min(len(table.fields_str), 2))
                else:
                    result.attrs = random.sample(table.fields_num, min(len(table.fields_num), 2))
            case 2: # select str(if not, num) attrs
                if not table.fields_str:
                    result.attrs = random.sample(table.fields_num, min(len(table.fields_num), 2))
                else:
                    result.attrs = random.sample(table.fields_str, min(len(table.fields_str), 2))
        
        match(query_type):
            case Operation.SIMPLE_SELECT:
                pass # no other attrs
            
            case Operation.SELECT_WHERE:
                field_type = random.randint(0, 1) # 0: num field, 1: str field
                result.w_attr, result.w_op, result.w_value \
                    = self.getRandomWhereCondition(table, field_type, random_index)
            
            case Operation.ORDER_BY:
                field_type = random.randint(0, 1) # 0: num field, 1: str field
                # add Where condition
                result.w_attr, result.w_op, result.w_value \
                    = self.getRandomWhereCondition(table, field_type, random_index)
                
                result.o_attr = self.getRandomField(table, field_type)
                result.pattern = random.choice(order_patterns)
            
            case Operation.GROUP_BY:
                field_type = random.randint(0, 1) # 0: num field, 1: str field
                # add Where condition
                result.w_attr, result.w_op, result.w_value \
                    = self.getRandomWhereCondition(table, field_type, random_index)
                result.g_attr = self.getRandomField(table, field_type)
            
            case Operation.GROUP_BY_HAVING:
                field_type = random.randint(0, 1) # 0: num field, 1: str field
                # add Where condition
                result.w_attr, result.w_op, result.w_value \
                    = self.getRandomWhereCondition(table, field_type, random_index)
                result.g_attr = self.getRandomField(table, field_type)
                # add Group by Having condition
                result.h_attr, result.h_op, result.h_value \
                    = self.getRandomWhereCondition(table, field_type, random_index)

            case _: 
                raise ValueError(f"singleResultAttr error: {query_type}")
                
        return result
    

    def getRandomField(self, table: Table, field_type: int) -> str:
        """Return a random field name given # 0: num field, 1: str field"""
        if not table.fields_str:
            field = random.choice(table.fields_num)
        elif not table.fields_num:
            field = random.choice(table.fields_str)
        else:
            field1 = random.choice(table.fields_str)
            field2 = random.choice(table.fields_num)
            if field_type == 1:
                field = field1
            else:
                field = field2

        return field
    

    def getRandomWhereCondition(self, table: Table, field_type: int, random_index) -> List:
        """Return a random field name given # 0: num field, 1: str field"""
        df = table.df

        if not table.fields_str:
            field = random.choice(table.fields_num)
        elif not table.fields_num:
            field = random.choice(table.fields_str)
        else:
            field1 = random.choice(table.fields_str)
            field2 = random.choice(table.fields_num)
            if field_type == 1:
                field = field1
            else:
                field = field2

        if not table.fields_str or (table.fields_num and field_type == 0):
            ops = random.choice(compare_ops)
        else:
            ops = random.choice(compare_ops_str)

        value = df[field].iloc[random_index]

        return [field, ops, value]
    
     
    def generateSentence(self, result: Result, query_type: Operation) -> str:
        formatted_string = None
        #join all the list attr
        if result.attrs:
            result.attrs = ', '.join(result.attrs)
        if result.attrs_t1:
            result.attrs_t1 = ', '.join(result.attrs_t1)
        if result.attrs_t2:
            result.attrs_t2 = ', '.join(result.attrs_t2)

        match(query_type):
            case Operation.SIMPLE_SELECT:
                simple_sentence = Template(Operation.SIMPLE_SELECT.value)
                formatted_string = simple_sentence.substitute(
                    attrs = result.attrs,
                    table = result.table
                )
            case Operation.SELECT_WHERE:
                simple_sentence = Template(Operation.SELECT_WHERE.value)
                formatted_string = simple_sentence.substitute(
                    attrs = result.attrs, 
                    table = result.table, 
                    w_attr = result.w_attr, 
                    w_op = result.w_op, 
                    w_value = result.w_value
                )
            case Operation.GROUP_BY:
                simple_sentence = Template(Operation.GROUP_BY.value)
                formatted_string = simple_sentence.substitute(
                    attrs = result.attrs, 
                    table = result.table, 
                    w_attr = result.w_attr, 
                    w_op = result.w_op, 
                    w_value = result.w_value,
                    g_attr = result.g_attr
                )
            case Operation.GROUP_BY_HAVING:
                simple_sentence = Template(Operation.GROUP_BY_HAVING.value)
                formatted_string = simple_sentence.substitute(
                    attrs = result.attrs, 
                    table = result.table, 
                    w_attr = result.w_attr, 
                    w_op = result.w_op, 
                    w_value = result.w_value,
                    g_attr = result.g_attr,
                    h_attr = result.h_attr,
                    h_op = result.h_op,
                    h_value = result.h_value
                )
            case Operation.ORDER_BY:
                simple_sentence = Template(Operation.ORDER_BY.value)
                formatted_string = simple_sentence.substitute(
                    attrs = result.attrs, 
                    table = result.table, 
                    w_attr = result.w_attr, 
                    w_op = result.w_op, 
                    w_value = result.w_value,
                    o_attr = result.o_attr,
                    pattern = result.pattern
                )
            case Operation.JOIN:
                simple_sentence = Template(Operation.JOIN.value)
                formatted_string = simple_sentence.substitute(
                    attrs_t1 = result.attrs_t1,
                    table_1 = result.table_1,
                    attrs_t2 = result.attrs_t2,
                    table_2 = result.table_2,
                    j_attr = result.j_attr
                )
            case _:
                raise ValueError(f"Unknown Query Type: {query_type}")
            
        return formatted_string

    #no use 
    def formatValue(self, value: str) -> bool:
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
