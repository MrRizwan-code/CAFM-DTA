"""Validate packaged corrected plotting inputs; never restore historical screening data."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
T=pd.read_csv(P/'data/per_target.csv')
reports={}
for p in (P.parent/'results/corrected_checkpoint_reports').glob('ds2_*.json'):
    d=json.loads(p.read_text());reports[d['mode'],d['seed']]=d
assert len(reports)==6
for _,row in T[T.group=='DS2'].iterrows():
    for mode in ['off','film']:
        for column,metric in [('r','pearson'),('rmse','rmse'),('sp','spearman')]:
            expected=np.mean([reports[mode,s]['per_target'][row.target][metric] for s in [1,2,3]])
            assert np.isclose(row[column+'_'+mode],expected,atol=1e-12,rtol=0)
print('PASS: corrected per-target plotting data match all six archived checkpoint reports.')
