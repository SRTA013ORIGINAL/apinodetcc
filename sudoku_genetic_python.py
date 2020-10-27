from math import sqrt
from random import shuffle, randint
import argparse

def same_column_indexes(tabuleiro, i, j, N, itself=True):
    """
        essa função cria indexes dos elementos que estão na mesma coluna dos indexes de entrada
    """

    sub_grid_column = i % N
    cell_column = j % N

    for a in range(sub_grid_column, len(tabuleiro), N):
        for b in range(cell_column, len(tabuleiro), N):
            if (a, b) == (i, j) and not itself:
                continue

            yield (a, b)


def same_row_indexes(tabuleiro, i, j, N, itself=True):
    """
    essa função cria os indexes dos elementos que estao na mesma linha dos indexes de entrada
    """

    sub_grid_row = int(i / N)
    cell_row = int(j / N)

    for a in range(sub_grid_row * N, sub_grid_row * N + N):
        for b in range(cell_row * N, cell_row * N + N):
            if (a, b) == (i, j) and not itself:
                continue

            yield (a, b)


def get_cells_from_indexes(grid, indexes):
    """
    essa funcao produz valores de uma lista de indexes do grid
    """

    for a, b in indexes:
        yield grid[a][b]


def resolucao(tabuleiro, populacao_size=1000, selecao_rate=0.5, max_generations_count=1000, taxa_mutacao=0.05):
    """
   resolve quebra cabeça do sudoku por algoritmo genetico
    """

    # square root of the problem grid's size
    N = int(sqrt(len(tabuleiro)))

    def grid_vazia(gera_elemento=None):
        """
            Retorna uma grade de Sudoku vazia
        """

        return [
            [
                (None if gera_elemento is None else gera_elemento(i, j))
                for j in range(len(tabuleiro))
            ] for i in range(len(tabuleiro))
        ]

    def copia_tabuleiro(grid):
        """
        Returns a deep copy of the grid argument.

        Parameters:
            - grid (list)
        """

        return grid_vazia(lambda i, j: grid[i][j])

    # this is done to avoid changes in the input argument
    tabuleiro = copia_tabuleiro(tabuleiro)

    def same_sub_grid_indexes(i, j, itself=True):
        """
        A generator function that yields indexes of the elements that are in the same sub-grid as the input indexes.

        Parameters:
            - i (int): Sub-grid's index.
            - j (int): Sub-grid's element index.
            - itself (bool) (optional=True): Indicates whether to yield the input indexes or not.
        """

        for k in range(len(tabuleiro)):
            if k == j and not itself:
                continue

            yield (i, k)

    def preenche_cel_determinadas():
        """
        Fills some predetermined cells of the Sudoku grid using a pencil marking method.
        See the paper for more details.

        Raises:
            - Exception: The puzzle is not solvable.
        """

        # TODO: Implement the hidden cell finder.

        track_grid = grid_vazia(lambda *args: [val for val in range(1, len(tabuleiro) + 1)])

        def marca_de_lapis(i, j):
            """
            Marks the value of grid[i][j] element in it's row, column and sub-grid.

            Parameters:
                - i (int): Sub-grid's index.
                - j (int): Sub-grid's element index.

            Returns: The more completed version of the grid.
            """

            # remove from same sub-grid cells
            for a, b in same_sub_grid_indexes(i, j, itself=False):
                try:
                    track_grid[a][b].remove(tabuleiro[i][j])
                except (ValueError, AttributeError) as e:
                    pass

            # remove from same row cells
            for a, b in same_row_indexes(tabuleiro, i, j, N, itself=False):
                try:
                    track_grid[a][b].remove(tabuleiro[i][j])
                except (ValueError, AttributeError) as e:
                    pass

            # remove from same column cells
            for a, b in same_column_indexes(tabuleiro, i, j, N, itself=False):
                try:
                    track_grid[a][b].remove(tabuleiro[i][j])
                except (ValueError, AttributeError) as e:
                    pass

        for i in range(len(tabuleiro)):
            for j in range(len(tabuleiro)):
                if tabuleiro[i][j] is not None:
                    marca_de_lapis(i, j)

        while True:
            anything_changed = False

            for i in range(len(tabuleiro)):
                for j in range(len(tabuleiro)):
                    if track_grid[i][j] is None:
                        continue

                    if len(track_grid[i][j]) == 0:
                        raise Exception('The puzzle is not solvable.')
                    elif len(track_grid[i][j]) == 1:
                        tabuleiro[i][j] = track_grid[i][j][0]
                        marca_de_lapis(i, j)

                        track_grid[i][j] = None

                        anything_changed = True

            if not anything_changed:
                break

        return tabuleiro

    def gera_populacao_inicial():
        """
        Generates an initial populacao of size "populacao_size".

        Returns (list): An array of candidato grids.
        """

        candidatos = []
        for k in range(populacao_size):
            candidato = grid_vazia()
            for i in range(len(tabuleiro)):
                sub_grid_embaralhado = [n for n in range(1, len(tabuleiro) + 1)]
                shuffle(sub_grid_embaralhado)

                for j in range(len(tabuleiro)):
                    if tabuleiro[i][j] is not None:
                        candidato[i][j] = tabuleiro[i][j]

                        sub_grid_embaralhado.remove(tabuleiro[i][j])

                for j in range(len(tabuleiro)):
                    if candidato[i][j] is None:
                        candidato[i][j] = sub_grid_embaralhado.pop()

            candidatos.append(candidato)

        return candidatos

    def fitness(grid):
        """
        Calculates the fitness function for a grid.

        Parameters:
            - grid (list)

        Returns (int): The value of the fitness function for the input grid.
        """

        cont_linhas_duplicadas = 0

        # calculate rows duplicates
        for a, b in same_column_indexes(tabuleiro, 0, 0, N):
            row = list(get_cells_from_indexes(grid, same_row_indexes(tabuleiro, a, b, N)))

            cont_linhas_duplicadas += len(row) - len(set(row))

        return cont_linhas_duplicadas

    def selecao(candidatos):
        """
        Returns the best portion ("selecao_rate") of candidatos based on their fitness function values (lower ones).

        Parameters:
            - candidatos (list)

        Returns (list)
        """

        # TODO: Probabilistically selecao.

        index_fitness = []
        for i in range(len(candidatos)):
            index_fitness.append(tuple([i, fitness(candidatos[i])]))

        index_fitness.sort(key=lambda elem: elem[1])

        selected_part = index_fitness[0: int(len(index_fitness) * selecao_rate)]
        indexes = [e[0] for e in selected_part]

        return [candidatos[i] for i in indexes], selected_part[0][1]

    preenche_cel_determinadas()

    populacao = gera_populacao_inicial()
    best_fitness = None

    for i in range(max_generations_count):
        populacao, best_fitness = selecao(populacao)

        if i == max_generations_count - 1 or fitness(populacao[0]) == 0:
            break

        shuffle(populacao)
        nova_populacao = []

        while True:
            solucao1, solucao2 = None, None

            try:
                solucao1 = populacao.pop()
            except IndexError:
                break

            try:
                solucao2 = populacao.pop()
            except IndexError:
                nova_populacao.append(solucao2)
                break

            cruzamento = randint(0, len(tabuleiro) - 2)

            sub_grid_temp = solucao1[cruzamento]
            solucao1[cruzamento] = solucao2[cruzamento + 1]
            solucao2[cruzamento + 1] = sub_grid_temp

            nova_populacao.append(solucao1)
            nova_populacao.append(solucao2)

        # mutation
        for candidato in nova_populacao[0:int(len(nova_populacao) * taxa_mutacao)]:
            sub_grid_aleatorio = randint(0, 8)
            trocas_possiveis = []
            for index_elemento in range(len(tabuleiro)):
                if tabuleiro[sub_grid_aleatorio][index_elemento] is None:
                    trocas_possiveis.append(index_elemento)
            if len(trocas_possiveis) > 1:
                shuffle(trocas_possiveis)
                primeiro_index = trocas_possiveis.pop()
                segundo_index = trocas_possiveis.pop()
                tmp = candidato[sub_grid_aleatorio][primeiro_index]
                candidato[sub_grid_aleatorio][primeiro_index] = candidato[sub_grid_aleatorio][segundo_index]
                candidato[sub_grid_aleatorio][segundo_index] = tmp

        populacao.extend(nova_populacao)

    return populacao[0], best_fitness


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("board", help="Input board that contains Sudoku's problem.")
    populacao_size=10000
    selecao_rate=0.5
    max_generations_count=1000
    taxa_mutacao=0.05
    args = parser.parse_args()
    try:
        linhas_tabuleiro = args.board.split(',')
        tabuleiro = [[] for i in range(len(linhas_tabuleiro))]
        sqrt_n = int(sqrt(len(linhas_tabuleiro)))
        for j in range(len(linhas_tabuleiro)):
            valor_linha = [(int(value) if value != '0' else None) for value in linhas_tabuleiro[j].strip().split(' ')]
            for i in range(len(valor_linha)):
                tabuleiro[
                    int(i / sqrt_n) +
                    int(j / sqrt_n) * sqrt_n
                    ].append(valor_linha[i])
        try:
            solucao, best_fitness = resolucao(
                tabuleiro,
                populacao_size=populacao_size,
                selecao_rate=selecao_rate,
                max_generations_count=max_generations_count,
                taxa_mutacao=taxa_mutacao
            )
            #output_str = "Best fitness value: " + str(best_fitness) + '\n\n'
            output_str = ""
            for a, b in same_column_indexes(solucao, 0, 0, sqrt_n):
                if(output_str != ""):
                    output_str += ","
                else:
                    output_str = "["
                row = list(get_cells_from_indexes(solucao, same_row_indexes(solucao, a, b, sqrt_n)))
                output_str += " ".join([str(row)])
            output_str += "]"
            print(output_str)

        except:
            exit('Input problem is not solvable.')
    except:
        exit("Any error")