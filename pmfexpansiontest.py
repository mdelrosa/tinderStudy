# tinder.py

from __future__ import print_function, division

import numpy
import thinkbayes2
import thinkplot

def MakePmfTest(shelf, **options):
    """Makes a discrete version of this Pdf.

    options can include
    label: string
    low: low end of range
    high: high end of range
    n: number of places to evaluate

    Returns: new Pmf
    """
    #print(options)
    label = options.pop('label', '')
    xs, ds = Render(shelf,**options)
    #print()
    #print(xs)
    #print(ds)
    return thinkbayes2.Pmf(dict(zip(xs, ds)), label=label)

def Render(shelf, **options):
    """Generates a sequence of points suitable for plotting.

    Returns:
        tuple of (xs, densities)
    """
    #low, high = options.pop('low', None), options.pop('high', None)
    steps = options.pop('steps')
    low = steps.min()
    high = steps.max()
    n = len(steps)

    print(n)

    xs = numpy.linspace(low, high, 1001)
            
    ds = shelf.Density(xs)
    return xs, ds


def main():
	maleRates = [0.52, 0.38, 0.39, 1.01, 2.63, 30]
	femaleRates = [50, 20.5, 40, 30, 45]
	pdfMale = thinkbayes2.EstimatedPdf(maleRates)
	pdfFemale = thinkbayes2.EstimatedPdf(femaleRates)
	low, high = 0, 100
	n = 1001
	xs = numpy.linspace(low, high, n)
	pmfMale = MakePmfTest(pdfMale,steps=xs)
	pmfFemale = MakePmfTest(pdfFemale,steps=xs)

	pmfMale.Normalize()
	pmfFemale.Normalize()

	thinkplot.Pdf(pmfMale, label='Male Prior')
	thinkplot.Pdf(pmfFemale, label='Female Prior')
	thinkplot.show()

if __name__ == '__main__':
	main()
