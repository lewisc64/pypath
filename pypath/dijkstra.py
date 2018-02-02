import pygame
import math

class Dijkstra:
    def __init__(self, map):
        self.map = map
        self.open = []
        self.closed = []
        self.open_node(map.start)
    
    def open_node(self, node):
        node.neighbours = []
        node.cost = 0
        for link in self.map.links:
            if link[0] == node:
                node.neighbours.append([link[1], math.sqrt((node.x - link[1].x) ** 2 + (node.y - link[1].y) ** 2)])
        self.open.append(node)
    
    def close_node(self, node):
        self.open.remove(node)
        self.closed.append(node)
    
    def traceback(self, current=None, previous=None, links=None):
        if current == None:
            current = self.map.finish
        if links == None:
            links = []
        
        lowest = -1
        next = None
        for neighbour in current.neighbours:
            if neighbour[0] != previous:
                if lowest == -1 or neighbour[0].cost + neighbour[1] < lowest:
                    next = neighbour[0]
                    lowest = next.cost + neighbour[1]
        
        links.append((current, next))
        
        if next.cost != 0:
            self.traceback(next, current, links)
        
        return links
        
    
    def perform_step(self):
        lowest = -1
        current = None
        
        for node in self.open:
            if lowest == -1 or node.cost < lowest:
                lowest = node.cost
                current = node
        
        self.close_node(current)
        
        for neighbour in current.neighbours:
            if neighbour[0] not in self.closed:
                if neighbour[0] not in self.open:
                    self.open_node(neighbour[0])
                    neighbour[0].cost = current.cost + neighbour[1]
                else:
                    cost = neighbour[1] + current.cost
                    if cost < neighbour[0].cost:
                        neighbour[0].cost = cost
        
        if not self.open or self.map.finish in self.closed:
            return self.traceback()
        return None
    
    def step_through(self, surface):
        background = surface.copy()
        clock = pygame.time.Clock()
        while True:
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif e.type == pygame.KEYUP:
                    if e.key == pygame.K_RETURN:
                        return self.solve()
            
            out = self.perform_step()
            
            surface.blit(background, (0, 0))
            for node in self.open:
                node.draw(surface, self.map.node_radius, (0, 255, 0))
            for node in self.closed:
                node.draw(surface, self.map.node_radius, (255, 0, 0))
            
            if out is not None:
                return out
            
            pygame.display.update()
            clock.tick(10)
    
    def solve(self):
        while True:
            out = self.perform_step()
            if out is not None:
                return out