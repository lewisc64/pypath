import pygame

keys = {pygame.K_a:"a",
        pygame.K_b:"b",
        pygame.K_c:"c",
        pygame.K_d:"d",
        pygame.K_e:"e",
        pygame.K_f:"f",
        pygame.K_g:"g",
        pygame.K_h:"h",
        pygame.K_i:"i",
        pygame.K_j:"j",
        pygame.K_k:"k",
        pygame.K_l:"l",
        pygame.K_m:"m",
        pygame.K_n:"n",
        pygame.K_o:"o",
        pygame.K_p:"p",
        pygame.K_q:"q",
        pygame.K_r:"r",
        pygame.K_s:"s",
        pygame.K_t:"t",
        pygame.K_u:"u",
        pygame.K_v:"v",
        pygame.K_w:"w",
        pygame.K_x:"x",
        pygame.K_y:"y",
        pygame.K_z:"z",
        pygame.K_1:"1",
        pygame.K_2:"2",
        pygame.K_3:"3",
        pygame.K_4:"4",
        pygame.K_5:"5",
        pygame.K_6:"6",
        pygame.K_7:"7",
        pygame.K_8:"8",
        pygame.K_9:"9",
        pygame.K_0:"0",
        pygame.K_SPACE:" ",
        pygame.K_MINUS:("-", "_")}

for key, value in keys.items():
    if type(value) is str:
        keys[key] = (value, value.upper())

def get_string(display, prompt="input: "):
    
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Consolas", 16)
    out = ""
    
    blinker = True
    frames = 0
    
    while True:
        
        frames += 1
        if frames % 30 == 0:
            blinker = not blinker
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return out
                elif e.key == pygame.K_BACKSPACE:
                    out = out[:-1]
                else:
                    i = 0
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        i = 1
                    if e.key in keys:
                        out += keys[e.key][i]
        
        display.fill((255, 255, 255))
        
        text = prompt + out
        if blinker:
            text += "_"
        display.blit(font.render(text, 1, (0, 0, 0)), (10, 10))
        
        pygame.display.update()
        clock.tick(60)
    
if __name__ == "__main__":
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    get_string(display)
