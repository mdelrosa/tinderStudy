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

    def __init__(self, timeScale):
        """
            - Upon initializing, we generate a pmf for each hypo
            - Pmf gives probability that a person will login again in the given timeScale

            timeScale: # of time divisions per hour; scales the hypos by this factor (lambda * hypo = timescale)
        """
        super( Lambda, self ).__init__()
        self.hypPmfs = []
        self.timeScale = timeScale
        high = 100*timeScale+1
        for hypo in range(1,high):
            print('hypo:',hypo)
        # Set up exponential Pmf for a given lambda value;
            lam = timeScale / hypo
            interarrival = thinkbayes2.MakeExponentialPmf(timeScale/hypo, high=high)
            for val, prob in interarrival.Items():
                interarrival[val] *= val
            interarrival.Normalize()
            
            # Make a mixture of distributions of time since last login
            metapmf = thinkbayes2.Pmf()
            for time, prob in interarrival.Items():
                if time == 0:
                    continue
                pmf = thinkbayes2.MakeUniformPmf(0, time, high)
                metapmf[pmf] = prob

            timesince = thinkbayes2.MakeMixture(metapmf)

            # Make a cdf using the mixture
            cdf = thinkbayes2.Cdf(timesince)

            # Use a random sampling to generate a pdf/pmf

            xs = numpy.linspace(0, high-1, high)
            ys = [scipy.misc.derivative(cdf.Prob, x) for x in xs]
            items = dict(zip(xs, ys))
            pmf = thinkbayes2.MakePmfFromItems(items)
            pmf.Normalize()

            self.hypPmfs.append(pmf)


    def Likelihood(self, data, hypo):
        """Computes likelihood of given lambda value for new data under the hypothesis
        
        data: time since last login in hours
        hypo: integer for 1/lambda value (lambda is arrival rate, so hypo is time between logins)
        """

        # print(self.Largest(1))
        largestData = 100*self.timeScale
        if (data > largestData):
            data = largestData

        # print('pmf:',self.hypPmfs[int(hypo)-1])
        # print('time:',data*self.timeScale)
        like = self.hypPmfs[int(hypo)-1].Prob(int(math.ceil(data*self.timeScale)))
    
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
            pmf = self.hypPmfs[int(val)-1]
            qVal = 1-pmf.ProbGreater(thresh)
            qProbs.append(prob)
            qVals.append(qVal)

        qPmf = thinkbayes2.MakePmfFromItems(dict(zip(qVals, qProbs)))

        return qPmf

def QUpdatePlot(pmf, data, thresh):
    """
        Updates a pmf given some data and plots the resulting pmf for the q based on the hypos and some theshold value

        pmf: pmf to be updated
        data: time/array of times since last login of users
        thresh: threshold time since last login used to determine q; 
    """
    if (type(data) is int or type(data) is float):
        pmf.Update(data)
    else:
        pmf.UpdateSet(data)
    thinkplot.Pdf(pmf.generateQ(thresh))

def main():
    # define threshold for Q calulculation in hours
    thresh = 10
    femaleData = [1,1,21,2,24,2,1,2,1,2,5,1,2,1,2,2,2,2,2.67,2,1,2,2,0.08333333333,3,2,24,336,11,3,10,1,0.1833333333,0.7166666667,3,1,1,3,3,3,0.15,3,3,3,48,1,72,2,2,0.6,1,4,5,4,0.6833333333,120,4,0.4,4,4,72,3,24,0.65,0.65,96,0.5333333333,1,2,2,6,3,1,3,720,7,6,24,0.06666666667,0.9,0.06666666667,0.2,0.4333333333,7,96,22,8,1,0.4,48,0.1,2,7,3,0.06666666667,6,24,0.4166666667,9,720,8,1,9]

    # make the priors
    normpmf = thinkbayes2.MakeNormalPmf(120,20,4)
    lampmf = Lambda(2)
    for val, prob in normpmf.Items():
        if val >= 0:
            lampmf[val]=prob
    lampmf.Normalize()

    # thinkplot.Pmf(lampmf)
    lampmf2 = copy.deepcopy(lampmf)
    lampmf3 = lampmf

    # QUpdatePlot(lampmf2, 5, thresh)
    count = 0    
    for x in femaleData:
        print('count:',count)
        print('data:', femaleData[count])
        QUpdatePlot(lampmf, x, thresh)
        count += 1

    # QUpdatePlot(lampmf2,[1,1,21,2,24,2,1,2,1,2,5,1,2,1,2,2,2,2,2.67,2,1,2,2,0.08333333333,3,2,24,336,11,3,10,1,0.1833333333,0.7166666667,3,1,1,3,3,3,0.15,3,3,3,48,1,72,2,2,0.6,1,4,5,4,0.6833333333,120,4,0.4,4,4,72,3,24,0.65,0.65,96,0.5333333333,1,2,2,6,3,1,3,720,7,6,24,0.06666666667,0.9,0.06666666667,0.2,0.4333333333,7,96,22,8,1,0.4,48,0.1,2,7,3,0.06666666667,6,24,0.4166666667,9,720,8,1,9], thresh)

    # Updates the lambda distribution with a the time since last login for a seen user
 
    # QUpdatePlot(lampmf2, 20)
    # QUpdatePlot(lampmf2, 15)
    # QUpdatePlot(lampmf2, 10)
    # QUpdatePlot(lampmf2, 5)

    # QUpdateSetPlot(lampmf2, [20,15,10,5])

    # thinkplot.Show()

    # QUpdatePlot(lampmf3, 5)
    # QUpdatePlot(lampmf3, 10)
    # QUpdatePlot(lampmf3, 15)
    # QUpdatePlot(lampmf3, 20)

    # QUpdateSetPlot(lampmf3, [5, 10, 15, 20])

    thinkplot.Show()

if __name__ == '__main__':
    main()



