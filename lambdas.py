from __future__ import print_function, division
import thinkbayes2
import thinkplot
import math
import matplotlib
import scipy
import numpy
import copy

class Lambda(thinkbayes2.Suite):
    """Represents distribution of lambda values."""

    def __init__(self):
        """
            Upon initializing, we generate a pmf for each 
        """
        super( Lambda, self ).__init__()
        self.hypPmfs = []
        for hypo in range(1,101):
            # print('hypo:',hypo)
        # Set up exponential Pmf for a given lambda value;
            if (hypo != 0):
                interarrival = thinkbayes2.MakeExponentialPmf(1/hypo, high=101)
            for val, prob in interarrival.Items():
                interarrival[val] *= val
            interarrival.Normalize()
            
            # Make a mixture of distributions of time since last login
            metapmf = thinkbayes2.Pmf()
            for time, prob in interarrival.Items():
                if time == 0:
                    continue
                pmf = thinkbayes2.MakeUniformPmf(0, time, 101)
                metapmf[pmf] = prob

            timesince = thinkbayes2.MakeMixture(metapmf)

            # Make a cdf using the mixture
            cdf = thinkbayes2.Cdf(timesince)

            # Use a random sampling to generate a pdf/pmf

            xs = numpy.linspace(0, 100, 101)
            ys = [scipy.misc.derivative(cdf.Prob, x) for x in xs]
            items = dict(zip(xs, ys))
            pmf = thinkbayes2.MakePmfFromItems(items)
            pmf.Normalize()

            print('hypo:',hypo)

            self.hypPmfs.append(pmf)


    def Likelihood(self, data, hypo):
        """Computes likelihood of given lambda value for new data under the hypothesis
        
        data: time since last login
        hypo: integer for 1/lambda value (lambda is arrival rate, so hypo )
        """

        if (data > 99):
            data = 99

        like = self.hypPmfs[int(hypo)+1].Prob(math.ceil(data))
    
        return like

    def generateQ(self, thresh):
        """
        - Creates a distribution of probabilities of q, which is ther percentage of active users
            - Assumes that "active user" is based on some threshold # of logins per day
            - PMF: x axis is q values, y axis is probability that said q value is true

        qProbs = probabilities for q PMF
        qVals = values for q PMF
        """
        qProbs = []
        qVals = []

        for val, prob in self.Items():
            pmf = self.hypPmfs[int(val)+1]
            qVal = 1-pmf.ProbGreater(thresh)
            qProbs.append(prob)
            qVals.append(qVal)
            print(qVal)

        qPmf = thinkbayes2.MakePmfFromItems(dict(zip(qVals, qProbs)))

        return qPmf

def QUpdatePlot(pmf, data):
    pmf.Update(data)
    thinkplot.Pdf(pmf.generateQ(10))

def QUpdateSetPlot(pmf, data):
    pmf.UpdateSet(data)
    thinkplot.Pdf(pmf.generateQ(10))

def main():
    # make the priors
    normpmf = thinkbayes2.MakeNormalPmf(10,20,4)
    lampmf = Lambda()
    for val, prob in normpmf.Items():
        if val >= 0:
            lampmf[val]=prob
    lampmf.Normalize()

    # thinkplot.Pmf(lampmf)
    lampmf2 = copy.deepcopy(lampmf)
    lampmf3 = lampmf
    # lampmf2.UpdateSet([1,1,21,2,24,2,1,2,1,2,5,1,2,1,2,2,2,2,2.67,2,1,2,2,0.08333333333,3,2,24,336,11,3,10,1,0.1833333333,0.7166666667,3,1,1,3,3,3,0.15,3,3,3,48,1,72,2,2,0.6,1,4,5,4,0.6833333333,120,4,0.4,4,4,72,3,24,0.65,0.65,96,0.5333333333,1,2,2,6,3,1,3,720,7,6,24,0.06666666667,0.9,0.06666666667,0.2,0.4333333333,7,96,22,8,1,0.4,48,0.1,2,7,3,0.06666666667,6,24,0.4166666667,9,720,8,1,9])

    # Updates the lambda distribution with a the time since last login for a seen user
 
    # QUpdatePlot(lampmf2, 20)
    # QUpdatePlot(lampmf2, 15)
    # QUpdatePlot(lampmf2, 10)
    # QUpdatePlot(lampmf2, 5)

    QUpdateSetPlot(lampmf2, [20,15,10,5])

    # thinkplot.Show()

    # QUpdatePlot(lampmf3, 5)
    # QUpdatePlot(lampmf3, 10)
    # QUpdatePlot(lampmf3, 15)
    # QUpdatePlot(lampmf3, 20)

    QUpdateSetPlot(lampmf3, [5, 10, 15, 20])

    thinkplot.Show()

if __name__ == '__main__':
    main()



