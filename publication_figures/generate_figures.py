"""Run in VS Code: python generate_figures.py. Requires numpy, pandas, matplotlib.
All chart data are local in data/. Output: 600-dpi PNG, vector PDF and SVG.
No training or network access. Edit style constants below to change appearance.
"""
from pathlib import Path
import json,sys
P=Path(__file__).resolve().parent
for folder in ['figures','previews']:(P/folder).mkdir(exist_ok=True)
# Optional bundled libraries on the current workstation; ordinary pip installs work elsewhere.
fallback=P.parent/'05_manuscript_revision/tools/packages'
if fallback.exists():sys.path.insert(0,str(fallback))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
C={'OFF':'#989898','FILM':'#C45C2D','CONCAT':'#497CA5','simple_concat':'#4A9185'}
plt.rcParams.update({'font.family':['Arial','DejaVu Sans'],'font.size':11,'axes.labelsize':11,'axes.titlesize':12,'axes.titlepad':14,'axes.spines.top':False,'axes.spines.right':False,'axes.axisbelow':True,'pdf.fonttype':42,'svg.fonttype':'none','axes.linewidth':.8})
def read(n):return json.loads((P/'data'/n).read_text())
D=read('verified_results.json');S=D['summary']
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(P/'figures'/f'{name}.{ext}',dpi=600,facecolor='white')
 fig.savefig(P/'previews'/f'{name}.png',dpi=125,facecolor='white');plt.close(fig);print(name,flush=True)
def panel(ax,title,x=None,y=None):
 ax.set_title(title,loc='left',fontweight='bold');ax.grid(axis='y',color='#EAEAEA',lw=.7)
 if x:ax.set_xlabel(x,labelpad=9)
 if y:ax.set_ylabel(y,labelpad=9)
def footer(fig,text):fig.text(.5,.025,text,ha='center',va='bottom',fontsize=9,linespacing=1.5)
def legend(fig,ax,y=.96):fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,y),ncol=2,frameon=False)

# 1. Modular architecture: arrows are confined to open corridors between boxes.
fig,ax=plt.subplots(figsize=(12,10));fig.subplots_adjust(left=.02,right=.98,bottom=.02,top=.98)
ax.set(xlim=(0,120),ylim=(-1,100));ax.axis('off')
def box(x,y,w,h,text,color='#F2F2F2',edge='#909090',size=11):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.3,rounding_size=1',fc=color,ec=edge,lw=1.2))
 ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,linespacing=1.5)
def arrow(x,y,u,v,c='#777777'):
 ax.add_patch(FancyArrowPatch((x,y),(u,v),arrowstyle='-|>',mutation_scale=13,lw=1.3,color=c))
ax.text(3,96,'(a) Protein–ligand representation',weight='bold',fontsize=15)
ax.text(78,96,'(b) Assay condition',weight='bold',fontsize=15)
box(3,78,30,13,'Ligand graph\nAtom and bond features')
box(39,78,30,13,'Protein graph\nResidue features + ESM-2')
box(3,58,66,12,'PSICHIC backbone\nThree coupled message-passing layers\nDrug–protein interaction updates',size=12)
arrow(18,78,18,70);arrow(54,78,54,70)
box(3,40,66,11,'Attention-weighted pooling and projection\nDrug vector (200-d) + protein vector (200-d)',color='#E8EEF3')
arrow(36,58,36,51)
box(14,24,44,10,'Concatenation\nInteraction fingerprint h (400-d)',color='#E8EEF3')
arrow(36,40,36,34)
box(78,78,39,13,'Measurement type (32-d embedding)\nAssay format (32-d embedding)',color='#FBECE4',edge=C['FILM'],size=10.5)
box(78,58,39,12,'Concatenate embeddings (64-d)\nMLP: 64 → 64 → 64\nReLU; dropout 0.1',color='#FBECE4',edge=C['FILM'])
arrow(97.5,78,97.5,70,C['FILM'])
box(78,40,39,11,'Condition code c (64-d)\nScale and shift projections\n64 → 400 each',color='#FBECE4',edge=C['FILM'])
arrow(97.5,58,97.5,51,C['FILM'])
box(72,24,45,10,'FiLM parameters\nγ = 1 + g(c);  β = b(c)',color='#FBECE4',edge=C['FILM'],size=12)
arrow(97.5,40,97.5,34,C['FILM'])
box(33,9,49,9,'FiLM: h′ = γ ⊙ h + β\n400-dimensional output',color='#FFF6F0',edge=C['FILM'],size=12)
arrow(36,24,36,18);arrow(94,24,94,13.5,C['FILM']);arrow(94,13.5,82,13.5,C['FILM'])
box(3,0,114,5,'Shared regression head: 400 → 200 → 1     •     Output: predicted pChEMBL',color='white',size=12)
arrow(57,9,57,5)
save(fig,'Figure_1_architecture')

