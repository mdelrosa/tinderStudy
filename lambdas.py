from __future__ import print_function, division
import thinkbayes2
import thinkplot
import math
%matplotlib inline

class Lambda(thinkbayes2.Suite):
    """Represents distribution of lambda values."""

    def Likelihood(self, data, hypo):
        """Computes likelihood of given lambda value for new data under the hypothesis
        
        data: time since last login
        hypo: integer for lambda value
        """
        
        interarrival = thinkbayes2.MakeExponentialPmf(hypo, high=90)
        for val, prob in interarrival.Items():
            interarrival[val] *= val
        interarrival.Normalize()
        
        metapmf = thinkbayes2.Pmf()
        for time, prob in interarrival.Items():
            if time == 0:
                continue
            pmf = thinkbayes2.MakeUniformPmf(0, time, 101)
            metapmf[pmf] = prob
        timesince = thinkbayes2.MakeMixture(metapmf)
        thinkplot.Pmf(timesince)
        
        cdf = thinkbayes2.Cdf(timesince)
        sample = cdf.Sample(10000)
        pdf = thinkbayes2.EstimatedPdf(sample)
        
        
        
        like = pdf[math.ceil(data)]
    
        return like

normpmf = thinkbayes2.MakeNormalPmf(10,20,4)
lampmf = Lambda()
for val, prob in normpmf.Items():
    if val >= 0:
        lampmf[val]=prob
lampmf.Normalize()
        
thinkplot.Pmf(lampmf)


lampmf.Update(1)

thinkplot.Pmf(lampmf)
