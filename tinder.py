# tinder.py

from __future__ import print_function, division

import numpy
import thinkbayes2
import thinkplot


def main():
	maleRates = [0.52, 0.38, 0.39, 1.01, 2.63]
	femaleRates = [50, 20.5]
	pdfMale = thinkbayes2.EstimatedPdf(maleRates)
	pdfFemale = thinkbayes2.EstimatedPdf(femaleRates)
	low, high = 0, 100
	n = 101
	xs = numpy.linspace(low, high, n)
	pmfMale = pdfMale.MakePmf(steps=xs)
	pmfFemale = pdfFemale.MakePmf(steps=xs)

	thinkplot.Pdf(pdfMale, label='Male Prior')
	thinkplot.Pdf(pdfFemale, label='Female Prior')
	thinkplot.show()

if __name__ == '__main__':
	main()
