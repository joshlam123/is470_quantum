'''
At some n, generating the list of solutions is going to take such a long time that it will be more worth to use the doubly
linked list data structure to optimize the city generation
'''
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

# Create the doubly linked list
class doubly_linked_list:

    def __init__(self):
        self.head = None
    
    def push(self, new_node):
        '''
        push takes in a value and adds it to the end of the doubly linked list
        '''
        new = Node(new_node)
        new.next = self.head
        if self.head is not None:
            self.head.prev = new
        self.head = new

    def insert(self, prev_node, new_node):
        '''
        takes in value of the previous node
        '''
        if prev_node is None:
            return
        new = Node(new_node)
        new.next = prev_node.next
        prev_node.next = new
        new.prev = prev_node
        if new.next is not None:
            new.next.prev = new
            
    def delete(self, node):
        if self.head.data == node:
            self.head = self.head.next
            self.head.prev = None
            return

        n = self.head
        while n.next is not None:
            if n.data == node:
                break;
            n = n.next
        if n.next is not None:
            n.prev.next = n.next
            n.next.prev = n.prev
        else:
            if n.data == node:
                n.prev.next = None
            else:
                print("Element not found")
                
    # Define the method to print the linked list 
    def listprint(self, node):
        while (node is not None):
            print(node.data),
            last = node
            node = node.next
            
    def get_tour(self, node):
        ordered_tour = list()
        while (node is not None):
            ordered_tour.append(node.data)
            last = node
            node = node.next
        return ordered_tour[::-1]
    
    def get_node_index(self, node):
        current=self.head
        index=1
        while current != None:
            if current.data == node:
                return index
            current = current.next
            index += 1
        return -1
    
    def get_next_node(self, node):
        next_node = None
        current=self.head
        
        # somehow need to check the last node
        
        while current.next.data != node:
            current = current.next
            
        next_node = current.data
        print(next_node)
        return next_node
        
        

# [dllist.push(i) for i in cities.keys()]

# dllist = doubly_linked_list()
# dllist.push(12)
# dllist.push(8)
# dllist.push(62)
# dllist.push(50)
# # dllist.insert(dllist.head.next, 13)
# #dllist.listprint(dllist.head)
# dllist.get_next_node(62)
