"""Regenerate corrected Figures 6/S2 from packaged verified summaries; no training."""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=P)
args=parser.parse_args()
OUT=args.output_dir.resolve()
for folder in ['figures','previews']:(OUT/folder).mkdir(parents=True,exist_ok=True)
evidence=json.loads((P.parent/'results/corrected_checkpoint_summary.json').read_text())
summary=evidence['ds2_summary'];paired=evidence['ds2_paired_test']
T=pd.read_csv(P/'data/per_target.csv')
# Preserve the embedded figures' overall design, colors and aspect ratios.
plt.rcParams.update({'font.family':['Arial','DejaVu Sans'],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.axisbelow':True,'pdf.fonttype':42,'svg.fonttype':'none'})
colors={'off':'#989898','film':'#bf5b29'}
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(OUT/'figures'/f'{name}.{ext}',dpi=600,facecolor='white')
 fig.savefig(OUT/'previews'/f'{name}.png',dpi=125,facecolor='white');plt.close(fig)
primary=json.loads((P/'data/verified_results.json').read_text())['summary']
metrics=['pearson','rmse','ci','spearman']; names=['Pearson r','RMSE (pChEMBL units)','Concordance index','Spearman ρ']
fig,axs=plt.subplots(2,2,figsize=(10.5,8.1));fig.subplots_adjust(left=.11,right=.97,top=.93,bottom=.21,wspace=.35,hspace=.40)
ylims=[(.74,.87),(.73,.85),(.77,.85),(.75,.87)]
for i,(ax,k,title) in enumerate(zip(axs.flat,metrics,names)):
 for j,m in enumerate(['off','film']):
  vals=[primary[m.upper()][k]['mean'],summary[m][k]['mean']];sd=[primary[m.upper()][k]['sd'],summary[m][k]['sd']]
  ax.bar(np.arange(2)+(j-.5)*.29,vals,width=.29,yerr=sd,color=colors[m],hatch='//' if m=='off' else None,edgecolor='#555555',capsize=4,label=m)
 ax.set_xticks([0,1],['Primary','DS2']);ax.set_ylabel(title);ax.set_ylim(*ylims[i]);ax.grid(axis='y',color='#e8e8e8');ax.set_title(f'({chr(97+i)})',loc='left',fontweight='bold',pad=14)
fig.legend(*axs[0,0].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,.115),ncol=2,frameon=False)
fig.text(.5,.07,'Mean ± sample SD, three seeds. Primary: 5 epochs; DS2: 15 epochs.',ha='center',fontsize=10)
fig.text(.5,.035,f'Primary Pearson p ≈ 0.0040; DS2 p = {paired["p"]:.4f} (corrected checkpoint predictions).',ha='center',fontsize=10)
save(fig,'Figure_6_dataset_comparison')

fig,(a,b)=plt.subplots(2,1,figsize=(10.5,7),gridspec_kw={'height_ratios':[1.3,1]});fig.subplots_adjust(left=.15,right=.91,top=.93,bottom=.18,hspace=.42)
x=np.arange(len(T));a.axvspan(4.5,9.5,color='#f2efec')
for j,row in T.iterrows():a.plot([j,j],[row.r_off,row.r_film],color='#c7c7c7',lw=3)
for m in ['off','film']:a.scatter(x,T['r_'+m],color=colors[m],edgecolor='white',s=48,label=m+' (PSICHIC baseline)' if m=='off' else m+' (CAFM-DTA)',zorder=3)
a.set_xticks(x,[]);a.set_xlim(-.5,9.5);a.set_ylim(.735,.875);a.grid(axis='y',color='#e4e4e4');a.axvline(4.5,color='#bbbbbb');a.set_ylabel('Pearson correlation (r)');a.legend(frameon=False,loc='upper left',fontsize=10)
a.set_title('(a)  Per-target accuracy',loc='left',pad=12)
mat=T[['d_r','d_rmse','d_sp']].to_numpy().T
im=b.imshow(mat,aspect='auto',cmap='viridis',vmin=0,vmax=max(.07,mat.max()))
for i in range(3):
 for j in range(10):b.text(j,i,f'{mat[i,j]:.3f}',ha='center',va='center',color='white' if mat[i,j]<.045 else '#202020',fontsize=10)
b.set_xticks(x,T.target);b.set_yticks([0,1,2],['Pearson r ↑','RMSE ↓','Spearman ρ ↑']);b.axvline(4.5,color='white',lw=2)
b.set_title('(b)  Per-target improvement (positive favors film)',loc='left',pad=12)
cax=fig.add_axes([.925,.18,.015,.28]);fig.colorbar(im,cax=cax);cax.set_ylabel('Improvement')
fig.text(.34,.11,'Primary (5 CRC targets)',ha='center',color='#555555');fig.text(.72,.11,'DS2 (5 independent targets)',ha='center',color='#555555')
fig.text(.5,.045,'Measurement-aligned predictions: primary seed 1; DS2 mean across seeds 1, 2 and 3.',ha='center',fontsize=9)
save(fig,'Figure_S2_targets')
