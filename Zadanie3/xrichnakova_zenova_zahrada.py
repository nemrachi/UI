import random
import pathlib
import time
import copy

# trieda zahrady
class Zen_Garden:
    # garden_size = velkost zahrady [sirka, vyska], stone_num = pocet kamenov v zahrade, print_garden_bool = rozhoduje, ci sa ma tlacit zahrada pocas hrabania
    def __init__(self, garden_size = [], stones_num = None, print_garden_bool = False):
        self.width = 0 # sirka zahrady
        self.height = 0 # vyska zahrady
        self.stones_num = 0 # pocet kamenov
        self.print_garden_bool = print_garden_bool

        self.garden_map = [] # mapa zahrady
        self.STONE = -1 # zapis kamena v zahrade
        self.SAND = 0 # zapisa piesku v zahrade

        if garden_size == [] and stones_num == None and print_garden_bool == False:
            # ak neboli vlozene ziadne hodoty do triedy, vytvori zahradu podla prikladu v zadani
            self.generate_garden_from_assigment()
        else:  
            # inak vytvori zahradu so zadanymi parametrami
            if garden_size:
                self.width = int(garden_size[0])
                self.height = int(garden_size[1])
            if stones_num:
                self.stones_num = int(stones_num)
            else: # ak nebol zadany pocet kamenov, vygeneruje nahodne
                self.stones_num = random.randrange(1, int((self.height * self.width)/4))

            self.generate_garden()

        self.rakeable_fields_num = (self.height * self.width) - self.stones_num # pocet poli, ktore mozu byt pohrabane
        self.half_perimeter = self.width + self.height # polobvod zahrady
        
    # vygeneruje zahrady
    def generate_garden(self): 
        self.fill_garden_with_stones_and_sand()

    # vygeneruje zahradu zo zadania
    def generate_garden_from_assigment(self):
        self.width = 12
        self.height = 10
        self.stones_num = 6
        self.fill_garden_with_stones_and_sand([(1, 5), (2, 1), (3, 4), (4, 2), (6, 8), (6, 9)]) # presna poloha kamenov

    # naplni zahradu pieskom a kamenmi
    def fill_garden_with_stones_and_sand(self, stones_position = []):
        self.fill_garden_with_sand()

        uniq_pos = dict() # struktura dictionary, ktora zabezpeci unikatne vygenerovanie polohy kamenov

        if not stones_position: # ak neboli zadane pozicie kamenov, tak ich nahodne vygeneruje
            while len(uniq_pos) != self.stones_num: # generuje polohy kamenov, pokial ich nie je tolko co kamenov
                rand_X = random.randrange(0, self.height)
                rand_Y = random.randrange(0, self.width)
                uniq_pos[(rand_X, rand_Y)] = 1

            for pos in uniq_pos:
                stones_position.append(pos)

        else: # ak boli zadane pozicie kamenov
            if len(stones_position) > self.stones_num: # ak je zadanych viac poloh kamenov ako pocet kamenov
                reminder = len(stones_position) - self.stones_num
                stones_position = stones_position[:reminder]

            elif len(stones_position) < self.stones_num: # ak je zadanych menej poloh kamenov ako pocet kamenov
                reminder = stones_num - len(stones_position)
                while len(uniq_pos) != reminder: # vygeneruje chybajuce polohy
                    rand_X = random.randrange(0, self.height)
                    rand_Y = random.randrange(0, self.width)
                    uniq_pos[(rand_X, rand_Y)] = 1

                for pos in uniq_pos:
                    stones_position.append(pos)

        for pos in stones_position: # pouklada kamene do zahrady
            self.garden_map[pos[0]][pos[1]] = self.STONE

        stones_position.clear()

    # naplni zahradu pieskom
    def fill_garden_with_sand(self):
        for i in range(self.height):
            self.garden_map.append([self.SAND] * self.width)

    # vytlaci zahradu
    def print_garden(self, garden = None):
        if garden == None:
            garden = self.garden_map
        # vypise hodnoty zapisane v zahrade
        print("Zenova zahradka (K = kamen, P = piesok)")
        print("------------------------")
        for row in garden:
            for r in row:
                if r == self.SAND:
                    print("P", end ="\t".replace('\t', ' '*(3-len('P'))))
                elif r == self.STONE:
                    print("K", end ="\t".replace('\t', ' '*(3-len('K'))))
                else:
                    print(str(r), end ="\t".replace('\t', ' '*(3-len(str(r)))))
            print("")
        print("------------------------")

    # skopiruje list listov, ktory predstavuje zahradu
    def copy_garden(self) -> list:
        monks_garden = [] # zahrada, do ktorej sa kopiruje povodna nepohrabana zahrada
        i = 0
        for slice_list in self.garden_map:
            monks_garden.append([])
            for element in slice_list:
                monks_garden[i].append(element)
            i += 1

        return monks_garden

    # pohrabanie zahrady; chromosome = predstavuje chromozom mnicha, ktory predstavuje vstupne body do zahrady
    # mnich moze vstupovat zo vsetkych stran zahrady 
    def rake_garden(self, chromosome : list) -> int:
        coordinate = {} # suradnice [vyska, sirka]
        new_coordinate = {} # nove suradnice [vyska, sirka]
        prev_coordinate = {} # predosle suradnice [vyska, sirka]
        crossing_num = 1 # cislo prechodu mnicha
        crossing_list = [] # list prechodov mnicha
        monks_garden = self.copy_garden() # skopiruje nepohrabanu zahradu pre kazdeho mnicha zvlast
        stuck_monk = False # uviaznutie mnicha

        for i in range(len(chromosome)): # mnich vstupuje do zahrady
            coordinate = self.get_direction(chromosome[i]) # podla cisla vstupu do zahrady vrati presne pole v zahrade

            if monks_garden[coordinate['row']][coordinate['col']] == self.SAND: # je volny vstup do zahrady?
                while self.is_field_in_garden(coordinate['row'], coordinate['col']): # pokial sa nachadza policko v zahrade, moze hrabat
                    if monks_garden[coordinate['row']][coordinate['col']] == self.SAND: # ak je policko piesok
                        monks_garden[coordinate['row']][coordinate['col']] = crossing_num # zaznaci prechod cez policko
                        new_coordinate = {'row': coordinate['row'] + coordinate['move'][0], 'col': coordinate['col'] + coordinate['move'][1], 
                                            'move': coordinate['move']}
                        prev_coordinate = coordinate
                        coordinate = new_coordinate

                    else: # ak narazi (cize objavi sa na policku s prekazkou)
                        coordinate = self.solve_colission(chromosome[i], monks_garden, prev_coordinate) # zisti, kam sa ma pohnut podla genu
                        if coordinate['move'] == None: # ak nema moznost pohybu nikam
                            if not self.is_field_in_garden(coordinate['row'], coordinate['col']): # ak sa zasekol pri kraji zahrady
                                break # uspesne konci
                            else: # ak narazil na dalsiu prekazku
                                stuck_monk = True
                                break # neuspesne konci

                if stuck_monk:
                    break

                crossing_num += 1

        if self.print_garden_bool:
            self.print_garden(monks_garden) # vytlaci zahradu, ak je to povolene

        return self.count_raked_fields(monks_garden)

    # spocita pocet pohrabanych policok
    def count_raked_fields(self, garden: list) -> int:
        unraked_count = 0 # pocet nepohrabanych
        for i in range(self.height):
            for j in range(self.width):
                if garden[i][j] == self.SAND:
                    unraked_count += 1
        return self.rakeable_fields_num - unraked_count

    def solve_colission(self, genome: int, garden: list, coor: dict()) -> dict():
        if coor['move'][0] == 0: # ak sa mnich presuval medzi stlpcami
            up = dict()
            up['move'] = [-1, 0]
            up['row'] = coor['row'] + up['move'][0]
            up['col'] = coor['col']

            down = dict()
            down['move'] = [1, 0]
            down['row'] = coor['row'] + down['move'][0]
            down['col'] = coor['col']

            if genome > 0: # ak je kladny gen, pojde hore
                if (self.is_field_in_garden(up['row'], up['col'])) and (garden[up['row']][up['col']] == self.SAND):
                    return up
                else: # ak nie je volne hore, pozrie sa este dole
                    if (self.is_field_in_garden(down['row'], down['col'])) and (garden[down['row']][down['col']] == self.SAND):
                        return down
                    else: # ak sa nema kde pohnut, nehybe sa
                        down['move'] = None
                        return down

            else: # ak je zaporny gen, pojde dole
                if (self.is_field_in_garden(down['row'], down['col'])) and (garden[down['row']][down['col']] == self.SAND):
                    return down
                else: # ak nie je volne dole, pozrie sa este hore
                    if (self.is_field_in_garden(up['row'], up['col'])) and (garden[up['row']][up['col']] == self.SAND):
                        return up
                    else: # ak sa nema kde pohnut, nehybe sa
                        up['move'] = None
                        return up

        elif coor['move'][1] == 0: # ak sa mnich presuval medzi riadkami
            right = dict()
            right['move'] = [0, 1]
            right['row'] = coor['row']
            right['col'] = coor['col'] + right['move'][1]

            left = dict()
            left['move'] = [0, -1]
            left['row'] = coor['row']
            left['col'] = coor['col'] + left['move'][1]
            if genome > 0: # ak je kladny gen, pojde doprava
                if (self.is_field_in_garden(right['row'], right['col'])) and (garden[right['row']][right['col']] == self.SAND):
                    return right
                else: # ak nie je volne vpravo, pozrie sa este dolava
                    if (self.is_field_in_garden(left['row'], left['col'])) and (garden[left['row']][left['col']] == self.SAND):
                        return left
                    else: # ak sa nema kde pohnut, nehybe sa
                        left['move'] = None
                        return left

            else: # ak je zaporny gen, pojde dolava
                if (self.is_field_in_garden(left['row'], left['col'])) and (garden[left['row']][left['col']] == self.SAND):
                        return left
                else: # ak nie je volne vlavo, pozrie sa este doprava
                    if (self.is_field_in_garden(right['row'], right['col'])) and (garden[right['row']][right['col']] == self.SAND):
                        return right
                    else: # ak sa nema kde pohnut, nehybe sa
                        right['move'] = None
                        return right
 
    # podla cisla vstupu do zahrady vrati presne pole v zahrade
    def get_direction(self, num: int) -> dict():
        num = abs(num)
        if num <= self.width: # ak je cislo z hornej hrany
            return {'row': 0, 'col': (num - 1), 'move': [1, 0]}
        elif num <= self.half_perimeter: # ak je cislo z pravej hrany
            return {'row': (num - self.width - 1), 'col': (self.width - 1), 'move': [0, -1]}
        elif num <= (self.half_perimeter + self.width): # ak je cislo z dolnej hrany
            return {'row': (self.height - 1), 'col': (self.half_perimeter + self.width - num), 'move': [-1, 0]}
        else: # ak je cislo z lavej hrany
            return {'row': ((self.half_perimeter * 2) - num), 'col': 0, 'move': [0, 1]}

    def is_field_in_garden(self, row: int, col: int) -> bool:
        if (0 <= row < self.height) and (0 <= col < self.width):
            return True
        else:
            return False

