import sys

# Dictionary mapping rsid to (Trait, Description)
KNOWLEDGE_BASE = {
    # Health & Diet
    'rs4988235': ('Lactose Tolerance', 'MCM6 gene. AA/AG = Lactose tolerant. GG = Lactose intolerant.'),
    'rs1801282': ('PPARg / Metabolism', 'PPARG gene. CG/GG = Better insulin sensitivity. CC = Normal.'),
    'rs9939609': ('Obesity Risk', 'FTO gene. AA = Higher risk of obesity. AT/TT = Normal risk.'),
    'rs1801260': ('Circadian Rhythm', 'CLOCK gene. TT = Early riser. CC/CT = Evening preference, sleep issues.'),
    'rs1799971': ('Pain / Opioid Sensitivity', 'OPRM1 gene. GG/AG = Higher pain sensitivity, lower opioid response. AA = Normal.'),
    'rs1800497': ('Dopamine D2 Receptor', 'DRD2 gene. A1/A1 (often reported as TT or AA depending on strand) = Lower dopamine receptors, risk for addiction/obesity.'),
    
    # Fitness & Body
    'rs1815739': ('Muscle Type (ACTN3)', 'ACTN3 gene. CC/CT = Sprint/power athlete (fast-twitch). TT = Endurance athlete.'),
    'rs6152': ('Male Pattern Baldness', 'AR gene (X chromosome). G = Higher risk. A = Lower risk.'),
    
    # Traits & Appearance
    'rs12913832': ('Eye Color', 'HERC2 gene. GG = Blue eyes. AA/AG = Brown eyes.'),
    'rs1805007': ('Red Hair / Sun Sensitivity', 'MC1R gene. CC/CT = Normal. TT = High chance of red hair/freckles.'),
    
    # Behavior & Brain
    'rs4680': ('Warrior vs Worrier', 'COMT gene. GG = Warrior (better under stress, lower dopamine). AA = Worrier (worse under stress, higher dopamine/memory). AG = Balanced.'),
    'rs53576': ('Empathy / Oxytocin', 'OXTR gene. GG = Highly empathetic, handles stress well. AA/AG = Less empathetic, introverted.'),
    
    # Severe Health Risks (often redacted but worth checking)
    'rs7412': ('APOE - Alzheimer\'s', 'APOE gene marker 1.'),
    'rs429358': ('APOE - Alzheimer\'s', 'APOE gene marker 2.'),
    'rs738409': ('Fatty Liver Disease', 'PNPLA3 gene. GG = High risk of fatty liver. CC = Normal.'),
    'rs1799945': ('Hemochromatosis', 'HFE gene. GG = High risk of iron overload. CC = Normal.')
}

def analyze_snps(filepath):
    found_snps = {}
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split('\t')
            if len(parts) == 5:
                rsid, chrom, pos, a1, a2 = parts
                if rsid in KNOWLEDGE_BASE:
                    found_snps[rsid] = a1 + a2
                    
    # Report
    print("=== ULTRATHINK DNA EXTRACT ===")
    for rsid, info in KNOWLEDGE_BASE.items():
        trait, desc = info
        gt = found_snps.get(rsid, "Not found in dataset")
        print(f"\n[ {trait} ] - {rsid}")
        print(f"Genotype: {gt}")
        print(f"Context : {desc}")

if __name__ == "__main__":
    analyze_snps(sys.argv[1])
