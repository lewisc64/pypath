import pygame
import math
import yaml
import os
from zipfile import ZipFile
from pygame import gfxdraw
from keyboard import *
from dijkstra import Dijkstra
from astar import Astar
pygame.init()

BACKGROUND_COLOR = (220, 220, 220)
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
#background = pygame.Surface((800,600))
try:
    background = pygame.image.load("bg.png")
except:
    background = pygame.Surface((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    background.fill(BACKGROUND_COLOR)

display = pygame.display.set_mode(background.get_size())
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 15)



class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self, surface, radius, color):
        gfxdraw.aacircle(surface, self.x, self.y, radius + 1, (255, 255, 255))
        gfxdraw.aacircle(surface, self.x, self.y, radius, color)
        gfxdraw.filled_circle(surface, self.x, self.y, radius, color)
    
    def get_pos(self):
        return (self.x, self.y)
    
    def __iter__(self):
        return iter(self.get_pos())
    
    def __len__(self):
        return 2
    
    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
    
    def __setitem__(self, i, value):
        if i == 0:
            self.x = value
        elif i == 1:
            self.y = value
    
    def __tuple__(self):
        return (self.x, self.y)

class Map:
    def __init__(self, background, nodes=None, links=None):
        self.background = background
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes
        if links is None:
            self.links = []
        else:
            self.links = links
        
        self.node_radius = 4
        self.node_color = (0, 128, 255)
        self.selected_node_color = (128, 0, 255)
        self.link_width = 1
        self.link_color = (0, 0, 128)
        self.start = None
        self.start_color = (0, 128, 0)
        self.start_radius = self.node_radius * 2
        self.finish = None
        self.finish_color = (128, 0, 0)
        self.finish_radius = self.node_radius * 2
    
    def draw_background(self, surface):
        surface.blit(self.background, (0, 0))
    
    def link_grid(self):
        for node1 in self.nodes:
            for node2 in self.nodes:
                if node1 != node2:
                    dist = (node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2
                    if dist <= self.node_side ** 2 * 2:
                        found = False
                        for link in self.links:
                            if node1 in link and node2 in link:
                                found = True
                                break
                        if not found:
                            self.links.append((node1, node2))
                            self.links.append((node2, node1))
    
    @staticmethod
    def save(graph, path):
        
        image_path = "image.png"
        map_path = "map.yml"

        background = graph.background.copy()
        del graph.background
        pygame.image.save(background, image_path)
        
        map_file = open(map_path, "w")
        map_file.write(yaml.dump(graph))
        map_file.close()
        
        with ZipFile(path, "w") as zip:
            zip.write(image_path)
            zip.write(map_path)
        
        os.remove(image_path)
        os.remove(map_path)

        graph.background = background
    
    @staticmethod
    def load(path):
        
        image_path = "image.png"
        map_path = "map.yml"
        
        with ZipFile(path, "r") as zip:
            zip.extractall()
            
        image = pygame.image.load(image_path)
        
        file = open(map_path, "r")
        graph = yaml.load(file.read())
        file.close()
        graph.background = image

        os.remove(image_path)
        os.remove(map_path)

        return graph
    
    def draw_nodes(self, surface, selected=None):
        if selected is None:
            selected = []
        for node in self.nodes:
            #pygame.draw.circle(surface, self.node_color, node, self.node_radius)
            if node in selected:
                color = self.selected_node_color
            else:
                color = self.node_color
            node.draw(surface, self.node_radius, color)
        
        if self.start is not None:
            gfxdraw.aacircle(surface, self.start.x, self.start.y, self.start_radius, self.start_color)
            gfxdraw.aacircle(surface, self.start.x, self.start.y, self.start_radius - 1, self.start_color)
        if self.finish is not None:
            gfxdraw.aacircle(surface, self.finish.x, self.finish.y, self.finish_radius, self.finish_color)
            gfxdraw.aacircle(surface, self.finish.x, self.finish.y, self.finish_radius - 1, self.finish_color)
        
        
    def draw_links(self, surface, links=None, color=None, thickness=1):
        if links is None:
            links = self.links
        if color is None:
            color = self.link_color
        for link in links:
            if thickness == 1:
                pygame.draw.aalines(surface, color, False, link)
            else:
                pygame.draw.lines(surface, color, False, link, thickness)
        
    def get_nodes(self, x, y):
        out = []
        for node in self.nodes:
            dist = math.sqrt((node.x - x) ** 2 + (node.y - y) ** 2)
            if dist <= self.node_radius:
                out.append(node)
        return out
    
    def get_nodes_in_rect(self, rect):
        out = []
        for node in self.nodes:
            if node.x >= rect[0] and node.x <= rect[0] + rect[2]:
                if node.y >= rect[1] and node.y <= rect[1] + rect[3]:
                    out.append(node)
        return out
    
    def delete_node(self, node):
        self.nodes.remove(node)
        for link in self.links[:]:
            if node in link:
                self.links.remove(link)
        if self.start == node:
            self.start = None
        if self.finish == node:
            self.finish = None

def wait():
    run = True
    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.KEYUP:
                run = False
        pygame.display.update()

def grid_editor(graph):
    
    keybindings = {"graph_editor":pygame.K_g}
    
    width = display.get_width()
    height = display.get_height()
    
    if not hasattr(graph, "node_side"):
        graph.node_side = 20
        #for x in range(0, width, graph.node_side):
        #    for y in range(0, height, graph.node_side):
        #        graph.nodes.append(Node(x + graph.node_side // 2, y + graph.node_side // 2))
    
    while True:
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif e.type == pygame.KEYUP:
                
                if e.key == keybindings["graph_editor"]:
                    graph.link_grid()
                    graph.background = display.copy()
                    return graph
        
        buttons = pygame.mouse.get_pressed()
        if buttons != (False, False, False):
            pos = pygame.mouse.get_pos()
            box = (pos[0] // graph.node_side * graph.node_side, pos[1] // graph.node_side * graph.node_side, graph.node_side, graph.node_side)
            if buttons[0]:
                for node in graph.get_nodes_in_rect(box):
                    graph.delete_node(node)
            elif buttons[2]:
                if len(graph.get_nodes_in_rect(box)) == 0:
                    graph.nodes.append(Node(box[0] + box[2] // 2, box[1] + box[3] // 2))
                    
        display.fill((0, 0, 0))
        for node in graph.nodes:
            pygame.draw.rect(display, (255, 255, 255), (node.x - graph.node_side // 2, node.y - graph.node_side // 2, graph.node_side, graph.node_side))
        
        #for x in range(0, width, map.node_side):
        #    pygame.draw.line(display, (128, 128, 128), (x, 0), (x, height))
        #for y in range(0, height, map.node_side):
        #    pygame.draw.line(display, (128, 128, 128), (0, y), (width, y))
        
        pygame.display.update()
        clock.tick(60)

def graph_editor(graph):
    global display
    
    keybindings = {"link":pygame.K_l,
                   "unlink":pygame.K_u,
                   "delete":pygame.K_DELETE,
                   "set_start":pygame.K_s,
                   "set_finish":pygame.K_f,
                   "grid_editor":pygame.K_g,
                   "select_all":pygame.K_a,
                   "save":pygame.K_s,
                   "open":pygame.K_o,
                   "new":pygame.K_n}
                   
    algorithms = {pygame.K_1:Dijkstra,
                  pygame.K_2:Astar}
                  
    selected = []
    
    held_point = None
    drag_box = False
    box = [0, 0, 0, 0]
    
    while True:
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif e.type == pygame.KEYUP:
                
                if e.key == keybindings["link"] or e.key == keybindings["unlink"]:
                    for node1 in selected[:]:
                        for node2 in selected[:]:
                            if node1 != node2:
                                link = (node1, node2)
                                if e.key == keybindings["link"]:
                                    if link not in graph.links:
                                        graph.links.append(link)
                                else:
                                    if link in graph.links:
                                        graph.links.remove(link)
                    selected = []
                    
                elif e.key == keybindings["delete"]:
                    for node in selected:
                        graph.delete_node(node)
                    selected = []
                    
                elif e.key == keybindings["set_start"]:
                    if len(selected) == 1:
                        graph.start = selected[0]
                        selected = []
                        
                elif e.key == keybindings["set_finish"]:
                    if len(selected) == 1:
                        graph.finish = selected[0]
                        selected = []
                
                elif e.key == keybindings["grid_editor"]:
                    grid_editor(graph)
                
                else:
                    if e.key in algorithms:
                        solver = algorithms[e.key](graph)
                        links = solver.step_through(display)
                        graph.draw_links(display, links, (0, 255, 0), thickness=3)
                        wait()
                        
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    
                    if e.key == keybindings["select_all"]:
                        selected = graph.nodes
                    
                    elif e.key == keybindings["save"]:
                        path = get_string(display, "name?: ") + ".zip"
                        Map.save(graph, path)
                    
                    elif e.key == keybindings["open"]:
                        path = get_string(display, "name?: ") + ".zip"
                        graph = Map.load(path)
                        display = pygame.display.set_mode(graph.background.get_size())
                    
                    elif e.key == keybindings["new"]:
                        graph = Map(background.copy())
                        display = pygame.display.set_mode(graph.background.get_size())
            
            elif e.type == pygame.MOUSEBUTTONDOWN:
                
                if e.button == 1:
                    held_point = e.pos
                    drag_box = False
                    box = [held_point[0], held_point[1], 0, 0]
            
            elif e.type == pygame.MOUSEBUTTONUP:
                
                if e.button == 1:
                    
                    held_point = None
                    
                    if drag_box:
                        
                        if pygame.key.get_mods() == 0:
                            selected = []
                        drag_box = False
                        
                        for node in graph.get_nodes_in_rect(box):
                            if pygame.key.get_mods() & pygame.KMOD_ALT:
                                if node in selected:
                                    selected.remove(node)
                            elif node not in selected:
                                selected.append(node)
                        
                        box = [0, 0, 0, 0]
                        
                    else:
                        
                        nodes = graph.get_nodes(*e.pos)
                        if len(nodes) == 0:
                            selected = []
                        elif nodes[0] not in selected:
                            selected.append(nodes[0])
                        else:
                            selected.remove(nodes[0])
                        
                elif e.button == 3:
                    graph.nodes.append(Node(*e.pos))
            
            elif e.type == pygame.MOUSEMOTION:
                
                if held_point is not None:
                    current_point = e.pos
                    x = min(current_point[0], held_point[0])
                    y = min(current_point[1], held_point[1])
                    width = abs(current_point[0] - held_point[0])
                    height = abs(current_point[1] - held_point[1])
                    box = [x, y, width, height]
        
        if held_point is not None:
            drag_box = box[2] > 0 or box[3] > 0
        
        graph.draw_background(display)
        graph.draw_links(display)
        graph.draw_nodes(display, selected)
        if drag_box:
            pygame.draw.rect(display, (0, 0, 0), box, 1)
            pygame.draw.rect(display, (255, 255, 255), [box[0] + 1, box[1] + 1, box[2] - 2, box[3] - 2], 1)
        
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    graph_editor(Map(background.copy()))
