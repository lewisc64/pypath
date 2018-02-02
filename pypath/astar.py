from dijkstra import Dijkstra
import math

class Astar(Dijkstra):
    
    def __init__(self, map):
        super().__init__(map)
        map.start.cost = self.heuristic(map.start)
    
    def open_node(self, node):
        super().open_node(node)
        node.gcost = -1
        node.parent = None
    
    def heuristic(self, node):
        return math.sqrt((node.x - self.map.finish.x) ** 2 + (node.y - self.map.finish.y) ** 2)
    
    def traceback(self, current=None, links=None):
        if current == None:
            current = self.map.finish
        if links == None:
            links = []
        if current.parent is not None:
            links.append((current, current.parent))
            self.traceback(current.parent, links)
        return links
    
    def perform_step(self):
        lowest = -1
        current = None
        
        for node in self.open:
            if lowest == -1 or node.cost < lowest:
                lowest = node.cost
                current = node

        if current == self.map.finish:
            return self.traceback()
        
        self.close_node(current)
        
        for neighbour in current.neighbours:
            if neighbour[0] not in self.closed:
                if neighbour[0] not in self.open:
                    self.open_node(neighbour[0])
                gcost = current.gcost + neighbour[1]
                if gcost < neighbour[0].gcost or neighbour[0].gcost == -1:
                    neighbour[0].parent = current
                    neighbour[0].gcost = gcost
                    neighbour[0].cost = gcost + self.heuristic(neighbour[0])
        
        return None