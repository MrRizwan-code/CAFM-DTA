
import json

KEEP_STD = ['IC50', 'Ki', 'EC50', 'Kd']
KEEP_ASSAY = ['B', 'F']
OTHER = 'other'

def build_condition_maps(train_df):
    std_map = {c: i for i, c in enumerate(KEEP_STD + [OTHER])}
    assay_map = {c: i for i, c in enumerate(KEEP_ASSAY + [OTHER])}
    return std_map, assay_map

def apply_condition_map(df, std_map, assay_map):
    other_std, other_assay = std_map[OTHER], assay_map[OTHER]
    def map_col(series, m, other_id):
        return [m.get(str(v).strip() if v is not None else OTHER, other_id)
                for v in series.tolist()]
    std_ids = map_col(df['standard_type'], std_map, other_std) if 'standard_type' in df.columns else [other_std]*len(df)
    assay_ids = map_col(df['assay_type'], assay_map, other_assay) if 'assay_type' in df.columns else [other_assay]*len(df)
    return std_ids, assay_ids

def save_maps(path, std_map, assay_map):
    with open(path, 'w') as f:
        json.dump({'std_map': std_map, 'assay_map': assay_map}, f, indent=2)

def load_maps(path):
    with open(path, 'r') as f:
        d = json.load(f)
    return d['std_map'], d['assay_map']
