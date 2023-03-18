import numpy as np
import random
import cv2

# Parameters
population_size = 100
num_triangles = 50
mutation_rate = 0.1
crossover_rate = 0.8
num_generations = 1000


def load_target_image(image_path):
    # Load the target image using OpenCV
    target_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Convert the target image to floating point representation in the range [0, 1]
    target_image = target_image.astype(np.float32) / 255.0

    return target_image


def create_individual(num_triangles, image_width, image_height):
    # Create a random individual (chromosome)
    # Each triangle has 3 vertices (6 coordinates) and 3 color values (RGBA)
    individual = []

    for i in range(num_triangles):
        # Generate random triangle vertices
        for j in range(3):
            x = random.uniform(0, image_width)
            y = random.uniform(0, image_height)
            individual.extend([x, y])

        # Generate random color values (RGBA)
        r = random.random()
        g = random.random()
        b = random.random()
        a = random.random()
        individual.extend([r, g, b, a])

    return individual
    # return [random.random() for _ in range(9 * num_triangles)]


def initialize_population(population_size, num_triangles, image_width, image_height):
    # Initialize the population
    return [create_individual(num_triangles, image_width, image_height) for _ in range(population_size)]


def render_triangles(individual, image_width, image_height):
    # Create an empty image
    image = np.zeros((image_height, image_width, 3))

    # Iterate over the triangles
    for i in range(0, len(individual), 10):
        # Extract triangle vertices and color
        vertices = np.array([(individual[i], individual[i + 1]), (individual[i + 2], individual[i + 3]),
                             (individual[i + 4], individual[i + 5])], dtype=np.int32)
        color = (individual[i + 6], individual[i + 7], individual[i + 8], individual[i + 9])

        # Draw the triangle on the image
        cv2.fillConvexPoly(image, vertices, color)

    return image


def fitness(individual, target_image):
    # Render the triangles from the individual
    rendered_image = render_triangles(individual, target_image.shape[1], target_image.shape[0])

    # Compute the difference between the rendered image and target image
    difference = np.mean((rendered_image - target_image) ** 2)

    # Define fitness as the negative difference (higher fitness means smaller difference)
    return -difference


def selection(population, fitnesses):
    # Calculate the total fitness
    total_fitness = sum(fitnesses)

    # Calculate the relative fitness for each individual
    relative_fitnesses = [fitness / total_fitness for fitness in fitnesses]

    # Generate a random number in the range [0, 1)
    r = random.random()

    # Choose a parent using roulette wheel selection
    cumulative_sum = 0
    for index, rel_fitness in enumerate(relative_fitnesses):
        cumulative_sum += rel_fitness
        if r <= cumulative_sum:
            return population[index]

    # If the above loop does not return, return the last individual
    return population[-1]


def crossover(parent1, parent2):
    crossover_point = random.randrange(0, len(parent1), 10)

    # Perform single-point crossover
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]

    return child1, child2


def mutation(individual, mutation_rate, mutation_scale):
    mutated_individual = []

    for gene in individual:
        # Check if mutation should be applied
        if random.random() < mutation_rate:
            # Apply Gaussian mutation
            mutated_gene = gene + random.gauss(0, mutation_scale)

            # Make sure the mutated gene is within the valid range [0, 1]
            mutated_gene = min(max(mutated_gene, 0), 1)
        else:
            # If no mutation, keep the original gene
            mutated_gene = gene

        mutated_individual.append(mutated_gene)

    return mutated_individual


def save_and_display_image(final_image, save_path):
    # Convert the image back to the range [0, 255] and convert to uint8
    final_image_uint8 = (final_image * 255).astype(np.uint8)

    # Save the image using OpenCV
    cv2.imwrite(save_path, final_image_uint8)

    # Display the image using OpenCV
    cv2.imshow('Final Image', final_image_uint8)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    # Load the target image
    image_path = 'chrome.jpg'
    target_image = load_target_image(image_path)

    # Initialize the population
    population_size = 100
    num_triangles = 50
    image_width = target_image.shape[1]
    image_height = target_image.shape[0]

    population = initialize_population(population_size, num_triangles, image_width, image_height)

    # Define GA parameters
    generations = 500
    mutation_rate = 0.1
    mutation_scale = 0.05

    # Run the genetic algorithm
    for generation in range(generations):
        # Evaluate the fitness of each individual in the population
        fitnesses = [fitness(individual, target_image) for individual in population]

        # Select parents and perform crossover and mutation to create offspring
        offspring = []
        for _ in range(population_size // 2):
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)

            child1, child2 = crossover(parent1, parent2)
            child1 = mutation(child1, mutation_rate, mutation_scale)
            child2 = mutation(child2, mutation_rate, mutation_scale)

            offspring.append(child1)
            offspring.append(child2)

        # Replace the old population with the offspring
        population = offspring

    # Find the best individual in the final population
    best_individual = max(population, key=lambda x: fitness(x, target_image))

    # Render the final image from the best individual
    final_image = render_triangles(best_individual, image_width, image_height)

    # Save and display the final image
    save_path = 'chromeFit.jpg'
    save_and_display_image(final_image, save_path)


if __name__ == '__main__':
    main()