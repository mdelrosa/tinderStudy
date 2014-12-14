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

    def __init__(self, label=None):
        """
            - Upon setting priors, we generate a pmf for each hypo that represents
            the probability that an observed user has not logged in for a
            specified amount of time.
            - This generation of pmfs was initially done in likelihood, but this
            became to computationally expensive to do given the size of our data
            set. It is faster to calculate all pmfs before trying to run any updates.
        """
        # Ensure that the __init__'s of super classes are carried out
        super( Lambda, self ).__init__()

        # Initialize container for hypo pmfs
        self.hypPmfs = []

        # Iterate through all 100 hypos. These each represent hours since login
        for hypo in range(1,101):

        # Set up exponential Pmf for a given lambda value;
            if (hypo != 0):
                interarrival = thinkbayes2.MakeExponentialPmf(1/hypo, high=101)
            for val, prob in interarrival.Items():
                interarrival[val] *= val
            interarrival.Normalize()

            # Make a mixture of uniform distributions of time since last login
            metapmf = thinkbayes2.Pmf()
            for time, prob in interarrival.Items():
                if time == 0:
                    continue
                pmf = thinkbayes2.MakeUniformPmf(0, time, 101)
                metapmf[pmf] = prob

            timesince = thinkbayes2.MakeMixture(metapmf)

            # Make a cdf using the mixture
            cdf = thinkbayes2.Cdf(timesince)

            # Take derivative of cdf to generate its pmf
            xs = numpy.linspace(0, 100, 101)
            ys = [scipy.misc.derivative(cdf.Prob, x) for x in xs]
            items = dict(zip(xs, ys))
            pmf = thinkbayes2.MakePmfFromItems(items)
            pmf.Normalize()

            # Store pmf in object to be called on later in Likelihood
            self.hypPmfs.append(pmf)


    def Likelihood(self, data, hypo):
        """Computes likelihood of given lambda value for new data under the hypothesis.
        
        data: time since last login
        hypo: integer for 1/lambda value (lambda is arrival rate, so hypo is time between logins)
        """

        # Note: Some of the data which we collected was much larger than
        # our upper limit, so we attenuate these outliers with this conditional
        upper = 99
        if (data > upper):
            data = upper

        # The likelihood is the probability that you saw a person at a given
        like = self.hypPmfs[int(hypo)+1].Prob(math.ceil(data))
    
        return like

    def generateQ(self, thresh):
        """
        - Creates a distribution of probabilities of q, which is the percentage of active users
            - Assumes that "active user" is based on some threshold # of logins per day
            - PMF: x axis is q values, y axis is probability that said q value is true

        qProbs = probabilities for q PMF
        qVals = values for q PMF
        """
        qProbs = []
        qVals = []

        # Iterate through hypos
        for val, prob in self.Items():
            """
            The probability of a given q value is the total probability that it has been less
            than some threshold time since a user has logged in.
            """
            # Access relevant pmf
            pmf = self.hypPmfs[int(val)+1]
            # Get probability that observed time is less than threshold time
            qVal = 1-pmf.ProbGreater(thresh)
            # Add q probabilities and values
            qProbs.append(prob)
            qVals.append(qVal)

        # Generate pmf from q values and probabilities
        qPmf = thinkbayes2.MakePmfFromItems(dict(zip(qVals, qProbs)))

        return qPmf

def QUpdatePlot(pmf, data, thresh, label=None):
    if (type(data) is int or type(data) is float):
        pmf.Update(data)
        thinkplot.Pdf(pmf.generateQ(thresh), label=label)
    else:
        pmf.UpdateSet(data)
        thinkplot.Pdf(pmf.generateQ(thresh), label=label)

def QVals():
    QUpdatePlot(lampmf2, femaleData, 5, label='Thresh=5')
    QUpdatePlot(lampmf3, femaleData, 10, label='Thresh=10')

    ### Plot
    # thinkplot.Show( legend=True,
    #                 xlabel='Q Value',
    #                 ylabel='Probability',
    #                 title='Q Values for Given Threshold')

    ### Save
    formats = ['png']
    root = 'Q Values'
    thinkplot.Save(root=root,
                   xlabel='Q Value',
                   ylabel='Probability',
                   formats=formats,
                   legend=True,
                   title='Q Values for Given Threshold')

def PriorPost(pmf, data):
    thinkplot.Pdf(pmf, label='Prior')
    pmf.UpdateSet(data)
    thinkplot.Pdf(pmf, label='Posterior')

    # thinkplot.Show(xlabel='Lambda',
    #                ylabel='Probability',
    #                legend=True,
    #                title='Arrival Rate Distribution')

    formats = ['png']
    root = 'PriorAndPosterior'
    thinkplot.Save(root=root,
                   xlabel='Lambda',
                   ylabel='Probability',
                   legend=True,
                   formats=formats,
                   title='Arrival Rate Distribution')

def main():
    # Data of time since last login for >100 observed females
    femaleData=[1,1,21,2,24,2,1,2,1,2,5,1,2,1,2,2,2,2,2.67,2,1,2,2,0.08333333333,3,2,24,336,11,3,10,1,0.1833333333,0.7166666667,3,1,1,3,3,3,0.15,3,3,3,48,1,72,2,2,0.6,1,4,5,4,0.6833333333,120,4,0.4,4,4,72,3,24,0.65,0.65,96,0.5333333333,1,2,2,6,3,1,3,720,7,6,24,0.06666666667,0.9,0.06666666667,0.2,0.4333333333,7,96,22,8,1,0.4,48,0.1,2,7,3,0.06666666667,6,24,0.4166666667,9,720,8,1,9]

    # make the priors (normal distribution)
    normpmf = thinkbayes2.MakeNormalPmf(10,10,4)
    lampmf = Lambda(label='Thresh=5')
    for val, prob in normpmf.Items():
        if (val >= 0 and val <=100):
            lampmf[val]=prob
    lampmf.Normalize()

    # thinkplot.Pmf(lampmf)
    lampmf2 = copy.deepcopy(lampmf)
    lampmf3 = lampmf.Copy(label='Thresh=10')

    # QVals()

    # PriorPost(lampmf, femaleData)
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

if __name__ == '__main__':
    main()



