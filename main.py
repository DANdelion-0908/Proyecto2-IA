import itertools
import seaborn as sns
import matplotlib.pyplot as plt
import random
import pandas as pd
from logic_project import *

class MastermindSolver:
    COLORS = ['azul', 'rojo', 'blanco', 'negro', 'verde', 'purpura']
    
    def __init__(self):
        self.possible_combinations = list(itertools.product(self.COLORS, repeat=4))
        self.search_space_sizes = []
        self.avg_attempts = {}
        self.knowledge = And()
        self.attempts = 0

    
    def create_symbol(self, position, color):        
        return Symbol(f"pos{position}_{color}")
    
    def initialize_knowledge(self):        
        for pos in range(4):
            color_symbols = [self.create_symbol(pos, color) for color in self.COLORS]
                
            self.knowledge.add(Or(*color_symbols))
                
            for color1, color2 in itertools.combinations(self.COLORS, 2):
                self.knowledge.add(Not(And(
                    self.create_symbol(pos, color1),
                    self.create_symbol(pos, color2)
                )))
    
    def process_feedback(self, guess, correct_pos, correct_color):        
        self.attempts += 1

        self.search_space_sizes.append(len(self.possible_combinations))
        
        possible_matches = []
        
        for combo in self.possible_combinations:    
            cp = sum(1 for g, c in zip(guess, combo) if g == c)
            cc = sum(min(guess.count(c), combo.count(c)) for c in set(guess)) - cp
            
            if cp == correct_pos and cc == correct_color:        
                conj = And()
                for pos, color in enumerate(combo):
                    conj.add(self.create_symbol(pos, color))
                possible_matches.append(conj)
        
        self.knowledge.add(Or(*possible_matches))
        
        self.possible_combinations = [
            combo for combo in self.possible_combinations 
            if self.is_consistent(combo)
        ]

    def is_consistent(self, combination):        
        model = {}
        for pos, color in enumerate(combination):    
            for c in self.COLORS:
                model[f"pos{pos}_{c}"] = (c == color)

        return self.knowledge.evaluate(model)

    def make_guess(self):        
        if not self.possible_combinations:
            raise ValueError("No hay combinaciones posibles consistentes con el conocimiento")
        
        return self.possible_combinations[0]

    def solve_automatic(self, secret):        
        self.initialize_knowledge()
        self.attempts = 0
        self.search_space_sizes = []
        self.avg_attempts = {}
        
        while True:
            guess = self.make_guess()
            if guess == secret:
                print(f"\nModo automático - Resuelto en {self.attempts} intentos")
                print("Evolución del tamaño del espacio de búsqueda:")
                for i, size in enumerate(self.search_space_sizes, 1):
                    print(f"  Intento {i}: {size} combinaciones posibles")
                    self.avg_attempts[i] = size / self.attempts
                return self.attempts, self.avg_attempts
                
            correct_pos = sum(1 for g, s in zip(guess, secret) if g == s)
            correct_color = sum(min(guess.count(c), secret.count(c)) for c in set(guess)) - correct_pos
            
            self.process_feedback(guess, correct_pos, correct_color)
    
    def solve_real_time(self):        
        self.initialize_knowledge()
        self.attempts = 0
        self.search_space_sizes = []
        
        print("\nMastermind Solver - Modo en Tiempo Real")
        print(f"Colores disponibles: {', '.join(self.COLORS)}")
        print("Ingresa la retroalimentación como dos números separados por espacio (ej. '1 2')")

        while len(self.possible_combinations) > 1:
            guess = self.make_guess()
            print(f"\nIntento {self.attempts + 1}: Adivinanza sugerida → {guess}")
            
            while True:
                feedback = input("Retroalimentación (correctos_posición correctos_color): ").strip()
                try:
                    cp, cc = map(int, feedback.split())
                    if 0 <= cp <= 4 and 0 <= cc <= 4 and (cp + cc) <= 4:
                        break
                    print("Valores inválidos. Deben ser números entre 0 y 4, con suma <=4")
                except ValueError:
                    print("Formato incorrecto. Ingresa dos números separados por espacio")
            
            self.process_feedback(guess, cp, cc)
            print(f"  → Combinaciones posibles restantes: {len(self.possible_combinations)}")

        if len(self.possible_combinations) == 1:
            print(f"\nSolución encontrada en {self.attempts} intentos: {self.possible_combinations[0]}")
            print("\nEvolución del espacio de búsqueda:")
            for i, size in enumerate(self.search_space_sizes, 1):
                print(f"  Intento {i}: {size} combinaciones posibles")
            return self.attempts
        else:
            print("No hay solución consistente con la retroalimentación proporcionada")
            return -1
        
def two_hundred_attempts():
    all_data = []

    for i in range(200):
        solver = MastermindSolver()
        secret_code = tuple(random.choices(solver.COLORS, k=4))
        solver.solve_automatic(secret_code)

        for intento_num, space_size in enumerate(solver.search_space_sizes, 1):
            all_data.append({
                "Juego": i + 1,
                "Intento": intento_num,
                "Espacio de búsqueda": space_size
            })

    df = pd.DataFrame(all_data)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="Intento", y="Espacio de búsqueda", estimator="mean")
    plt.title("Promedio del tamaño del espacio de búsqueda por intento (200 juegos)")
    plt.xlabel("Intento")
    plt.ylabel("Tamaño promedio del espacio de búsqueda")
    plt.show()

while True:
    solver = MastermindSolver()
    secret_code = tuple(input(f"Ingresa la combinación de colores separados por comas (azul, rojo, blanco, negro, verde, purpura): ").strip().split(","))
    
    if len(secret_code) != 4:
        print("\nFormato incorrecto ingresa exactamente 4 colores\n")
    
    else:
        attempts, avg_attempts = solver.solve_automatic(secret_code)

        print(f"\nModo automático - Resuelto en {attempts} intentos")

        input("\n Presiona ENTER para continuar al modo en tiempo real\n")

        solver = MastermindSolver()
        solver.solve_real_time()

# two_hundred_attempts()