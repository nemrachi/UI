import pathlib
import string

CONDITION = 'condition'
ACTION = 'action'
PRIDAJ = 'pridaj'
VYMAZ = 'vymaz'
SPRAVA = 'sprava'
knowledge_base = list()

def obtain_rules(rules: dict, lines_rules: list) -> dict:
    name_line = ""
    for line in lines_rules:
        if line.startswith("Meno:"):
            if line.endswith("\n"):
                line = line[:len(line)-1]
            line = line.split()
            name_line = ' '.join(line[1:])
            rules[name_line] = dict()
        elif line.startswith("AK"):
            if line.endswith("\n"):
                line = line[3:len(line)-1]
            else:
                line = line[3:]
            line = line.split(",")
            rules[name_line][CONDITION] = line
        elif line.startswith("POTOM"):
            if line.endswith("\n"):
                line = line[6:len(line)-1]
            else:
                line = line[6:]
            line = line.split(",")
            rules[name_line][ACTION] = dict()
            for l in line:
                line_split = l.split()
                rules[name_line][ACTION][line_split[0]] = ' '.join(line_split[1:])
    return rules

def obtain_facts(facts: list, lines_facts: list) -> dict:
    name_line = ""
    for line in lines_facts:
        if line.endswith("\n"):
            line = line[:len(line)-1]
        facts.append(line)
    return facts

def test_obtaining():
    rules = dict()
    facts = list()
    lines_rules = list()
    lines_facts = list()
    file_path = pathlib.Path(__file__).parent.absolute()
    file_pravidla = str(file_path) + "\\pravidla.txt" # meno textoveho suboru s pravidlami
    file_fakty = str(file_path) + "\\fakty.txt" # meno textoveho suboru s faktami
    try:
        with open(file_pravidla, 'r') as f:
            lines_rules = f.readlines()

        with open(file_fakty, 'r') as f:
            lines_facts = f.readlines()
        
        if lines_facts == [] or lines_rules == []: # ak su subory prazdne
            raise Exception("\n\tERROR: Subory su prazdne\n")

        rules = obtain_rules(rules, lines_rules)
        facts = obtain_facts(facts, lines_facts)
        print(rules, end="\n\n")
        print(facts)
    except (IOError, FileNotFoundError) as e: # error, ak nemoze subor najst alebo precitat
        print("\n\tERROR: Subory sa nenasli\n")

def remove_empty_or_same_knowledge():
    global knowledge_base
    if None in knowledge_base:
        knowledge_base.remove(None)
    if "" in knowledge_base:
        knowledge_base.remove("")

    print("\t\t", knowledge_base)


def get_knowledge(rule: dict, con_index: int, variables: dict) -> list:
    global knowledge_base
    remove_empty_or_same_knowledge()

    con_pattern = rule[CONDITION][con_index].split()

    if rule[CONDITION][1].startswith('zena'):
        print("")

    relationship = ""
    for p in con_pattern:
        if "?" not in p: relationship += p + " "
    relationship = relationship[:len(relationship)-1]

    for f in knowledge_base:
        f_split = f.split()  
        
        if relationship in f:
            if variables == {}: #or (not all(type(value) != int for value in variables.values())):
                for p in con_pattern:
                    if p.startswith("?"): # zistime indexy premennych v patterne
                        variables[p[1:]] = f_split[con_pattern.index(p)] 

                new_knowledge = get_knowledge(rule, con_index + 1, variables)
                if new_knowledge not in knowledge_base:
                    knowledge_base.append(new_knowledge)
                
                variables = {}

            else:
                add_knowledge = False
                for v_key in variables.keys():
                    if variables[v_key] in f:
                        print(rule)
                        print("\t", con_pattern)
                        print("\t", f_split)
                        if con_pattern.index("?" + v_key) == f_split.index(variables[v_key]):
                            for p in con_pattern:
                                if p.startswith("?"): # zistime indexy premennych v patterne
                                    variables[p[1:]] = f_split[con_pattern.index(p)] 
                            add_knowledge = True
                            break
                        else:
                            return ""

                if not add_knowledge:
                    return ""

                rule_action = rule[ACTION]

                knowledge = ""

                if PRIDAJ in rule_action.keys():
                    action = rule_action[PRIDAJ].split()
                    for a in action:
                        if a.startswith("?"):
                            knowledge += variables[a[1:]] + " "
                        else:
                            knowledge += a + " "

                knowledge = knowledge[:len(knowledge)-1]
                print("Knowledge: ", knowledge)


                if con_index + 1 == len(rule[CONDITION]):
                    return knowledge
        else:
            continue


def knowledge_base_agent(facts: list, rules: dict):
    global knowledge_base
    knowledge_base = facts
    for name in rules:
        knowledge_base.append(get_knowledge(rules[name], 0, {}))


def main():
    global knowledge_base
    rules = dict()
    facts = list()
    lines_rules = list()
    lines_facts = list()

    file_path = pathlib.Path(__file__).parent.absolute()
    file_pravidla = str(file_path) + "\\pravidla.txt" # meno textoveho suboru s pravidlami
    file_fakty = str(file_path) + "\\fakty.txt" # meno textoveho suboru s faktami
    print("Zadanie 4 - Dopredny produkcny system\n")

    try:
        with open(file_pravidla, 'r') as f:
            lines_rules = f.readlines()

        with open(file_fakty, 'r') as f:
            lines_facts = f.readlines()
        
        if lines_facts == [] or lines_rules == []: # ak su subory prazdne
            raise Exception("\n\tERROR: Subory su prazdne\n")

        # transformuje pravidla do formy {'Meno': {'condition': [list of conditions], 'action': {dictionary of actions}}}
        rules = obtain_rules(rules, lines_rules) 
        # transformmuje fakty do formy listu stringov
        facts = obtain_facts(facts, lines_facts)
        # ziskava znalosti
        knowledge_base_agent(facts, rules)
            
    except (IOError, FileNotFoundError) as e: # error, ak nemoze subor najst alebo precitat
        print("\n\tERROR: Subory sa nenasli\n")

main()
# test_obtaining()