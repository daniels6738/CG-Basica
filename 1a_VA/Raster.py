import pygame
import math

nome_geometria = 'geometria.txt'
nome_camera = 'camera.txt'

#normalizacao de vetor
def norm_vet(v):
    norm = math.sqrt(sum(x ** 2 for x in v))
    return [x / norm for x in v]


#produto vetorial de duas matrizes
def prod_mats(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

#produto matriz vetor
def prod_vet_mat(mat, vet):
    result = []
    for row in mat:
        result.append(sum(row[i] * vet[i] for i in range(len(vet))))
    return result

#converter coordenadas universais para camera
def proj_verts(verts, N, V, d, hx, hy, C):
    
    U = norm_vet(prod_mats(N, V))
    V = norm_vet(prod_mats(U, N))
    N = norm_vet(N)
    M = [U, V, N] #matriz p mudanca de base

    verts_vista = [prod_vet_mat(M, [v[i] - C[i] for i in range(3)]) for v in verts]

    verts_proj = []
    for vert in verts_vista:
        if abs(vert[2]) < 1e-5:
            vert[2] = 1e-5
        x = (d / hx) * (vert[0] / vert[2])
        y = (d / hy) * (vert[1] / vert[2])
        verts_proj.append((x, y))
    return verts_proj

#coordenadas normalizadas -> coordenadas de tela
def coordenadas_tela(verts_proj, largura, altura):
    return [
        (int((v[0] + 1) * largura / 2), int((1 - v[1]) * altura / 2))
        for v in verts_proj
    ]

def interpola(x0, y0, x1, y1):
    if y0 == y1:  #se dois vertices estao na mesma linha horizontal
        return [x0] * (y1 - y0 + 1)
    
    step = (x1 - x0) / (y1 - y0)
    return [int(x0 + i * step) for i in range(abs(y1 - y0) + 1)]

#rasterizacao scan line
def rasterizar_triangulo(surface, pontos):
    pontos = sorted(pontos, key=lambda p: p[1]) #ordena vertices por y
    p1, p2, p3 = pontos

    def desenhar_linha(y, x1, x2):
        for x in range(int(x1), int(x2) + 1):
            surface.set_at((x, y), (255, 255, 255))  #pintar de branco

    altura1 = interpola(p1[0], p1[1], p2[0], p2[1])  #ab
    altura2 = interpola(p2[0], p2[1], p3[0], p3[1])  #bc
    altura3 = interpola(p1[0], p1[1], p3[0], p3[1])  #ac

    #triangulo de cima, ate y de B
    for i, y in enumerate(range(p1[1], p2[1] + 1)):
        x_start = altura1[i]
        x_end = altura3[i]
        desenhar_linha(y, min(x_start, x_end), max(x_start, x_end))

    #triangulo de baixo
    for i, y in enumerate(range(p2[1], p3[1] + 1)):
        x_start = altura2[i]
        x_end = altura3[len(altura1) + i -1]
        desenhar_linha(y, min(x_start, x_end), max(x_start, x_end))



#desenhar cada triangulo fornecido
def desenhar_triangulos(verts_proj, triangulos):
    largura, altura = 800, 600  #resolucao
    tela = pygame.display.set_mode((largura, altura))
    tela.fill((0, 0, 0))  #inicialmente preenchendo a tela de preto

    verts_tela = coordenadas_tela(verts_proj, largura, altura)

    for triangulo in triangulos:
        pontos = [verts_tela[i - 1] for i in triangulo]
        rasterizar_triangulo(tela, pontos)

#carregar vertices e triangulos de arquivo (nome do arquivo como parametro)
def load_triangulos(arquivo):
    f = open(arquivo, "r")
    linhas = f.readlines()
    num_verts, num_triangulos = map(int, linhas[0].split())
    
    verts = [list(map(float, linhas[i + 1].split())) for i in range(num_verts)]
    
    triangulos = [list(map(int, linhas[num_verts + i + 1].split())) for i in range(num_triangulos)]
    
    return verts, [[v for v in triangulo] for triangulo in triangulos]

#carregar parametros da camera de arquivo (nome do arquivo como parametro da funcao)
def load_cam(arquivo):
    f = open(arquivo, "r")
    linhas = f.readlines()
    
    N = list(map(float, linhas[0].split('=')[1].split()))
    V = list(map(float, linhas[1].split('=')[1].split()))
    d = float(linhas[2].split('=')[1])
    hx = float(linhas[3].split('=')[1])
    hy = float(linhas[4].split('=')[1])
    C = list(map(float, linhas[5].split('=')[1].split()))
    
    return N, V, d, hx, hy, C

#pygame para visualizacao dos triangulos

verts, triangulos = load_triangulos(nome_geometria)
N, V, d, hx, hy, C = load_cam(nome_camera)
verts_proj = proj_verts(verts, N, V, d, hx, hy, C)

pygame.init()
tela = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Rasterizacao CG Basica")
desenhar_triangulos(verts_proj, triangulos)
pygame.display.update()

# Loop para recarregar os arquivos
execucao = True
while execucao:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            execucao = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  #R para recarregar os arquivos de geometria e camera
                verts, triangulos = load_triangulos(nome_geometria)
                N, V, d, hx, hy, C = load_cam(nome_camera)
                verts_proj = proj_verts(verts, N, V, d, hx, hy, C)
                desenhar_triangulos(verts_proj, triangulos)
                pygame.display.update()
            elif event.key == pygame.K_ESCAPE: #ESC pra encerrar visualizacao
                execucao = False
                pygame.quit()

