import sys
import time
import matplotlib.pylab as plt
import simulate
import minimax

def time_minimax(max_depth=5, num_iters=5):
    team = simulate.gen_team()
    times = []
    for i in range(1, max_depth+1):
        total = 0
        print "Testing tree depth %s ..." % i,
        for t in range(num_iters):
            start = time.clock()
            tree = minimax.generate_tree(team, False, i)
            end = time.clock()
            total += (end - start) / float(num_iters)
        times.append(total)
        print "took %0.4fsec (averaged over %s iterations)" % (total, num_iters)

    plt.figure("Minimax tree depth vs. generation time")
    plt.plot(range(1, max_depth+1), times)
    plt.show()

def test_backprop(max_depth=5):
    team = simulate.gen_team()
    tree = minimax.generate_tree(team, False, max_depth)
    print "generate successful"
    tree.backprop()
    print "backprop successful"

def test_next_move(max_depth=5):
    team = simulate.gen_team()
    print minimax.move_for_gamestate(team, max_depth)

if __name__ == "__main__":
    print "TIMING MINIMAX:"
    time_minimax(num_iters=1)

    print "TESTING BACKPROP:"
    test_backprop()

    print "TESTING NEXT_MOVE"
    test_next_move()

