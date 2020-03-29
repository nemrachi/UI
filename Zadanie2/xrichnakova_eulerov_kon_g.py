import random

num_of_starting_position = 10 # pocet roznych zaciatocnych bodov pre kona

class Eulers_horse:
    def __init__(self, grid_size): # grid_size = velkost sachovnice
        self.move_off = [(1, 2), (1, -2), (-1, 2), (-1, -2),
                        (2, 1), (2, -1), (-2, 1), (-2, -1)] # moznosti pohybov kona 
        
        self.width = grid_size[0]
        self.height = grid_size[1]
        self.path = [] # vysledna cesta
        self.board = [] # sachovnica

        for i in range(num_of_starting_position):
            self.star_pos_x = random.randrange(self.width - 1) # vygeneruje nahodnu x-ovu suradnicu
            self.star_pos_y = random.randrange(self.height - 1) # vygeneruje nahodnu y-ovu suradnicu  
            self.start_position = (self.star_pos_x, self.star_pos_y) # startovacia pozicia kona 
            print("_______________________________________________________________________\n")
            print(i + 1 ,". startovacia pozicia: ", self.start_position)

            self.generate_board()

            self.find_path(self.start_position)

            self.print_board()
            print("_______________________________________________________________________\n")


    def generate_board(self):
        # vygeneruje pole, ktore predstavuje sachovnicu
        # vyplni jednotlive policka 0 (ako nenavstivene)
        self.board = [] # zresetuje sachovnicu
        for i in range(self.height):
            self.board.append([0] * self.width) # nastavi vsade 0

    def print_board(self):
        # vypise hodnoty zapisane v sachovnici
        print("\nSachovnica s cestou kona")
        print("------------")
        for row in self.board:
            print (row)
        print("------------")

    def print_path(self):
        # vypise cestu
        # vypis zarovnava na 5 policok na riadok
        for i in range(0, len(self.path), 5):
            print(self.path[i:i+5])


    def generate_legal_moves(self, cur_pos):
        # vygeneruje list policok, na ktore sa kon moze pohnut z aktualneho policka (cur_pos)
        possible_pos_list = []

        for move in self.move_off:
            new_x = cur_pos[0] + move[0]
            new_y = cur_pos[1] + move[1]

            if ((new_x < 0) or (new_x >= self.width) or
                (new_y < 0) or (new_y >= self.height)):
                continue # ak by kon vysiel mimo sachovnice, nezapise sa dany pohyb
            else:
                possible_pos_list.append((new_x, new_y))

        return possible_pos_list

    def sort_next_position(self, pos): 
        '''
        -> Warnsdorffovo pravidlo
        
        usporiada buduce tahy, cize prve zaznamy v liste budu 
        tie buduce policka, ktore maju najmensie "skore",
        t.j. najmenej tahov sa da z buduceho policka spravit
        na dalsie policko
        
        tymto sa docieli, ze kon sa najprv bude pohybovat zo zaciatku pri krajoch sachovnice
        '''

        # vygenerujeme list vsetkych policok, na kt. sa mozme dostat z aktualneho policka (pos)
        next_pos_list = self.generate_legal_moves(pos) 
        unvisited_pos_list = [] # list nenastivenych policok

        for next_pos in next_pos_list:
            # ak je policko nenastivene (na policku je napisane 0), zapiseme si ho
            if self.board[next_pos[0]][next_pos[1]] == 0:
                unvisited_pos_list.append(next_pos)

        if not unvisited_pos_list:
            # ak sme nenasli ani 1 nenastivene policko 
            return [] # vraciame prazdne pole

        scores = [] 

        for unvisited in unvisited_pos_list:
            # ku kazdemu nenavstivenemu policku priradime skore => pocet dalsich tahov
            score = [unvisited, 0] 
            # vygenerujeme list vsetkych policok, na kt. sa mozme dostat z aktualneho policka (unvisited)
            moves = self.generate_legal_moves(unvisited)
            for m in moves:
                if self.board[m[0]][m[1]] == 0: # ak je policko nenastivene
                    score[1] += 1 # scita pocet moznych nasledujucih tahov
            scores.append(score)

        # usporida list scores vzostupne podla hodnoty skore
        sorted_scores = sorted(scores, key=lambda s: s[1], reverse=False)
        sorted_next_pos = []
        for s in sorted_scores:
            # print(s[1]) # vypisanie poradia skore
            sorted_next_pos.append(s[0]) # ulozi usporiadane policka bez skore
        return sorted_next_pos

    def find_path(self, pos): # pos = aktualna pozicia kona
        # funkcia najde cestu pre Eulerovho kona
        move = 1 # pocitadlo pohybov
        path = [] # sem sa uklada generovana cesta

        while True:
            self.board[pos[0]][pos[1]] = move # zapise index pohybu do aktualneho policka
            path.append(pos) # prida dane policko do cesty
            # print(pos)

            if move == self.width * self.height: # ak kon presiel vsetky policka, zapise sa cesta a funkcia sa konci uspesne
                print("Cesta bola najdena :)")
                self.path = path
                self.print_path()
                return

            else:
                # usporiada mozne nasledujuce tahy
                # na prve miesta listu su dane take policka, z ktorych vedie najmensi pocet dalsich tahov
                sorted_next_pos = self.sort_next_position(pos) 
                if not sorted_next_pos:
                    # ak sa uz nenasli ziadne dalsie mozne tahy, ale kon este nepresiel celu sachovnicu, funkcia konci neuspesne
                    print("Cesta nebola najdena :(")
                    return

                pos = sorted_next_pos.pop(0); # posuvame sa na policko, ktore ma najmensi pocet dalsich tahov
                move += 1


# Main
if __name__== "__main__":    
    print("Zadanie 2 poduloha g) - Eulerov kon rieseny heuristicky")
    # zadanie sirky a vysky sachovnice uzivatelom
    grid_size = list(map(int, input("\nZadaj sirku a vysku sachovnice odelene medzerou: ").strip().split()))[:2] 
    
    if not grid_size:
        grid_size = (8, 8) # zakladna velkost sachovnice, ak uzivatel nezada inu

    Eulers_horse(grid_size)