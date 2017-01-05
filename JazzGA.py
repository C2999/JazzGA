import math
import random
import time
from random import randint
from music21 import *
from simpleOSC import initOSCClient, initOSCServer, setOSCHandler, sendOSCMsg, closeOSC, \
     createOSCBundle, sendOSCBundle, startOSCServer


class JazzGA:

    def __init__(self, target, popSize, upperBound, lowerBound):
        self.target = target
        self.popSize = popSize
        self.upperBound = upperBound
        self.lowerBound = lowerBound
        self.possibleNotes = []
        self.population = []

    ##creates set used by createRandomSolution
    def createRandomSolutionSet(self):
        sc = scale.ChromaticScale()
        possibleNotes = [] 
        for p in sc.getPitches(self.lowerBound,self.upperBound):
            n = note.Note(p, quarterLength=.5)
            possibleNotes.append(n)
        self.possibleNotes = possibleNotes

    ##creates random solution for begining of algorithm 
    def createRandomSolution(self):
        randomSolution = []
        for i in range(len(self.target)):
            randomSolution.append(self.possibleNotes[randint(0,len(self.possibleNotes)-1)])
        return randomSolution

    ##creates initial population
    def initialize(self):
        self.createRandomSolutionSet()
        self.createRandomSolution()
        for i in range(self.popSize):
            self.population.append(self.createRandomSolution())
        self.generatePopulationFitness()

    ##counts number of correct elements in the array
    def fitness(self, solution):
        count = 0
        for i in range(len(solution)):
            if solution[i].pitch.isEnharmonic(self.target[i].pitch):
                count += 1
        return count ** 2

    ##sets fitness for every solution in the total population
    def generatePopulationFitness(self):
        self.popFitnesses = []
        for s in self.population:
            self.popFitnesses.append(self.fitness(s))

    ##picks a parent with a higher probability of picking a fit parent
    def pickFitParent(self):
        totalFitness = sum(self.popFitnesses)
        r = random.randrange(totalFitness)
        ind = -1
        while r > 0:
            ind += 1
            r -= self.popFitnesses[ind]
        return self.population[ind]
  
    ##Splices half of one array with another  
    def crossover(self, p1, p2):
        newChild = []
        i = 0
        while i < len(p1)/2:
            newChild.append(p1[i])
            i += 1
        while i < len(p1):
            newChild.append(p2[i])
            i += 1
        return newChild

    ##changes an element of the array to a random note based on the mutation rate.
    def mutate(self, child, mutation_rate=0.01):
        newChild = []
        for i in range(len(child)):
            if random.random() < mutation_rate:
                newChild.append(self.possibleNotes[randint(0,len(self.possibleNotes)-1)])
            else:
                newChild.append(child[i])
        return newChild

    ## breeds new child by selecting fit parents with an added chance of mutation
    def generateNewPopulation(self):
        newPopulation = []
        for i in range(self.popSize):
            p1 = self.pickFitParent()
            p2 = self.pickFitParent()
            child = self.crossover(p1, p2)
            child = self.mutate(child)
            newPopulation.append(child)
        self.population = newPopulation

    ##runs algorithm for specified number of epochs 
    def evolve(self, epochs):
        for i in range(epochs):
            self.generateNewPopulation()
            self.generatePopulationFitness()
            fitness, solution = self.getBestSolution()
            freqSolution = self.convertToFrequency(solution)
            normFitness = self.normalizeFitness(fitness)
            ##self.testing(solution,fitness)
            self.sendResults(normFitness, freqSolution)
            time.sleep(.5)

    ##for testing. Shows each solution.
    def testing(self,solution,fitness):
        solutionOutput = ""
        targetOutput = ""
        for i in range(len(solution)):
            solutionOutput += str(solution[i].pitch) + ", "
        for i in range(len(self.target)):
            targetOutput += str(self.target[i].pitch) + ", "
        print("Solution: " + solutionOutput)
        print("Target: " + targetOutput)
        print("Fitness: " + str(fitness))

    ##chooses best solution by selecting the solution with the highest fitness
    def getBestSolution(self):
        max_ind = self.popFitnesses.index(max(self.popFitnesses))
        fitness = self.fitness(self.population[max_ind])
        return math.sqrt(fitness), self.population[max_ind]

    ##converts notes to frequencies 
    def convertToFrequency(self,solution):
        newSolution = []
        for i in range(len(solution)):
            newSolution.append(solution[i].pitch.midi)
        return newSolution

    ##sets fitness between 0 and 1
    def normalizeFitness(self,fitness):
        return float(fitness/len(self.target))

    ##sends results to max
    def sendResults(self,fitness,solution): 
        try:
            sendOSCMsg("/notes", [solution])
            sendOSCMsg("/fitness", [fitness])

        except KeyboardInterrupt:
            print "closing all OSC connections... and exit"
            closeOSC() ## finally close the connection before exiting or program.

##Takes in xml file and makes an array of the notes in between the starting and ending measure
def parseData(segStart, segEnd, part, fileName='Jazz_Licks.xml'):
    s = converter.parse(fileName)
    selectedPart = s.parts[part]
    segment = selectedPart.measures(segStart,segEnd)
    noteArr = []
    for n in segment.recurse().notes:
            noteArr.append(n)
    return noteArr

def configureOSC():
    initOSCClient() 
    initOSCServer()
    startOSCServer() 

if __name__=="__main__":
    noteArr = parseData(10,12,0) 
    JS = JazzGA(noteArr,300,"A-2","C6")
    configureOSC() ##configures OSC client to send note arrays to max
    JS.initialize()
    JS.evolve(10000)
