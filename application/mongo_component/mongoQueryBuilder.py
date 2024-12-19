from typing import Any, Dict, List
from application.toolkit.templateBuilder import Operation, Result
from application.constant import DB_NAME

order_patterns = {
    'descending': -1, 
    'ascending': 1
}

query_template = {
    'collection': '',
    'projection': {},
    'match': {},
    'group': {},
    'having': {},
    'joins': [],
    'sort': {}
}

# 支持的操作符映射
compare_ops = {
    'equals': '$eq',
    'unequals': '$ne',
    'greater than': '$gt',
    'less than': '$lt',
    'greater than or equals': '$gte',
    'less than or equals': '$lte',
    # 'in': '$in',
    # 'not in': '$nin',
    # 'like': '$regex'
}

def parse_query(result: Result, query_type: Operation) -> Dict[str, Any]:
    """
    解析用户输入的查询字符串，返回MongoDB查询字典
    Args: result: Result
    Returns: Dict包含MongoDB查询的各个组件
    """
    query_dict = query_template.copy()
    query_dict['collection'] = result.table if result.table else result.table_1

    # Projection
    if result.attrs and result.attrs_t1 and result.attrs_t2:
        _to_proj = list(set(result.attrs) | set(result.attrs_t1 + result.attrs_t2))
    elif result.attrs:
        _to_proj = result.attrs
    elif result.attrs_t1 and result.attrs_t2:
        _to_proj = result.attrs_t1 + result.attrs_t2
    query_dict['projection'] = { attr: 1 for attr in _to_proj if attr != 'all' }

    # Where
    if result.w_attr and result.w_op and result.w_value:
        query_dict['match'] = parse_condition(result.w_attr, result.w_op, result.w_value)

    # Group by
    if result.g_attr:
        query_dict['group'] = {
            '_id': {attr: f'${attr}' for attr in result.g_attr},
        } if type(result.g_attr) == list else {
            '_id': {f'{result.g_attr}': f'${result.g_attr}'}
        }
        
        # 添加投影中的聚合字段
        if result.attrs and ('all' not in result.attrs):
            print(result.attrs, len(result.attrs))
            reserve = result.attrs
            if result.h_attr in result.attrs:
                reserve = result.attrs + [result.h_attr]
            
            for attr in reserve:
                if attr not in [result.g_attr, 'all']:
                    query_dict['group'][attr] = {'$first': f'${attr}'}
        # else:
        query_dict['group']['doc'] = {'$first': "$$ROOT"}

    # Having
    if result.h_attr and result.h_op and result.h_value:
        query_dict['having'] = parse_condition(result.h_attr, result.h_op, result.h_value)
        
    # Order by
    if result.o_attr:
        query_dict['sort'] = {
            result.o_attr: order_patterns.get(result.o_attr, 1)
        }
    
    # Inner join
    if result.attrs_t1 and result.table_1 and result.attrs_t2 and result.table_2 and result.j_attr:
        query_dict['joins'] = build_mongodb_join_query(
            result.attrs_t1, result.table_1, result.attrs_t2, result.table_2, result.j_attr
        )
    return query_dict

def build_mongodb_join_query(attrs_t1, table_1, attrs_t2, table_2, j_attr):
    """构建MongoDB的aggregate查询"""
    try:
        # 构建MongoDB aggregate pipeline
        pipeline = [
            {
                '$lookup': {
                    'from': f'{DB_NAME}.{table_2}',
                    # 'from': table_2,
                    'localField': j_attr,
                    'foreignField': j_attr,
                    'as': 'joined_data'
                }
            },{
                '$unwind': "$joined_data"
            }
        ]
        
        # 构建投影，包含两个表的属性
        projection = {'_id': 0}
        
        # 添加第一个表的属性
        for attr in attrs_t1:
            projection[attr] = 1
            
        # 添加第二个表的属性（从joined_data中获取）
        for attr in attrs_t2:
            projection[attr] = f'$joined_data.{attr}'

        pipeline.append({'$project': projection})

        return pipeline
    
    except Exception as e:
        raise ValueError(f"Create mongo Join failure: {str(e)}")
    
def parse_condition(attr: str, op: str, value: str) -> Dict[str, Any]:
        """解析条件子句（where或having）"""
        try:
            # 尝试转换为数字
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit() and value.count('.') == 1:
                value = float(value)
            # 处理布尔值
            elif value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            # 处理数组
            elif value.startswith('[') and value.endswith(']'):
                value = eval(value)
        except:
            # 如果转换失败，保持字符串类型
            pass
            
        # 构建查询条件
        if op in compare_ops:
            mongo_op = compare_ops[op]
            return {attr: {mongo_op: value}}
        else:
            raise ValueError(f"Unsupported operator: {op}")

def build_pipeline(query_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    将查询字典转换为MongoDB聚合管道
    优化的管道顺序：
    1. $lookup (join)
    2. $unwind (join结果展开)
    3. $match (where)
    4. $group (group by)
    5. $match (having)
    6. $sort (order by)
    7. $project (投影)
    Args: query_dict: 解析后的查询字典
    Returns: List[Dict]表示MongoDB聚合管道
    """
    pipeline = []
    
    # 1. 添加join阶段（$lookup）
    if query_dict['joins']:
        pipeline.extend(query_dict['joins'])
        
    # 2. 添加match阶段（where条件）
    if query_dict['match']:
        pipeline.append({'$match': query_dict['match']})
        
    # 3. 添加group阶段
    if query_dict['group']:
        pipeline.append({'$group': query_dict['group']})
        pipeline.append({'$replaceRoot': {'newRoot': "$doc"}})
        
    # 4. 添加having阶段
    if query_dict['having']:
        pipeline.append({'$match': query_dict['having']})
        
    # 5. 添加sort阶段
    if query_dict['sort']:
        pipeline.append({'$sort': query_dict['sort']})
        
    # 6. 最后添加project阶段（投影）
    print('if query_dict[joins] ==', query_dict['joins'])
    if not query_dict['joins'] and query_dict['projection']:
        # 如果是分组查询，需要调整投影字段的路径
        if query_dict['group']:
            adjusted_projection = {'_id': 0}
            for field in query_dict['projection']:
                adjusted_projection[field] = 1
                
                if field in query_dict['group']['_id']:
                    adjusted_projection[field] = f'$_id.{field}'
                else:
                    adjusted_projection[field] = 1
                
            pipeline.append({'$project': adjusted_projection})
        else:
            pipeline.append({'$project': query_dict['projection']})
        
    return pipeline

def getPipeline(result: Result, query_type: Operation) -> tuple[str, List[Dict[str, Any]]]:
    query_dict = parse_query(result, query_type)
    pipeline = build_pipeline(query_dict)
    print('query_dict[collection], pipeline', query_dict['collection'], pipeline)
    return query_dict['collection'], pipeline
