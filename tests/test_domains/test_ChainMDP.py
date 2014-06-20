from rlpy.Representations import Tabular
from rlpy.Domains import ChainMDP
from rlpy.Agents.TDControlAgent import SARSA
import numpy as np
from rlpy.Tools import __rlpy_location__
import os

from rlpy.Policies import eGreedy
from rlpy.Experiments import Experiment
import logging

def _make_experiment(exp_id=1, path="./Results/Tmp/test_ChainMDP/"):
    """
    Each file specifying an experimental setup should contain a
    make_experiment function which returns an instance of the Experiment
    class with everything set up.

    @param id: number used to seed the random number generators
    @param path: output directory where logs and results are stored
    """

    ## Domain:
    chainSize = 5
    domain = ChainMDP(chainSize=chainSize)

    ## Representation
    # discretization only needed for continuous state spaces, discarded otherwise
    representation  = Tabular(domain)

    ## Policy
    policy = eGreedy(representation, epsilon=0.2)

    ## Agent
    agent = SARSA(representation=representation, policy=policy,
                  discount_factor=domain.discount_factor,
                  learn_rate=0.1)
    checks_per_policy = 3
    max_steps = 50
    num_policy_checks = 3
    experiment = Experiment(**locals())
    return experiment

def _checkSameExperimentResults(exp1, exp2):
    """ Returns False if experiments gave same results, true if they match. """
    if not np.all(exp1.result["learning_steps"] == exp2.result["learning_steps"]):
        # Same number of steps before failure (where applicable)
        print 'LEARNING STEPS DIFFERENT'
        print exp1.result["learning_steps"]
        print exp2.result["learning_steps"]
        return False
    if not np.all(exp1.result["return"] == exp2.result["return"]):
        # Same return on each test episode
        print 'RETURN DIFFERENT'
        print exp1.result["return"]
        print exp2.result["return"]
        return False
    if not np.all(exp1.result["steps"] == exp2.result["steps"]):
        # Same number of steps taken on each training episode
        print 'STEPS DIFFERENT'
        print exp1.result["steps"]
        print exp2.result["steps"]
        return False
    return True

def test_seed():
    """ Ensure that providing the same random seed yields same result """
    # [[initialize and run experiment without visual]]
    expNoVis = _make_experiment(exp_id=1)
    expNoVis.run(visualize_steps=False,
            visualize_learning=False,
            visualize_performance=0)
    
    # [[initialize and run experiment with visual]]
    expVis1 = _make_experiment(exp_id=1)
    expVis1.run(visualize_steps=True,
            visualize_learning=False,
            visualize_performance=1)
    
    expVis2 = _make_experiment(exp_id=1)
    expVis2.run(visualize_steps=False,
            visualize_learning=True,
            visualize_performance=1)
    
    # [[assert get same results]]
    assert _checkSameExperimentResults(expNoVis, expVis1)
    assert _checkSameExperimentResults(expNoVis, expVis2)
    
def test_transitions():
    """
    Ensure that actions result in expected state transition behavior. 
    Note that if the agent attempts to leave the edge 
    (select LEFT from s0 or RIGHT from s49) then the state should not change.
    NOTE: assume p_action_failure is only noise term.
    
    """
    # [[initialize domain]]
    chainSize = 5
    domain = ChainMDP(chainSize=chainSize)
    dummyS = domain.s0()
    domain.state = np.array([2]) # state s2
    left = 0
    right = 1
    
    # Check basic step
    r,ns,terminal,possibleA = domain.step(left)
    assert ns[0] == 1 and terminal == False
    assert np.all(possibleA == np.array([left, right])) # all actions available
    assert r == domain.STEP_REWARD
    
    # Ensure all actions available, even on corner case, to meet domain specs
    r,ns,terminal,possibleA = domain.step(left)
    assert ns[0] == 0 and terminal == False
    assert np.all(possibleA == np.array([left, right])) # all actions available
    assert r == domain.STEP_REWARD
    
    # Ensure state does not change or wrap around per domain spec
    r,ns,terminal,possibleA = domain.step(left)
    assert ns[0] == 0 and terminal == False
    assert np.all(possibleA == np.array([left, right])) # all actions available
    assert r == domain.STEP_REWARD
    
    r,ns,terminal,possibleA = domain.step(right)
    assert ns[0] == 1 and terminal == False
    assert np.all(possibleA == np.array([left, right])) # all actions available
    assert r == domain.STEP_REWARD
    
    r,ns,terminal,possibleA = domain.step(right)
    r,ns,terminal,possibleA = domain.step(right)
    r,ns,terminal,possibleA = domain.step(right)
    
    # Ensure goal state gives proper condition
    assert ns[0] == 4 and terminal == True
    assert np.all(possibleA == np.array([left, right])) # all actions available
    assert r == domain.GOAL_REWARD
    
