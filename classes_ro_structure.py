"""
    For accessing ragnarok's lists.
    * This code looks ugly, I'm sorry. xD *
"""

class Node:

    offset_to_next = 0x0
    offset_to_prev = 0x4
    offset_to_element = 0x8

    def __init__(self, proc, addr, game_class):
        self.proc = proc
        self.addr = addr
        self.addr_next = self.proc.read_int(self.addr + Node.offset_to_next)
        self.addr_prev = self.proc.read_int(self.addr + Node.offset_to_prev)
        self.addr_element = self.proc.read_int(self.addr + Node.offset_to_element)
        self.game_class = game_class
    
    def get_element(self):
        return self.game_class(self.proc, self.addr_element)


class LinkedList:

    offset_addr_begin = 0x0
    offset_addr_end = 0x4

    def __init__(self, proc, addr, game_class):
        self.proc = proc
        self.addr = addr
        self.addr_begin = self.proc.read_int(self.addr + (LinkedList.offset_addr_begin))
        self.addr_end = self.proc.read_int(self.addr + (LinkedList.offset_addr_end))
        self.addr_current = self.addr_begin
        self.at_end = False
        self.game_class = game_class
        self.current = Node(self.proc, self.addr_current, game_class)

    def get_current(self):
        return self.current.get_element()

    def go_next(self):
        if self.addr_current == self.addr_end:
            self.at_end = True
        if not self.at_end:
            addr_next = self.current.addr_next
            self.current = Node(self.proc, addr_next, self.game_class)
            self.addr_current = addr_next

    def has_next(self):
        return not self.at_end