# Variant schematic kept separate, eliminating cramped architecture footnotes.
fig,ax=plt.subplots(figsize=(11,4.6));ax.axis('off');ax.set(xlim=(0,100),ylim=(0,44))
rows=[('off','h → shared regression head'),('simple_concat','[h, c] → Linear (464 → 400) → shared head'),('concat','[h, c] → Linear → ReLU → LayerNorm → shared head'),('film','h′ = (1 + g(c)) ⊙ h + b(c) → shared head')]
for i,(m,txt) in enumerate(rows):
 y=37-i*9;ax.text(2,y,m,fontsize=13,weight='bold',color=C.get(m.upper(),C['simple_concat']));ax.text(24,y,txt,fontsize=12)
ax.text(2,1,'h: 400-d fingerprint; c: 64-d condition code. FiLM projection weights and biases start at zero.',fontsize=10)
save(fig,'Figure_1b_condition_variants')

# 2. Labels sit in a dedicated row above the observations, away from SD whiskers.
metrics=['pearson','rmse','ci','spearman'];names=['Pearson r','RMSE (pChEMBL units)','Concordance index','Spearman ρ']
order=['OFF','CONCAT','FILM','simple_concat'];labels=['off','concat*','film','simple_concat†']
fig,axs=plt.subplots(2,2,figsize=(11,8));fig.subplots_adjust(left=.09,right=.98,top=.92,bottom=.19,wspace=.28,hspace=.46)
for i,(ax,k,n) in enumerate(zip(axs.flat,metrics,names)):
 lows=[];highs=[]
 for j,m in enumerate(order):
  q=S[m][k];sd=q['sd'] or 0;lows.append(q['mean']-sd);highs.append(q['mean']+sd)
  ax.scatter(j+np.linspace(-.10,.10,len(q['values'])),q['values'],s=22,c=C[m],alpha=.45,zorder=3)
  ax.errorbar(j,q['mean'],yerr=q['sd'],fmt='D' if m=='simple_concat' else 'o',color=C[m],ms=8,capsize=4,ecolor='#333333',zorder=4)
  ax.text(j,.96,f"{q['mean']:.4f}",transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=11)
 span=max(highs)-min(lows);ax.set_ylim(min(lows)-span*.15,max(highs)+span*.40)
 ax.set_xlim(-.5,3.5);ax.set_xticks(range(4),labels);ax.tick_params(axis='x',labelsize=10)
 panel(ax,f'({chr(97+i)})  {n}',y='Lower is better' if k=='rmse' else 'Higher is better')
footer(fig,'Mean ± sample SD; off, concat and film: 3 seeds. Small points: individual seeds.\n* Concat aggregate is approximate (seed 1: rounded log).  † Simple_concat: seed 1 only.\nPaired off–film Pearson test: p ≈ 0.0040. All runs: five-epoch training budget.')
save(fig,'Figure_2_primary_ablation')

