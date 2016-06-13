"""
This test file is meant for developing purposes. Providing an easy method to
test the functioning of gwtsa during development.

"""

from gwtsa import *

# read observations
fname = 'data/B32D0136001_1.csv'
obs = ReadSeries(fname,'dino')

# Create the time series model
ml = Model(obs.series)

# read climate data
fname = 'data/KNMI_20160522.txt'
RH=ReadSeries(fname,'knmi',variable='RH')
EV24=ReadSeries(fname,'knmi',variable='EV24')

# Create stress
ts = Recharge(RH.series, EV24.series, Gamma(), Linear(), name='recharge')
ml.addtseries(ts)

# Add drainage level
d = Constant(obs.series.min())
ml.addtseries(d)

# Add noise model
n = NoiseModel()
ml.addnoisemodel(n)

# Solve the time series model
ml.solve()

# show results
ml.plot()
ml.stats.summary()