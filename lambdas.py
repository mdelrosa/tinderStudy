from __future__ import print_function, division
import thinkbayes2
import thinkplot
import math
import matplotlib

class Lambda(thinkbayes2.Suite):
    """Represents distribution of lambda values."""

    def __init__(self):
        """
            Upon initializing, we generate a pmf for each 
        """
        super( Lambda, self ).__init__()
        self["hypPmfs"] = []
        for hypo in range(1,101):
            print('hypo:',hypo)
        # Set up exponential Pmf for a given lambda value;
            if (hypo != 0):
                interarrival = thinkbayes2.MakeExponentialPmf(1/hypo, high=90)
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
            sample = cdf.Sample(10000)
            pdf = thinkbayes2.EstimatedPdf(sample)
            pmf = pdf.MakePmf(low=0, high=100, n=101)
            pmf.Normalize()

            self.hypPmfs[hypo-1] = pmf


    def Likelihood(self, data, hypo):
        """Computes likelihood of given lambda value for new data under the hypothesis
        
        data: time since last login
        hypo: integer for 1/lambda value (lambda is arrival rate, so hypo )
        """
        
        like = self.hypPmfs[hypo+1].Prob(data)
    
        return like

normpmf = thinkbayes2.MakeNormalPmf(10,20,4)
lampmf = Lambda()
for val, prob in normpmf.Items():
    if val >= 0:
        lampmf[val]=prob
lampmf.Normalize()

thinkplot.Pmf(lampmf)
lampmf2 = lampmf

lampmf2.UpdateSet([5,70,45])

thinkplot.Pmf(lampmf2)

thinkplot.Show()