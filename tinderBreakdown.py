from __future__ import print_function, division

"""
Predicting percentage of Tinder users by gender in a given area
This code is based on euro.py from Allen Downey's ThinkBayes
"""

import thinkbayes2
import thinkplot


class Tinder(thinkbayes2.Suite):
    """Represents hypotheses about the probability of heads."""

    def Likelihood(self, data, hypo):
        """Computes the likelihood of the data under the hypothesis.

        hypo: integer value of x, the probability that there are a given percentage of males using Tinder (0-100)
        data: string 'H' or 'T'
        """
        scale = 0.75
        
        if data['gender'] == 'Male':
            x = scale*abs(hypo-data['rate']) / 100.0
            return 1-x
        else:
            x = scale*abs(hypo-(100-data['rate'])) / 100.0
            return 1-x

def TrianglePrior():
    """Makes a Suite with a triangular prior."""
    suite = Tinder()
    for x in range(0, 51):
        suite.Set(x, x)
    for x in range(51, 101):
        suite.Set(x, 100-x) 
    suite.Normalize()
    return suite


def RunUpdate(suite, rate, gender):
    """Updates the Suite with the given number of heads and tails.

    suite: Suite object
    rate: matching response rate
    gender: male or female
    """
    data = {'rate': rate, 'gender': gender}

    suite.Update(data)


def Summarize(suite):
    """Prints summary statistics for the suite."""
    print(suite.Prob(50))

    print('MLE', suite.MaximumLikelihood())

    print('Mean', suite.Mean())
    print('Median', suite.Percentile(50)) 

    print('5th %ile', suite.Percentile(5)) 
    print('95th %ile', suite.Percentile(95)) 

    print('CI', suite.CredibleInterval(90))


def PlotSuites(suites, root):
    """Plots two suites.

    suite1, suite2: Suite objects
    root: string filename to write
    """
    formats = ['pdf', 'png']
    thinkplot.Clf()
    thinkplot.PrePlot(len(suites))
    thinkplot.Pmfs(suites)
    thinkplot.Save(root=root,
                   xlabel='Percentage of Active Female Users',
                   ylabel='Probability',
                   formats=formats,
                   legend=True)


def main():
    # make the priors
    suiteTri = TrianglePrior()
    suiteTri.name = 'Prior'
    suiteUpd = TrianglePrior()
    suiteUpd.name = 'Final Posterior'

    # plot the priors
    PlotSuites([suiteTri], 'Prior')

    # update based on collected data
    RunUpdate(suiteUpd, 0.52, "Male")
    RunUpdate(suiteUpd, 0.38, "Male")
    RunUpdate(suiteUpd, 0.39, "Male")
    RunUpdate(suiteUpd, 1.01, "Male")
    RunUpdate(suiteUpd, 2.63, "Male")
    RunUpdate(suiteUpd, 50, "Female")
    RunUpdate(suiteUpd, 20.5, "Female")
    Summarize(suiteUpd)

    # plot the posteriors
    PlotSuites([suiteUpd], 'Posterior')

if __name__ == '__main__':
    main()