# 3. Pair-clustered bootstrap slice results and archived per-pair scatter.
B=read('slice_bootstrap_pair_cluster.json');E=read('step_error_vs_disagreement.json')
fig=plt.figure(figsize=(11,8));gs=fig.add_gridspec(2,2,left=.09,right=.97,top=.92,bottom=.14,hspace=.52,wspace=.30)
a=fig.add_subplot(gs[0,0]);b=fig.add_subplot(gs[0,1]);c=fig.add_subplot(gs[1,:])
labs=['All\n(n = 28,673)','Multi-assay\n(n = 5,029)','Single-assay\n(n = 23,644)']
for j,q in enumerate(B):
 a.plot([j,j],[q['off'],q['film']],c='#BBBBBB',lw=2)
 for m in ['off','film']:a.scatter(j,q[m],c=C[m.upper()],s=45,label=m if j==0 else None,zorder=3)
 a.annotate(f"{q['film']:.4f}",(j,q['film']),xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
 a.annotate(f"{q['off']:.4f}",(j,q['off']),xytext=(0,-16),textcoords='offset points',ha='center',fontsize=10,color='#666666')
 gain=q['film']-q['off'];lo,hi=q['ci'];b.bar(j,gain,color=C['FILM'] if j==1 else '#B8C3CC',width=.55)
 b.errorbar(j,gain,yerr=[[gain-lo],[hi-gain]],fmt='none',ecolor='#333333',capsize=4)
 b.text(j,hi+.004,f'{gain:+.4f}',ha='center',fontsize=10)
a.set_ylim(.685,.85);a.set_xlim(-.5,2.5);a.set_xticks(range(3),labs);a.legend(frameon=False,loc='upper left',ncol=2,fontsize=9)
b.set_ylim(0,.105);b.set_xticks(range(3),labs)
panel(a,'(a) Accuracy by measurement group',y='Pearson r');panel(b,'(b) Gain with 95% bootstrap interval',y='Pearson r gain (film − off)')
x=np.array(E['points']['disagreement']);y=np.array(E['points'][next(k for k in E['points'] if k!='disagreement')])
c.scatter(x,y,s=8,alpha=.28,color=C['FILM'],rasterized=True);coef=np.polyfit(x,y,1);xx=np.array([x.min(),x.max()]);c.plot(xx,np.polyval(coef,xx),c='#444444');c.axhline(0,c='#A6B6C3',lw=1)
panel(c,'(c) Per-pair benefit and measurement disagreement',x='Measurement disagreement (SD of observed affinity)',y='MAE reduction (off − film)')
c.text(.99,.95,'Spearman ρ = 0.401; p = 3.66 × 10⁻⁹⁴; n = 2,417 pairs',transform=c.transAxes,ha='right',va='top',fontsize=10)
footer(fig,'Seed 1. Panel (b): 5,000 pair-clustered bootstrap resamples within each slice (protein-ligand pairs).')
save(fig,'Figure_3_measurement_disagreement')

# 4. Scale deviation and cosine similarity, reordered consistently.
G=read('filmparam_analysis.json');types=['IC50','Ki','Kd','EC50','other'];pretty=[r'IC$_{50}$',r'$K_i$',r'$K_d$',r'EC$_{50}$','other'];ix=[0,1,3,2,4]
fig,(a,b)=plt.subplots(1,2,figsize=(11,4.9));fig.subplots_adjust(left=.12,right=.91,bottom=.20,top=.86,wspace=.55)
v=[G['gamma_mean'][k] for k in types]
a.hlines(range(5),v,0,color='#BBBBBB',lw=2);a.scatter(v,range(5),c=C['FILM'],s=60,zorder=3);a.axvline(0,c='#8FA9C0')
for j,z in enumerate(v):a.text(z-.04,j,f'{z:.2f}',ha='right',va='center')
a.set_yticks(range(5),pretty);a.invert_yaxis();a.set_xlim(-1.3,.12);panel(a,'(a) Scale deviation',x='Mean g(c) = γ − 1')
mat=np.array(G['gamma_cosine_matrix'])[np.ix_(ix,ix)];im=b.imshow(mat,cmap='Oranges',vmin=.7,vmax=1)
for i in range(5):
 for j in range(5):b.text(j,i,f'{mat[i,j]:.2f}',ha='center',va='center',color='white' if mat[i,j]>.9 else '#222222',fontsize=11)
b.set_xticks(range(5),pretty);b.set_yticks(range(5),pretty);b.set_title('(b) Similarity between scale deviations',loc='left',weight='bold',fontsize=11)
fig.colorbar(im,ax=b,fraction=.048,pad=.05,label='Cosine similarity')
footer(fig,'Seed 1; assay format fixed to binding (B). Zero scale deviation denotes identity scaling (γ = 1).')
save(fig,'Figure_4_condition_parameters')

# 5. Original intervention values, explicitly retained at their recorded precision.
fig,ax=plt.subplots(figsize=(7.5,6));fig.subplots_adjust(left=.15,right=.96,top=.76,bottom=.18)
x=np.array([0,.5,1,2]);w=np.array([0,.480,1.140,2.054]);z=np.array([r['recovered'] for r in read('step2_recovery_predshift.json')]);xx=np.linspace(0,2.1,100)
ax.plot(xx,xx,'--',c='#999999',label='Identity (shift = offset)')
for vals,label,filled in [(w,'Within-pair',True),(z,'Absolute',False)]:
 slope=np.dot(x,vals)/np.dot(x,x);ax.plot(xx,xx*slope,c=C['FILM'],ls='-' if filled else ':');ax.scatter(x,vals,s=65,facecolors=C['FILM'] if filled else 'white',edgecolors=C['FILM'],linewidth=1.6,zorder=3,label=f'{label} shift (slope {slope:.3f})')
ax.set_xlim(-.08,2.15);ax.set_ylim(-.08,2.22);panel(ax,'',x='Offset injected into Kᵢ training labels (pChEMBL units)',y='Recovered prediction shift (pChEMBL units)');legend(fig,ax,.97)
footer(fig,'Seed 1; eight-epoch intervention budget. Within-pair values retain three-decimal source precision.')
save(fig,'Figure_5_intervention')

# Figures 6 and S2 are generated by generate_corrected_figures.py below.

# 7. Matched controls separated visually from contextual external baselines.
cold={r['model']:r for r in D['records'] if r['split']=='cold'}
fig,axs=plt.subplots(1,2,figsize=(11,5));fig.subplots_adjust(left=.09,right=.97,top=.84,bottom=.26,wspace=.30)
for i,(ax,k) in enumerate(zip(axs,['pearson','rmse'])):
 vals=[cold['OFF'][k],cold['FILM'][k],read('deepdta_coldsplit_result.json')[k],read('graphdta_coldsplit_result.json')[k]]
 for j,v in enumerate(vals):ax.scatter(j,v,s=75,c=[C['OFF'],C['FILM'],'#6C91B0','#6C91B0'][j]);ax.annotate(f'{v:.4f}',(j,v),xytext=(0,12),textcoords='offset points',ha='center')
 ax.axvline(1.5,c='#BBBBBB',ls='--');ax.set_xticks(range(4),['off','film','DeepDTA','GraphDTA']);ax.set_xlim(-.5,3.5);ax.margins(y=.30)
 panel(ax,f'({chr(97+i)}) '+('Pearson r (higher is better)' if k=='pearson' else 'RMSE (lower is better)'))
 ax.text(.25,-.19,'Matched, 15 epochs',transform=ax.transAxes,ha='center',fontsize=9);ax.text(.77,-.19,'External baselines',transform=ax.transAxes,ha='center',fontsize=9)
footer(fig,'Cold-ligand test: 28,698 measurements. Off and film: seed 1; external baselines: single convergence runs.\nNo between-seed error bars. Different baseline protocols limit direct architectural comparisons.')
save(fig,'Figure_7_cold_ligand')

# S1. Gains from saved per-assay analysis.
Q=read('step12c_perassay.json');keys=['IC50','Ki','EC50','Kd']
fig,ax=plt.subplots(figsize=(7,5));fig.subplots_adjust(left=.15,right=.96,top=.88,bottom=.23)
v=[Q[k]['gain'] for k in keys];ax.bar(range(4),v,color=C['FILM'],width=.6)
for i,z in enumerate(v):ax.text(i,z+.003,f'{z:+.4f}',ha='center')
assay_labels=[r'IC$_{50}$',r'$K_i$',r'EC$_{50}$',r'$K_d$']
ax.set_xticks(range(4),[f'{label}\n(n = {Q[k]["n"]:,})' for k,label in zip(keys,assay_labels)]);ax.set_ylim(0,.10);panel(ax,'',y='Pearson r gain (film − off)')
footer(fig,'Primary split; mean gain across three seeds. Other measurement types are not plotted.')
save(fig,'Figure_S1_measurement_type')

# S3. Use the archived bin counts and values without interpolation.
Q=read('step12e_ad_curve.json');q=Q['bins'];fig,(a,b)=plt.subplots(1,2,figsize=(11,5));fig.subplots_adjust(left=.09,right=.97,top=.86,bottom=.27,wspace=.35)
for m in ['OFF','FILM']:a.plot(range(5),[r[m.lower()+'_r'] for r in q],'o-',color=C[m],label=m.lower())
for ax in [a,b]:ax.set_xticks(range(5),[r['bin'] for r in q],rotation=25);ax.set_xlabel('Nearest-training-ligand Tanimoto similarity',labelpad=10)
panel(a,'(a) Accuracy by similarity bin',y='Pearson r');a.legend(frameon=False)
n=[r['n'] for r in q];b.bar(range(5),n,color=['#B8C3CC']*4+[C['FILM']]);b.set_ylim(0,33000)
for i,z in enumerate(n):b.text(i,z+750,f'{z:,}\n{z/sum(n)*100:.1f}%',ha='center',fontsize=10)
panel(b,'(b) Test-set coverage',y='Number of measurements')
footer(fig,'Primary split; three-seed mean correlations. Median ligand similarity = 1.000. Lowest bin: only 72 measurements.')
save(fig,'Figure_S3_applicability')

# S4. Bias means and SD are calculated from the archived per-seed values.
Q=read('step12d_calibration.json');fig,(a,b)=plt.subplots(1,2,figsize=(11,5));fig.subplots_adjust(left=.10,right=.97,top=.88,bottom=.22,wspace=.36)
a.plot([4.5,9],[4.5,9],'--',c='#AAAAAA')
for m in ['OFF','FILM']:
 q=Q[m.lower()];a.plot(q['truth'],q['pred'],'o-',c=C[m],label=m.lower(),ms=5)
a.legend(frameon=False);panel(a,'(a) Reliability',x='Observed affinity (pChEMBL)',y='Predicted affinity (pChEMBL)')
for j,m in enumerate(['OFF','FILM']):
 vals=Q['per_seed_bias'][m.lower()];b.scatter(j+np.array([-.06,0,.06]),vals,facecolors='white',edgecolors=C[m],s=45,zorder=3);b.errorbar(j,np.mean(vals),yerr=np.std(vals,ddof=1),fmt='_',color=C[m],ms=22,capsize=5)
b.axhline(0,c='#A6B6C3');b.set_xticks([0,1],['off','film']);b.set_xlim(-.5,1.5);panel(b,'(b) Prediction bias',y='Predicted − observed affinity')
footer(fig,'Primary split, three seeds. Bias: mean ± sample SD; open points: individual seeds.\nECE: off 0.056 ± 0.009; film 0.127 ± 0.058. Lower prediction error does not imply better calibration.')
save(fig,'Figure_S4_calibration')

import subprocess
subprocess.run([sys.executable, str(P/'generate_corrected_figures.py')], check=True)