# trieda evolucneho algoritmu
class Evolution_algorithm:
    # metoda krizenia - two-point (rozdelenie chromozomu na 3 casti)
    # vyber rodicov - turnament 2 jedincov
    def __init__(self, garden: Zen_Garden):
        # konstanty
        self.POPULATION_SIZE = 40 # velkost populacie
        self.CROSSOVER_RATE = 0.95 # sanca na krizenie
        self.GENERATIONS_MAX = 2500 # maximalny pocet generacii
        self.MUTATION_MIN_PERC = 0.1 # minimalne % mutacie
        self.MUTATION_MAX_PERC = 0.5 # maximalne % mutacie

        self.garden = garden # instancia triedy Zen_garden
        self.genome_num = self.get_num_of_genome() # pocet genomov sa rovna polovici obvodu zahrady + pocet kamenov
        self.population = [] # 2d pole pre populaciu (pole chromozonov celej populacie)
        self.start_time = 0
        self.end_time = 0

        self.start_time = time.time() # zaciatok casu vykonania algoritmu
        self.generate_first_population()
        self.generations_evolution()       

    # vyvoj generacii 
    def generations_evolution(self):
        population_fitness = [] # list fitnesov pre kazdeho jedinca
        generation_counter = 0 # pocet zbehnutych generacii
        mutation_value = self.MUTATION_MIN_PERC # vybrane percento mutacie
        max_fitness = 0 # najvyssia dosiahnuta fitnes
        max_i = 0 # index jedinca s maximalnou fitness
        prev_max_fitness = 0 # predosla najvyssia dosiahnuta fitnes
        same_max_fitness_counter = 0

        while generation_counter < self.GENERATIONS_MAX:
            monks = [[0 for i in range(self.POPULATION_SIZE)] for j in range(self.genome_num)] # list mnichov jednotlivcov
            i = 0
            for pop in self.population:
                # pohrabanie zahrady populaciou a zistenie fitnes kazdeho jedinca
                # vlozi sa chromozon mnicha do funkcie rake_garden()
                population_fitness.append(self.garden.rake_garden(pop))

            max_fitness = max(population_fitness)
            max_i = population_fitness.index(max_fitness)      

            if max_fitness == self.garden.rakeable_fields_num or generation_counter == self.GENERATIONS_MAX - 1: # ak najlepsi mnich pohrabal vsetky policka
                print('V generacii ',generation_counter ,' najlepsi mnich pohrabal', max_fitness,' z ', self.garden.rakeable_fields_num)  
                self.end_time = time.time()
                self.garden.print_garden_bool = True
                self.garden.rake_garden(self.population[max_i]) # vypise pohrabanu celu zahradu
                print('Vitazny chromozom: ', self.population[max_i])
                self.garden.print_garden_bool = False
                print('Cas trvania evolucie: ', (self.end_time - self.start_time))
                break # koniec

            # uprava hodnot mutacie, ak sme uz dlho vo fitnes v lokalnom maxime
            if (max_fitness != prev_max_fitness) or (mutation_value >= self.MUTATION_MAX_PERC):
                # ak sa zvysila maximalna fitnes alebo percento mutacie prekrocilo maximalnu stanovenu hodnou
                prev_max_fitness = max_fitness # zapis si novu maximalne fitnes
                mutation_value = self.MUTATION_MIN_PERC # zresetuj percento mutacie
            else:
                same_max_fitness_counter += 1
                if mutation_value < self.MUTATION_MAX_PERC:
                    mutation_value += 0.01

            if same_max_fitness_counter == int(self.POPULATION_SIZE):
                self.population = self.population[:int(self.POPULATION_SIZE/2)]
                self.generate_first_population(int(self.POPULATION_SIZE - int(self.POPULATION_SIZE/2)))
                same_max_fitness_counter = 0

						
            self.generate_new_population(population_fitness, mutation_value, max_i)
            population_fitness.clear()

            generation_counter += 1

    #vytvorenie novej generacie
    def generate_new_population(self, population_fitness: list, mutation_value: float, max_i: int):
        children = [] # deti aktualnej generacie
        for i in range(self.POPULATION_SIZE):
            children.append([0] * self.genome_num)

        for i in range(0, self.POPULATION_SIZE, 2):
            monk1 = self.tournament(population_fitness) # index 1.rodica 
            monk2 = self.tournament(population_fitness) # index 2.rodica 

            if (random.uniform(0, 1) < self.CROSSOVER_RATE): # krizenie
                index_limit1 = int(random.uniform(0, 1) * self.genome_num) # index, po ktory sa bude sekat 1.cast chromozomu
                index_limit2 = int(random.uniform(0, 1) * self.genome_num) # index, po ktory sa bude sekat 2.cast chromozomu

                if index_limit1 > index_limit2:
                    tmp = index_limit1
                    index_limit1 = index_limit2
                    index_limit2 = tmp

                if index_limit1 == 0:
                    index_limit1 = 1
                if index_limit1 == self.genome_num:
                    index_limit1 = self.genome_num - 2
                    index_limit2 = self.genome_num - 1
                if index_limit2 == 0:
                    index_limit1 = 1
                    index_limit2 = 2
                if index_limit2 == self.genome_num:
                    index_limit2 = self.genome_num - 1

                # rodicov monk1 a monk2 rozdeli na 3 casti
                # 1.potomkovi ide 1.cast 1.rodica + 2.cast 2.rodica + 3.cast 1.rodica 
                # 2.potomkovi ide 1.cast 2.rodica + 2.cast 1.rodica + 3.cast 2.rodica 
                children[i][0:index_limit1] = self.population[monk1][0:index_limit1]
                children[i][index_limit1:index_limit2] = self.population[monk2][index_limit1:index_limit2]
                children[i][index_limit2:self.genome_num] = self.population[monk1][index_limit2:self.genome_num]
                children[i + 1][0:index_limit1] = self.population[monk2][0:index_limit1]
                children[i + 1][index_limit1:index_limit2] = self.population[monk1][index_limit1:index_limit2]
                children[i + 1][index_limit2:self.genome_num] = self.population[monk2][index_limit2:self.genome_num]

                for child in range(2):
                    for j in range(self.genome_num):
                        if (random.uniform(0, 1) < mutation_value):
                            genome_mutation = int(random.uniform(0, 1) * ((self.garden.half_perimeter) * 2) - 1) + 1
                            if random.randrange(0, 10) < 5:
                                # sanca 50%, ze vygeneruje bud kladne alebo zaporne cislo -> to ovplyvni vyber smeru pri zrazke s prekazkou 
                                genome_mutation *= -1

                            indexes_duplicate_value = self.list_duplicates_of(children[i + child], genome_mutation)
                            if indexes_duplicate_value == []: # ak sa nenasiel duplikat cisla genome_muation
                                children[i + child][j] = genome_mutation # zmutuje dany gen
                            else: # vymeny geny na indexoch
                                tmp = children[i + child][j]
                                children[i + child][j] = children[i + child][indexes_duplicate_value[0]]
                                children[i + child][indexes_duplicate_value[0]] = tmp

            else: # ak sa nekrizi, tak len kopiruje jedincov do novej generacie
                for j in range(self.genome_num):
                    children[i][j] = self.population[monk1][j]
                    children[i+1][j] = self.population[monk2][j]

        for i in range(self.genome_num): # eliarizmus, ulozime si toho najlepsieho
            children[0][i] = self.population[max_i][i]

        self.copy_new_population(children)
        children.clear()

    # skopiruje list listov, ktory predstavuje novu populaciu
    def copy_new_population(self, new_population: list):
        self.population.clear()
        i = 0
        for slice_list in new_population:
            self.population.append([])
            for element in slice_list:
                self.population[i].append(element)
            i += 1

    # vyber 2 rodicov turnamentom
    def tournament(self, population_fitness: list) -> int:
        monk1 = int(random.uniform(0, 1) * self.POPULATION_SIZE) # random index z populacie
        monk2 = int(random.uniform(0, 1) * self.POPULATION_SIZE) # random index z populacie
        if population_fitness[monk1] > population_fitness[monk2]:
            return monk1
        else:
            return monk2

    # vygeneruje 1 chromozon
    def generate_chromosome(self) -> list:
        chromosome = [] # list genov = chromozom
        perimeter_numbers = [] # cisla z obvodu zahrady (od 1 po 2*(sirka + vyska))

        for i in range(1, ((self.garden.half_perimeter) * 2) + 1):
            perimeter_numbers.append(i)

        random.shuffle(perimeter_numbers) # nahodne rozhodi cisla celeho obvodu

        for i in range(self.genome_num): # prvych n (= pocet genomov) vlozi do chromozonu
            num = perimeter_numbers[i]
            if random.randrange(0, 10) < 5:
                # sanca 50%, ze vygeneruje bud kladne alebo zaporne cislo -> to ovplyvni vyber smeru pri zrazke s prekazkou 
                num *= -1

            chromosome.append(num)

        return chromosome

    # vygeneruje prvu populaciu
    def generate_first_population(self, pop_size = 0):
        if pop_size == 0:
            pop_size = self.POPULATION_SIZE
        for i in range(pop_size):
            self.population.append(self.generate_chromosome())

    def get_num_of_genome(self) -> int: # funkcia vrati pocet genov v chromozome
        return self.garden.half_perimeter + self.garden.stones_num

    def list_duplicates_of(self, l: list, item: int) -> list:
        return [i for i, x in enumerate(l) if x == item]


