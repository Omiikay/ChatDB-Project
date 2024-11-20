from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MenuItem:
    text: str
    children: Dict[str, 'MenuItem'] = None
    handler: Optional[callable] = None
    # TODO: extract and list attributes

@dataclass
class UserState:
    '''Store menu state info'''
    current_menu: Dict[str, MenuItem]
    menu_path: List[str]
    parent_menu: Optional[Dict[str, MenuItem]] = None

class MenuBot:
    def __init__(self) -> None:
        # recording user states
        self.user_states: Optional[UserState] = None

        # init menu tree
        self.menu_tree = {
            '1': MenuItem('Use MongoDB [NoSQL]', {

                ''' 
                Show supportted Queries, gernerate with randomly picked attributes   
                    like:
                        here's some sample of queries supportted so far, please enter as the template suggest:
                        1. find the info (or specify by <name>) of customers who lives in <city name>
                            1.1 find the info of (all) customers who lives in (la)
                        2. show the <VendorName> whose company loacated at <country> 
                        ...
                        0. Go back to the home menu.
                '''
                '1': MenuItem('Simple Search Query', handler = self.test_handler), # TODO: set handler
                '2': MenuItem('Aggregate Search Query', handler = self.test_handler), # TODO: set handler
                '3': MenuItem(' Query', handler = self.test_handler), # TODO: set handler
                #TODO: implement more
                
                '0': MenuItem('Exit', handler = self.go_back)# TODO: set handler
            }),
            '2': MenuItem('Use MySQL [SQL]', {
                '1': MenuItem('Simple Search Query', handler = self.test_handler), # TODO: set handler
                '2': MenuItem('Aggregate Search Query', handler = self.test_handler), # TODO: set handler
                '3': MenuItem(' Query', handler = self.test_handler), # TODO: set handler

                '0': MenuItem('Exit', handler = self.go_back)# TODO: set handler
            })
        }
    
    # Get current menu
    def get_current_menu(self) -> UserState:
        if not self.user_states:
            self.user_states = UserState(
                current_menu = self.menu_tree,
                menu_path = [],
                parent_menu = None
            )
        
        return self.user_states

    # format menu options 
    def format_menu(self, menu: Dict[str, MenuItem]):
        result = "See options:\n"
        for key, item in menu.items():
            result += f"\t{key}. {item.text}\n"
        return result

    # handler of inputs 
    def handle_input(self, user_input: str) -> str:
        state = self.get_current_menu()
        current_menu = state.current_menu

        if user_input not in current_menu:
            return 'Invalid input, please try again.'

        selected = current_menu[user_input]

        # if having child menu, update state of current menu
        if selected.children:
            state.parent_menu = current_menu
            state.current_menu = selected.children
            state.menu_path.append(user_input)
            return self.format_menu(selected.children)

        # if selected is a functional node
        if selected.handler:
            return selected.handler()
        
        return "Error when handling input!"
    
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
    
    def test_handler(self) -> str:
        return 'test_handler has bees called succesfully.'
    
    def go_home(self) -> str:
        state = self.get_current_menu()
        state.current_menu = self.menu_tree
        state.menu_path = []
        state.parent_menu = None
        return self.format_menu(self.menu_tree)

    def process_message(self, message: str = None) -> str:
        state = self.get_current_menu()
        if not message or message.strip() in ['', 'Home']:
            return self.format_menu(state.current_menu)
        return self.handle_input(message.strip())