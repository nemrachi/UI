import random
import pathlib
import time

class Zen_Garden:
    def __init__(self, garden_size = [], stones_num = None): # garden_size = velkost zahrady (sirka x vyska), stone_num = pocet kamenov v zahrade
        self.width = 0
        self.height = 0
        self.stones_num = 0

        self.garden_map = []
        self.STONE = -1
        self.SAND = 0

        if garden_size == [] and stones_num == None:
            # ak neboli vlozene ziadne hodoty do triedy, vytvori zahradu podla prikladu v zadani
            self.generate_garden_from_assigment()
        else:  
            # inak vytvori zahradu so zadanymi parametrami
            if garden_size:
                self.width = int(garden_size[0])
                self.height = int(garden_size[1])
            if stones_num:
                self.stones_num = int(stones_num)

            self.generate_garden()

        self.rakeable_fields_num = (self.height * self.width) - self.stones_num # pocet poli, ktore mozu byt pohrabane
        self.half_perimeter = self.width + self.height
        
    def generate_garden(self):
        self.fill_garden_with_stones_and_sand()

    def generate_garden_from_assigment(self):
        self.width = 12
        self.height = 10
        self.stones_num = 6
        self.fill_garden_with_stones_and_sand([(1, 5), (2, 1), (3, 4), (4, 2), (6, 8), (6, 9)])

    def fill_garden_with_stones_and_sand(self, stones_position = []):
        # naplni zahradu pieskom a kamenmi
        self.fill_garden_with_sand()

        uniq_pos = dict() # struktura dictionary, ktora zabezpeci unikatne vygenerovanie polohy kamenov

        if not stones_position:
            # ak neboli zadane pozicie kamenov, tak ich nahodne vygeneruje
            while len(uniq_pos) != self.stones_num:
                rand_X = random.randrange(0, self.height)
                rand_Y = random.randrange(0, self.width)
                uniq_pos[(rand_X, rand_Y)] = 1

            for pos in uniq_pos:
                stones_position.append(pos)

        else:
            if len(stones_position) > self.stones_num:
                reminder = len(stones_position) - stones_num
                stones_position = stones_position[:reminder]

            elif len(stones_position) < self.stones_num:
                reminder = stones_num - len(stones_position)
                while len(uniq_pos) != reminder:
                    rand_X = random.randrange(0, self.height)
                    rand_Y = random.randrange(0, self.width)
                    uniq_pos[(rand_X, rand_Y)] = 1

                for pos in uniq_pos:
                    stones_position.append(pos)

        for pos in stones_position: # pouklada kamene
            self.garden_map[pos[0]][pos[1]] = self.STONE

    def fill_garden_with_sand(self): # rozsype vsade piesok
        self.garden_map = [] # zresetuje najprv zahradu
        for i in range(self.height):
            self.garden_map.append([self.SAND] * self.width)

    def print_garden(self):
        # vypise hodnoty zapisane v zahrade
        print("\nZenova zahradka")
        print("------------")
        for row in self.garden_map:
            print(row)
        print("------------")

    def get_num_of_genome(self):
        return self.half_perimeter + self.stones_num

    def rake_garden(self, chromosome : list, console_print = True) -> int:
        coordinate = {} # suradnice (vyska x sirka)
        new_coordinate = {} # suradnice (vyska x sirka)
        prev_coordinate = {} # suradnice (vyska x sirka)
        crossing_num = 1 # cislo prechodu mnicha
        crossing_list = [] # list prechodov mnicha
        monks_garden = self.garden_map # skopiruje vzor zahrady pre kazdeho mnicha zvlast
        stuck_monk = False # uviaznutie mnicha
        print_garden = console_print

        for i in range(len(chromosome)):
            coordinate = self.get_direction(chromosome[i])

            # moze vojst do zahrady?
            if monks_garden[coordinate['row']][coordinate['col']] == self.SAND:
                # pokial je policko v zahrade, hrabe
                while is_field_in_garden(coordinate['row'], coordinate['col']):
                    # ak narazi
                    if monks_garden[coordinate['row']][coordinate['col']] != self.SAND:
                        coordinate = self.solve_colission(chromosome[i], monks_garden)


                    # zaznaci prechod medzi polickami
                    monks_garden[coordinate['row']][coordinate['col']] = crossing_num
                    new_coordinate = {'row': coordinate['row'] + coordinate['move'][0], 'col': coordinate['col'] + coordinate['move'][1], 
                                        'move': coordinate['move'], 'prev_coor': [coordinate['row'], coordinate['col']]}
                    coordinate = new_coordinate

                crossing_num += 1
                stuck_monk = False

                if print_garden:
                    print_garden_map(monks_garden)

    def solve_colission(self, genome: int, garden: list) -> dict():
        new_coordinate = dict()
        pass

    def get_direction(self, num: int) -> dict():
        if num <= self.width:
            return {'row': 0, 'col': num - 1, 'move': [1, 0], 'prev_coor': [None, None]}
        elif num <= self.half_perimeter:
            return {'row': num - self.width - 1, 'col': self.width - 1, 'move': [0, -1], 'prev_coor': [None, None]}
        elif num <= (self.half_perimeter + self.width):
            return {'row': self.height - 1, 'col': self.half_perimeter + self.width - num, 'move': [-1, 0], 'prev_coor': [None, None]}
        else:
            return {'row': (self.half_perimeter * 2), 'col': 0, 'move': [0, 1], 'prev_coor': [None, None]}

    def is_field_in_garden(self, row: int, col: int) -> bool:
        if (0 <= row < self.height) and (0 <= col < self.width):
            return True
        else:
            return False

    def print_garden_map(self, garden: list):
        for row in garden:
            print(row)

        