# main funckia
def main():
    file_name = pathlib.Path(__file__).parent.absolute()
    file_name = str(file_name) + "\\zen_garden_parameters.txt"
    print("Zadanie 3 - Zenova zahrada\n")
    print("Parametre zenovej zahrady su zapisane v textovom subore\n", file_name,"\nv tvare \'sirka(int) vyska(int) kamene(int) vypis_zahrady(bool)\'")

    try:
        with open(file_name, 'r') as f: # otvorenie suboru s parametrami zenovej zahrady
            lines = f.readlines() # ulozenie jednotlivych riadkov do listu

        for line in lines:
            garden_size = [] # list so sirkou a vyskou zahrady
            stones_num = None # pocet kamenov v zahrade
            print_garden = False

            param = line.split()
            print('\nNova zahrada', param)
            for i in range(len(param)):
                if i == 0:
                    garden_size.append(int(param[i])) # sirka zahrady
                elif i == 1:
                    garden_size.append(int(param[i])) # vyska zahrady
                elif i == 2:
                    if param[i].isdigit():
                        stones_num = int(param[i]) # pocet kamenov
                    else:
                        if param[i] == 'True':
                            print_garden = True
                        elif param[i] == 'False':
                            print_garden = False
                elif i == 3:
                    if param[i] == 'True':
                            print_garden = True
                    elif param[i] == 'False':
                        print_garden = False

            garden = Zen_Garden(garden_size=garden_size, stones_num=stones_num, print_garden_bool=print_garden) # vytvorenie zahrady
            Evolution_algorithm(garden) # spustenie evolucneho algoritmu

    except (IOError, FileNotFoundError) as e: # eror, ak nemoze subor najst alebo precitat
        print("\n\tERROR: Subor ", file_name," sa nenasiel, zahrada bude vytvorena podla predlohy zo zadania\n")
        garden = Zen_Garden() # vytvorenie zahrady
        Evolution_algorithm(garden) # spustenie evolucneho algoritmu

main()