import sys
import random
from operator import itemgetter, attrgetter
from statistics import mean

import yaml 

# from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node
from msgs_control.srv import SimPID  # Importa el mensaje de servicio personalizado

import os
script_dir = os.path.dirname(__file__) # absolute dir the script is in

class GeneticTuner(Node):

    def __init__(self, w_ts = 25., w_d = .6, w_overshoot = 200., w_ess = 15.):
        super().__init__('genetic_tuning')
        self.cli = self.create_client(SimPID, '/serv/sim_pid')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = SimPID.Request()
        
        self.Fitness = 0
        self.w = (w_ts, w_d, w_overshoot, w_ess) # weight of ts, d, overshoot, ess  (25., .6, 200., 15.)
        self.fitness_curve_mean = []
        self.fitness_curve_best = []        
            
    def llamada_control(self, kp, ki, kd):
        self.req.kp = kp
        self.req.ki = ki
        self.req.kd = kd
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        
        Ts, d, overshoot, Ess = attrgetter('ts', 'd', 'overshoot', 'ess')(self.future.result())
        
        return Ts, d, overshoot, Ess
    
    # Función de evaluación (fitness)
    def evaluate(self, chromosome):
        # Aquí debes implementar la evaluación del cromosoma y retornar un valor de fitness
        Ts, d, overshoot, Ess = self.llamada_control(chromosome[0], chromosome[1], chromosome[2])
        Fitness = self.w[0] * Ts + self.w[1] * d + self.w[2] * overshoot + self.w[3] * Ess
        return Fitness

    # Generar un cromosoma aleatorio
    def generate_random_chromosome(self, length):  
        chromosome = []
        for _ in range(length):
            gene = random.uniform(0.0, 10.0)  # Generar número aleatorio en el rango [0.0, 10.0]
            chromosome.append(gene)            
        return chromosome

    # Cruzar dos cromosomas
    def crossover(self, chromosome1, chromosome2, crossover_rate):
        new_chromosome=chromosome1
        if random.random() < crossover_rate:
            crossover_point = random.randint(1, len(chromosome1) - 1)
            new_chromosome = chromosome1[:crossover_point] + chromosome2[crossover_point:]
        return new_chromosome
        
    # Mutar un cromosoma
    def mutate(self, chromosome, mutation_rate):
        mutated_chromosome = []
        for gene in chromosome:
            if random.random() < mutation_rate:
                mutated_gene = random.uniform(0.0, 10.0)  # Generar número aleatorio en el rango [0.0, 5.0]
            else:
                mutated_gene = gene
            mutated_chromosome.append(mutated_gene)
        return mutated_chromosome

    #selección por torneo
    def selection_tournament(self, population_size, evaluated_population, T):
            parents = []            
            while len(parents) < population_size:
                candidates=[]
                for ite in range(T):
                    candidates.append(random.choice(evaluated_population))                            
                parents.append(min(candidates, key=itemgetter(1))[0])
            return parents
    
    # Algoritmo genético
    def genetic_algorithm(self, population_size, chromosome_length, generations, mutation_rate, crossover_rate, T=8):
        population = []
        for _ in range(population_size):
            chromosome = self.generate_random_chromosome(chromosome_length)
            population.append(chromosome)
       
        for generation in range(generations):     
            
            if generation % 20 == 0:
            	self.get_logger().info('Generation Progress: %d / %d' %
    		(generation, generations))
    			    
            # Evaluación de la población
            evaluated_population = [(chromosome, self.evaluate(chromosome)) for chromosome in population]

            # Selección de padres mediante torneo de longitud T
            parents = []
            # T=8 # Se seleccionan 8 cromosomas de manera aleatoria pra el torneo. Nos quedaremos con el de menor función de fitness
            parents = self.selection_tournament(population_size, evaluated_population, T)

            # Cruzamiento y mutación para generar descendencia
            offspring = []
            for i in range(0, population_size, 2):
                parent1 = parents[i]
                parent2 = parents[i + 1]
                child1 = self.crossover(parent1, parent2, crossover_rate)
                child2 = self.crossover(parent2, parent1, crossover_rate)
                mutated_child1 = self.mutate(child1, mutation_rate)
                mutated_child2 = self.mutate(child2, mutation_rate)
                offspring.extend([mutated_child1, mutated_child2])

            # Reemplazar la población anterior con la descendencia
            population = offspring

            self.fitness_curve_best.append(min(evaluated_population, key=lambda x: x[1])[1]) # Best chromosome only
            self.fitness_curve_mean.append(sum([x[1] for x in evaluated_population])/len(evaluated_population))# Average chromosome

        # Devolver el mejor cromosoma de la última generación
        best_chromosome = min(evaluated_population, key=lambda x: x[1])#[0]
        return best_chromosome, self.fitness_curve_best, self.fitness_curve_mean
        
def main(args=None):
    rclpy.init(args=args)
    
    # Cargar configuración del algoritmo genético desde del archivo yaml
    rel_path = "gen_config.yaml"
    abs_file_path = os.path.join(script_dir, rel_path)
    stream = open(abs_file_path, 'r')
    gen_config = yaml.safe_load(stream)
    
    gen = GeneticTuner(w_ts=gen_config["w_ts"], w_d=gen_config["w_d"], w_overshoot=gen_config["w_overshoot"], w_ess=gen_config["w_ess"])
    
    # Imprimir configuración cargada del archivo yaml
    gen.get_logger().info('\nYaml Configuration:\n Population Size: %d\n Chromosome Length: %d\n Generations: %d\n Mutation Rate: %f\n Crossover Rate: %f\n T: %d\n\n w_ts: %f\n w_d: %f\n w_overshoot: %f\n w_ess: %f\n' %
    	(gen_config["population_size"], gen_config["chromosome_length"], gen_config["generations"], gen_config["mutation_rate"], gen_config["crossover_rate"], gen_config["T"], gen_config["w_ts"],  gen_config["w_d"], gen_config["w_overshoot"], gen_config["w_ess"]))

    # Ejecutar el algoritmo genético
    best_chromosome, fitness_curve_best, fitness_curve_mean = gen.genetic_algorithm(gen_config["population_size"], gen_config["chromosome_length"], gen_config["generations"], gen_config["mutation_rate"], gen_config["crossover_rate"], gen_config["T"])
    
    BC = best_chromosome[0]
    
    # Imprimir el resultado (mejor cromosoma)
    gen.get_logger().info('Mejor Cromosoma: Kp=%f Ki=%f Kd=%f fitness=%f' %
    	(BC[0], BC[1], BC[2], best_chromosome[1]))
    
    # Imprimir calidad de la respuesta con el mejor cromosoma
    Ts, d, overshoot, Ess = gen.llamada_control(BC[0], BC[1], BC[2])
    gen.get_logger().info('\nResult:\n Ts: %f\n d: %f\n overshoot: %f\n Ess: %f\n' %
    	(Ts, d, overshoot, Ess))
    	
    # while(1): pass
    gen.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
