import sys
import json

MACRO_SNPS = {
    # == TRACK A: CLINICAL & LONGEVITY ==
    'rs1801133': ('MTHFR (Methylation)', 'C = Normal. T = Reduced enzyme activity (requires methylated folate/B12).'),
    'rs1801131': ('MTHFR (Methylation)', 'A = Normal. C = Reduced enzyme activity.'),
    'rs7412': ('APOE (Alzheimers/Cardio)', 'Marker 1 for APOE status.'),
    'rs429358': ('APOE (Alzheimers/Cardio)', 'Marker 2 for APOE status. C = Risk allele (e4).'),
    'rs1799945': ('HFE (Hemochromatosis)', 'C = Normal. G = Hemochromatosis risk (H63D).'),
    'rs1800562': ('HFE (Hemochromatosis)', 'G = Normal. A = Hemochromatosis risk (C282Y).'),
    'rs738409': ('PNPLA3 (Fatty Liver)', 'C = Normal. G = High risk of NAFLD.'),
    'rs12255372': ('TCF7L2 (Type 2 Diabetes)', 'G = Normal. T = Higher risk of T2D.'),
    'rs7903146': ('TCF7L2 (Type 2 Diabetes)', 'C = Normal. T = Higher risk of T2D.'),
    'rs1800629': ('TNF-Alpha (Inflammation)', 'G = Normal. A = Higher baseline inflammation/autoimmune risk.'),
    'rs662': ('PON1 (Heart Disease/Toxins)', 'A = Low enzyme activity. G = High enzyme activity (protective).'),
    'rs174537': ('FADS1 (Omega-3 Metabolism)', 'G = Normal EPA/DHA synthesis. T = Poor conversion of plant Omega-3s.'),
    
    # == TRACK B: OPTIMIZATION & DIET ==
    'rs4988235': ('MCM6 (Lactose Tolerance)', 'A/G = Tolerant. G/G = Intolerant (European).'),
    'rs9939609': ('FTO (Obesity Risk)', 'T = Normal. A = Higher obesity risk, lower satiety.'),
    'rs1801282': ('PPARG (Insulin Sensitivity)', 'C = Normal. G = Better insulin sensitivity.'),
    'rs762551': ('CYP1A2 (Caffeine Metabolism)', 'A = Fast metabolizer. C = Slow metabolizer (caffeine disrupts sleep/blood pressure).'),
    'rs1815739': ('ACTN3 (Muscle Fiber)', 'C = Fast twitch (Power). T = Slower twitch (Endurance).'),
    'rs1042713': ('ADRB2 (Exercise Response)', 'A = Good response to endurance. G = Good response to resistance training.'),
    'rs4341': ('ACE (Blood Pressure/Fitness)', 'G = Power/Strength bias. C = Endurance bias.'),
    'rs1544410': ('VDR (Vitamin D Receptor)', 'A = Higher need for Vitamin D. G = Normal.'),
    
    # == TRACK C: BEHAVIORAL & NEURO ==
    'rs4680': ('COMT (Warrior/Worrier)', 'G = Warrior (Fast dopamine clearance). A = Worrier (Slow dopamine clearance).'),
    'rs53576': ('OXTR (Empathy/Stress)', 'G = Highly empathetic. A = Introverted, less sensitive to social stress.'),
    'rs1800497': ('DRD2 (Dopamine Receptor)', 'G = Normal. A = Fewer D2 receptors (risk of addiction/overeating).'),
    'rs25531': ('SLC6A4 (Serotonin Transporter)', 'Related to serotonin reuptake (often grouped with 5-HTTLPR).'),
    'rs1800955': ('DRD4 (Novelty Seeking)', 'C = Normal. T = Higher novelty seeking / risk taking.'),
    'rs6265': ('BDNF (Brain Plasticity)', 'G = Normal BDNF production. A = Lower BDNF (harder to learn under stress).'),
    'rs1611115': ('DBH (Dopamine Beta-Hydroxylase)', 'C = Normal dopamine->norepinephrine conversion. T = Slower conversion (prone to brain fog).'),
    'rs1801260': ('CLOCK (Circadian Rhythm)', 'T = Morning person. C = Evening person.'),
    
    # == TRACK D: PHARMACOGENOMICS & OTHER ==
    'rs1799971': ('OPRM1 (Opioid/Pain Sensitivity)', 'A = Normal. G = Requires more anesthesia/opioids for pain relief.'),
    'rs1045642': ('ABCB1 (Drug Transporter)', 'C = Normal. T = Altered drug transport in gut/blood-brain barrier.'),
    'rs12913832': ('HERC2 (Eye Color)', 'A = Brown/Dark. G = Blue/Light.'),
    'rs1805007': ('MC1R (Red Hair/Sun)', 'C = Normal. T = Burn easily/Red hair.')
}

def analyze_snps(filepath):
    found_snps = {}
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#'): continue
            parts = line.strip().split('\t')
            if len(parts) == 5:
                rsid, chrom, pos, a1, a2 = parts
                if rsid in MACRO_SNPS:
                    found_snps[rsid] = a1 + a2
                    
    results = {
        "Track_A_Clinical": [],
        "Track_B_Optimization": [],
        "Track_C_Behavior": [],
        "Track_D_Traits": []
    }
    
    for rsid, info in MACRO_SNPS.items():
        trait, desc = info
        gt = found_snps.get(rsid, "NOT_FOUND")
        entry = {"rsid": rsid, "trait": trait, "genotype": gt, "context": desc}
        
        if "Methylation" in trait or "APOE" in trait or "Hemochromatosis" in trait or "Liver" in trait or "Diabetes" in trait or "Inflammation" in trait or "Heart" in trait or "Omega" in trait:
            results["Track_A_Clinical"].append(entry)
        elif "Lactose" in trait or "Obesity" in trait or "Insulin" in trait or "Caffeine" in trait or "Muscle" in trait or "Exercise" in trait or "Vitamin" in trait or "Blood" in trait:
            results["Track_B_Optimization"].append(entry)
        elif "Warrior" in trait or "Empathy" in trait or "Dopamine" in trait or "Serotonin" in trait or "Novelty" in trait or "Plasticity" in trait or "Circadian" in trait:
            results["Track_C_Behavior"].append(entry)
        else:
            results["Track_D_Traits"].append(entry)
            
    with open("ultrathink_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("Ultrathink extraction complete. Results saved to ultrathink_results.json")

if __name__ == "__main__":
    analyze_snps(sys.argv[1])
