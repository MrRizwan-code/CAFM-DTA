"""Recover plotting data from the archived study outputs; no model training."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
R=P.parents[1]
src=R/'code_extracted/CAFM-DTA'
code=(src/'analysis/figS2_pertarget_gain.py').read_text(encoding='utf-8')
env={'__file__':str(src/'analysis/figS2_pertarget_gain.py')}
exec(code[:code.index('try:\n    import matplotlib')],env)
env['T'].to_csv(P/'data/per_target.csv',index=False)
base=R/'zenodo_package/predictions_evalpath/primary_seed1'
a=pd.read_csv(base/'OFF_test_prediction_EVALPATH_seed1.csv')
b=pd.read_csv(base/'FILM_test_prediction_EVALPATH_seed1.csv')
keys=['Protein','Ligand','standard_type','assay_type','reg_truth']
assert a[keys].equals(b[keys]),'Prediction rows must align exactly'
y=a.reg_truth.to_numpy();u=a.reg_pred.to_numpy();v=b.reg_pred.to_numpy()
counts=a.groupby(['Protein','Ligand'])['reg_truth'].transform('size').to_numpy()
multi=counts>1
assert len(y)==28673 and multi.sum()==5029
rng=np.random.default_rng(42);boot=np.empty((5000,3))
def corr(x,y):
 x=x-x.mean();y=y-y.mean();return np.dot(x,y)/np.sqrt(np.dot(x,x)*np.dot(y,y))
for i in range(5000):
 ix=rng.integers(0,len(y),len(y));m=multi[ix]
 for j,ii in enumerate([ix,ix[m],ix[~m]]):boot[i,j]=corr(y[ii],v[ii])-corr(y[ii],u[ii])
out=[]
for j,m in enumerate([np.ones(len(y),bool),multi,~multi]):
 out.append({'n':int(m.sum()),'off':corr(y[m],u[m]),'film':corr(y[m],v[m]),'ci':np.percentile(boot[:,j],[2.5,97.5]).tolist()})
(P/'data/slice_bootstrap.json').write_text(json.dumps(out,indent=2))
print('Saved per-target values and 5,000-resample measurement bootstrap intervals.')
