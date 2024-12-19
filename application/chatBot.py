from dataclasses import dataclass
from typing import Dict, List, Optional
from application.mysql_component import mysqlApi
from application.mysql_component.mysqlQueryBuilder import generate_sql
from application.mongo_component import mongoApi
from application.mongo_component.mongoQueryBuilder import getPipeline
from application.toolkit.sampleGenerator import RandomSentence, SampleBuilder
from application.toolkit.templateBuilder import Operation, keywords_match, Result


@dataclass
class MenuItem: #Basic Menu class
    text: str #text message
    children: Dict[str, 'MenuItem'] = None #store children menu
    handler: Optional[callable] = None #which function to do
    randomSample: Optional[RandomSentence] = None #if for Sample Query
    isQuery: bool = False # Query operation flag
    query_type: Optional[Operation] = None # Query Operation type

@dataclass
class UserState: 
    '''Store menu state info'''
    current_menu: Dict[str, MenuItem]
    menu_path: List[str]
    parent_menu: Optional[Dict[str, MenuItem]] = None

class MenuBot: #main body
    def __init__(self) -> None:
         # current type of database
        self.is_mysql: bool = None
        
        # recording user states
        self.user_states: Optional[UserState] = None

        # Obj of QueryBuilder
        self.sample_generator: Optional[SampleBuilder] = None

        # init menu tree
        self.menu_tree = {
            '1': MenuItem('Use MongoDB [NoSQL]', {
                
                '1': MenuItem(text='Show tables', handler = self.show_tables),

                '2': MenuItem(Operation.SIMPLE_SELECT.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.SIMPLE_SELECT),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.SIMPLE_SELECT.value+'}', handler = self.leaf_symbol, query_type = Operation.SIMPLE_SELECT),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                 }),

                '3': MenuItem(Operation.SELECT_WHERE.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.SELECT_WHERE),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.SELECT_WHERE.value+'}', handler = self.leaf_symbol, query_type = Operation.SELECT_WHERE),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                }),

                '4': MenuItem(Operation.GROUP_BY.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.GROUP_BY),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.GROUP_BY.value+'}', handler = self.leaf_symbol, query_type = Operation.GROUP_BY),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                }),

                '5': MenuItem(Operation.GROUP_BY_HAVING.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.GROUP_BY_HAVING),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.GROUP_BY_HAVING.value+'}', handler = self.leaf_symbol, query_type = Operation.GROUP_BY_HAVING),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                }),

                '6': MenuItem(Operation.ORDER_BY.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.ORDER_BY),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.ORDER_BY.value+'}', handler = self.leaf_symbol, query_type = Operation.ORDER_BY),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                }),

                '7': MenuItem(Operation.JOIN.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.JOIN),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.JOIN.value+'}', handler = self.leaf_symbol, query_type = Operation.JOIN),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                }),

                '0': MenuItem('Go back', handler = self.go_back)

            }, handler = self.switch_Mongo),

            '2': MenuItem('Use MySQL [SQL]', {
                
                '1': MenuItem(text='Show tables', handler=self.show_tables),

                '2': MenuItem(Operation.SIMPLE_SELECT.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.SIMPLE_SELECT),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.SIMPLE_SELECT.value+'}', handler = self.leaf_symbol, query_type = Operation.SIMPLE_SELECT),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                 }),

                '3': MenuItem(Operation.SELECT_WHERE.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.SELECT_WHERE),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.SELECT_WHERE.value+'}', handler = self.leaf_symbol, query_type = Operation.SELECT_WHERE),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                }),

                '4': MenuItem(Operation.GROUP_BY.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.GROUP_BY),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.GROUP_BY.value+'}', handler = self.leaf_symbol, query_type = Operation.GROUP_BY),
                        '0': MenuItem('Go back', handler = self.go_back)
                    }),
                    '0': MenuItem('Go back', handler = self.go_back)
                }),

                '5': MenuItem(Operation.GROUP_BY_HAVING.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.GROUP_BY_HAVING),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.GROUP_BY_HAVING.value+'}', handler = self.leaf_symbol, query_type = Operation.GROUP_BY_HAVING),
                        '0': MenuItem('Go back', handler = self.go_back) 
                    }),
                    '0': MenuItem('Go back', handler = self.go_back) 
                }),

                '6': MenuItem(Operation.ORDER_BY.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.ORDER_BY),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.ORDER_BY.value+'}', handler = self.leaf_symbol, query_type = Operation.ORDER_BY),
                        '0': MenuItem('Go back', handler = self.go_back) 
                    }),
                    '0': MenuItem('Go back', handler = self.go_back) 
                }),

                '7': MenuItem(Operation.JOIN.value, {
                    '1': MenuItem('Show Samples', query_type=Operation.JOIN),
                    '2': MenuItem('Free Input', {
                        'Please Input your Query according to Template': MenuItem('\n\t{'+Operation.JOIN.value+'}', handler = self.leaf_symbol, query_type = Operation.JOIN),
                        '0': MenuItem('Go back', handler = self.go_back) 
                    }),
                    '0': MenuItem('Go back', handler = self.go_back) 
                }),

                '0': MenuItem('Go back', handler = self.go_back),  
                
            }, handler = self.switch_SQL),
            '#': MenuItem('Exit', handler = self.exit_chat) 
        }

    
    def switch_Mongo(self): #deactivate is_mysql flag
        self.is_mysql = False
    
    def switch_SQL(self): #activate is_mysql flag
        self.is_mysql = True

    def leaf_symbol(): #symbol of menu input leaf
        pass
    
    # Get current menu
    def get_current_menu(self) -> UserState:
        if not self.user_states: #if not have one, create one
            self.user_states = UserState(
                current_menu = self.menu_tree,
                menu_path = [],
                parent_menu = None
            )
        
        return self.user_states

    # format menu options 
    def format_menu(self, menu: Dict[str, MenuItem]):
        is_homepage = False
        result = ""
        for key, item in menu.items():
            result += f" {key}. {item.text}\n"
            if item.text == 'Exit':
                is_homepage = True
        result = ("Home Page:\n" if is_homepage else "See options:\n")+ result

        return result
    
    # generate final menu item
    def createChildren(self, cur_menu: MenuItem):
        '''
        state = self.get_current_menu() # UserState
        current_menu = state.current_menu # #num: MenuItem
        _idx, menu_item = list(current_menu.items())[0] # 
        '''

        if cur_menu.query_type: #only for those Menuitem who has query_type
            cur_menu.children = dict()
        
        # Create children menuitem (sample query)
        sample_list = self.randomSentences(cur_menu.query_type)
        children: List[MenuItem] = []
        for sample_sql in sample_list:
            children.append(
                MenuItem(
                    text=sample_sql.sentence, 
                    randomSample=sample_sql,
                    handler=self.find_handler, # to query Nosql / sql database
                    isQuery=True # isQuery flag ON
                )
            )
        #add children to cur menu {
        for i, item in enumerate(children):
            cur_menu.children[str(i + 1)] = item

        # if tables have no relation
        if sample_list == []:
            cur_menu.children["\nSorry"] = MenuItem('Tables have no relation!\n', handler = self.go_back)

        cur_menu.children["0"] = MenuItem('Go back', handler = self.go_back)
        cur_menu.children["#"] = MenuItem('Go home', handler = self.go_home)
        #}

    # handler of inputs 
    def handle_input(self, user_input: str) -> str:
        '''Difference:
            current_menu: Dict[str, MenuItem]
            _idx: str
            menu_item: MenuItem
        '''
        state = self.get_current_menu()
        current_menu = state.current_menu
        _idx, menu_item = list(current_menu.items())[0]
        
        #check whether input invalid, *except for Menuitem has query_type*
        if user_input not in current_menu and menu_item.query_type is None:
            return 'Invalid input, please try again.'
        
        # Free Input 
        if menu_item.handler and menu_item.handler.__name__ == 'leaf_symbol' and user_input not in current_menu:
            Type = menu_item.query_type            
            if user_input == '0':
                return self.go_back()
            elif user_input == '#':
                return self.go_home()
            return (self.format_sql(Type, user_input) + \
                   f"Enter '0' go back, enter '#' go to home page. Or just do your next query!") \
                   if self.is_mysql else (self.format_mongo(Type, user_input) + \
                   f"\n\nEnter '0' go back, enter '#' go to home page. Or just do your next query!")

        #check menu key
        selected = current_menu[user_input]        

        #only for query sample leaf
        if self.is_query_state(selected):
            self.createChildren(selected)

        # if having child menu, update state of current menu
        if selected.children:
            state.parent_menu = current_menu
            state.current_menu = selected.children
            state.menu_path.append(user_input)
            if selected.handler:
                selected.handler() #if child has function, operate it.
            return self.format_menu(selected.children)

        # if selected is a functional node
        if selected.handler:
            #print(selected.text, str(selected.handler))
            if selected.isQuery:
                return selected.handler(selected.randomSample.query_type, selected.randomSample.sentence)
            else:
                return selected.handler()
        
        return "Error when handling input!"
    
    # go to last page
    def go_back(self) -> str:
        state = self.get_current_menu()
        if state.parent_menu:
            state.current_menu = state.parent_menu
            state.menu_path.pop()
            if state.menu_path:
                new_parent = self.menu_tree
                for choice in state.menu_path[:-1]:
                    new_parent = new_parent[choice].children
                state.parent_menu = new_parent
            else:
                state.parent_menu = None
            return self.format_menu(state.current_menu)
        return self.format_menu(self.menu_tree)

    # go to home page
    def go_home(self) -> str:
        state = self.get_current_menu()
        state.current_menu = self.menu_tree
        state.menu_path = []
        state.parent_menu = None
        return self.format_menu(self.menu_tree)
    
    #exit current chat
    def exit_chat(self) -> str:
        self.user_states = None
        self.sample_generator = None
        return "Bye~!"
    
    #test
    def test_handler(self) -> str:
        return 'test_handler has bees called succesfully.'
    
    #show tables
    def show_tables(self) -> str:
        if self.is_mysql is None:
            print('Error! No databse status!')
            return
        tables = self.sample_generator.tables # List of tables
        print([table.tableName for table in tables])
        res = ''
        if self.is_mysql:
            for table in tables:
                res += '「' + table.tableName + '」' + 'Table  :\n\n' + mysqlApi.show_tables(table=table.tableName) + '\n\n\n'
        elif not self.is_mysql:
            for table in tables:
                res += '「' + table.tableName + '」' + 'Table  :\n\n' + mongoApi.find_all(col_name=table.tableName) + '\n\n\n'
        
        #Table followed with current menu
        state = self.get_current_menu()
        
        return res + self.format_menu(state.current_menu)
    
    #function to check sample query automatically
    def find_handler(self, query_type: Operation, sentence: str) -> str:
        state = self.get_current_menu()
        if self.is_mysql:
            return self.format_sql(query_type, sentence) + self.format_menu(state.current_menu)
        return self.format_mongo(query_type, sentence) + f'\n\n' + self.format_menu(state.current_menu)
    
    #create samples
    def randomSentences(self, query_type: Operation) -> List[RandomSentence]:
        return self.sample_generator.randomSampleSenteces(query_type)
    
    #process message
    def process_message(self, message: str = None) -> str:
        if not self.sample_generator or not self.sample_generator.tables:
            return 'There\'s no tables! Please upload file first!'
        if not self.user_states:
            state = self.get_current_menu()
            return self.format_menu(state.current_menu)

        #Overall command
        message = message.strip()        

        if message == 'Exit':
            return self.exit_chat()
        if message == 'Home':
            return self.go_home()
        
        return self.handle_input(message)
    
    
    def is_query_state(self, cur_menu: MenuItem) -> bool:
        """
        Check if current status is query samples
        Usage: to distinguish handler (with variables or not), go_back have no variable
        RETURN: True if in state to receive & execute query from user
        """

        if cur_menu.text == 'Show Samples':
            return True
        return False

    # prepare for free input and extract keywords
    def free_input_api(self, query_type: Operation, inputs: str, is_mysql = True) -> Result:
        return keywords_match(query_type, inputs, is_mysql)

    # SQL out
    def format_sql(self, query_type: Operation, inputs: str): #phrase nlp 
        result = self.free_input_api(query_type, inputs.lower()) #Mysql case insensitive
        #print(result)
        format_sql = generate_sql(result)
        # print(format_sql)
        return mysqlApi.mysql_send(format_sql)

    # Mongo out
    def format_mongo(self, query_type: Operation, inputs: str): #phrase nlp 
        result = self.free_input_api(query_type, inputs, is_mysql= False)
        #print(result)
        collection_name, pipeline = getPipeline(result, query_type)
        #print(collection_name, pipeline)
        formatted_query = f'db.{collection_name}.aggregate({pipeline})'
        print(formatted_query)
        return mongoApi.aggregate(collection_name, pipeline)