class Evolution_algorithm:
    # metoda krizenia - two-point
    # vyber rodicov - turnament - 2 rodicia
    def __init__(self, garden):
        # konstanty
        self.POPULATION_SIZE = 40 # velkost populacie
        self.CROSSOVER_RATE = 0.95 # sanca na krizenie
        self.GENERATIONS_MAX = 5000 # maximalny pocet generacii
        self.MUTATION_MIN_PERC = 0.05 # minimalne % mutacie
        self.MUTATION_MAX_PERC = 0.4 # maximalne % mutacie

        self.garden = garden # instancia triedy Zen_garden
        self.genome_num = self.garden.get_num_of_genome # pocet genomov sa rovna polovici obvodu zahrady + pocet kamenov
        self.population = [[0 for i in range(self.POPULATION_SIZE)] for j in range(self.genome_num)] # 2d pole pre populaciu (pole genomov celej populacie)
        self.solution = [0] * self.genome_num # vysledok

        genetic()

    def genetic(self):
        start_time = time.time() # zaciatok casu vykonania programu

        self.generate_starting_population() # vygeneruje zaciatocnu populaciu

        self.generations_evolution() # vyvoj generacie



        pass

    def generations_evolution(self):
        population_fitness = [0] * self.POPULATION_SIZE # list fitnesov pre kazdeho jedinca
        generation_counter = 0 # pocet zbehnutych generacii
        mutation_value = self.MUTATION_MIN_PERC # vybrane percento mutacie
        prev_max_fitness = 0 # druha najvyssia dosiahnuta fitnes

        while generation_counter < self.GENERATIONS_MAX:
            monks = [[0 for i in range(self.POPULATION_SIZE)] for j in range(self.genome_num)] # list mnichov jednotlivcov
            max_fitness = 0 # najvyssia dosiahnuta fitnes
            local_max = 0
            min_fitness = 0
            sum_fitness = 0

            for i in range(self.POPULATION_SIZE):
                # pohrabanie zahrady populaciou a zistenie fitnes kazdeho jedinca
                # vlozi sa chromozon mnicha do funkcie
                population_fitness[i] = garden.rake_garden(self.population[i])
            

            generation_counter += 1

    def generate_starting_population(self):
        for i in range(1, self.POPULATION_SIZE + 1):
            self.population.append = self.generate_chromosome()

    def generate_chromosome(self): # vygeneruje 1 chromozon
        chromosome = [0] * self.genome_num
        perimeter_numbers = []

        for i in range((self.garden.half_perimeter) * 2):
            perimeter_numbers.append(i)

        random.shuffle(perimeter_numbers) # pseudo-nahodne rozhodi cisla obvodu

        for i in range(self.genome_num): # prvych n (= poctu genomov) vlozi do chromozonu
            chromosome = perimeter_numbers[i]

        return chromosome
        

        

        

        




# main funckia
def main():
    print("Zadanie 3 - Zenova zahrada\n")
    garden_size = [] # list so sirkou a vyskou zahrady
    stones_num = None # pocet kamenov v zahrade

    file_name = pathlib.Path(__file__).parent.absolute()
    file_name = str(file_name) + "\\zen_garden_parameters.txt"
    print("Parametre zenovej zahrady su zapisane v textovom subore\n", file_name,"\nv tvare \'sirka vyska kamene\'\n")

    try:
        with open(file_name, 'r') as f: # otvorenie suboru s parametrami zenovej zahrady
            lines = f.readlines() # ulozenie jednotlivych riadkov do listu

        for line in lines:
            param = line.split()
            print(param)
            for i in range(len(param)):
                if i == 0:
                    garden_size.append(param[i]) # sirka zahrady
                elif i == 1:
                    garden_size.append(param[i]) # vyska zahrady
                elif i == 2:
                    stones_num = param[i] # pocet kamenov

            garden = Zen_Garden(garden_size, stones_num) # vytvorenie zahrady
            garden.print_garden() # vypisanie nepohrabanej zahrady

    except (IOError, FileNotFoundError) as e: # eror, ak nemoze subor najst alebo precitat
        print("Subor ", file_name," sa nenasiel, zahrada bude vytvorena podla predlohy zo zadania")

main()