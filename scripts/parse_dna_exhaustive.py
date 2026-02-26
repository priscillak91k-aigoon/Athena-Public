import sys
import json

# ==============================================================================
# ULTRATHINK MASSIVE SNP DICTIONARY (EXHAUSTIVE MODE)
# ==============================================================================
EXHAUSTIVE_SNPS = {

    # ================= TRACK A: CLINICAL, CARDIO, & LONGEVITY =================
    # Methylation & B-Vitamins
    'rs1801133': ('MTHFR (Methylation C677T)', 'C = Normal. T = Reduced enzyme activity. Governs folate metabolism.'),
    'rs1801131': ('MTHFR (Methylation A1298C)', 'A = Normal. C = Reduced enzyme activity. Governs BH4/neurotransmitters.'),
    'rs1979277': ('SHMT1 (Folate Pathway)', 'G = Normal. A = Needs more folate, impacts DNA synthesis.'),
    'rs1801394': ('MTRR (B12 Recycling)', 'A = Normal. G = Poor B12 recycling, higher homocysteine.'),
    'rs4654748': ('PEMT (Choline / Liver)', 'C = Normal. T = High need for dietary choline (eggs) for liver health.'),
    
    # Alzheimer's, Brain Aging, & Cardio
    'rs7412': ('APOE (Cardio/Alzheimers)', 'Checks APOE e2 allele.'),
    'rs429358': ('APOE (Alzheimers High Risk)', 'C = Risk allele (e4).'),
    'rs3818361': ('CR1 (Alzheimers Risk)', 'T = Normal. C = Increased risk of late-onset Alzheimers.'),
    'rs662': ('PON1 (Pesticide Detox / Heart)', 'A = Low enzyme activity (high risk). G = High activity (protective).'),
    'rs10455872': ('LPA (Lipoprotein(a))', 'A = Normal. G = Elevated Lp(a), higher heart attack risk.'),
    'rs10757274': ('9p21 (Heart Attack Risk)', 'A = Normal. G = Higher risk of coronary artery disease.'),

    # Diabetes & Blood Sugar
    'rs12255372': ('TCF7L2 (Type 2 Diabetes)', 'G = Normal. T = Reduced insulin secretion, higher T2D risk.'),
    'rs7903146': ('TCF7L2 (Type 2 Diabetes)', 'C = Normal. T = Major T2D risk factor.'),
    'rs1801282': ('PPARG (Insulin Sensitivity)', 'C = Normal. G = Better insulin sensitivity (protective).'),

    # Liver & Iron
    'rs738409': ('PNPLA3 (Fatty Liver/NAFLD)', 'C = Normal. G = High risk of liver fat accumulation.'),
    'rs1799945': ('HFE (Hemochromatosis H63D)', 'C = Normal. G = Risk of iron overload.'),
    'rs1800562': ('HFE (Hemochromatosis C282Y)', 'G = Normal. A = High risk of severe iron overload.'),

    # Detox, Inflammation & Immunity
    'rs1800629': ('TNF-Alpha (Inflammation)', 'G = Normal. A = High baseline inflammation / autoimmune risk.'),
    'rs1800795': ('IL-6 (Inflammation)', 'C = Normal. G = Higher inflammatory response.'),
    'rs4686484': ('GSTP1 (Toxin Detox)', 'A = Normal. G = Poor detox of environmental chemicals.'),
    'rs1695': ('GSTP1 (Toxin Detox)', 'A = Normal. G = Reduced glutathione conjugation.'),


    # ================= TRACK B: DIET, METABOLISM, & FITNESS =================
    # Diet & Digestion
    'rs4988235': ('MCM6 (Lactose Tolerance)', 'A/G = Tolerant. G/G = Intolerant.'),
    'rs1421085': ('FTO (Obesity Risk)', 'T = Normal. C = High obesity risk.'),
    'rs9939609': ('FTO (Satiety / Fat Storage)', 'T = Normal. A = Struggles with portion control / obesity.'),
    'rs174537': ('FADS1 (Omega-3 Conversion)', 'G = Normal. T = Cannot convert ALA (chia/flax) to EPA/DHA well.'),
    'rs762551': ('CYP1A2 (Caffeine Metabolism)', 'A/A = Fast. A/C or C/C = Slow metabolizer (caffeine raises heart attack risk + hurts sleep).'),

    # Vitamins
    'rs1544410': ('VDR (Vitamin D Receptor)', 'A = Needs higher Vitamin D levels. G = Normal.'),
    'rs1801131': ('VDR (Vitamin D Receptor)', 'A = Normal. C = Poor Vitamin D absorption.'),
    'rs2406321': ('CYP2R1 (Vitamin D Synthesis)', 'A = Normal. G = Lower natural Vitamin D levels.'),
    'rs2228145': ('IL6R (Vitamin C Response)', 'A/C = Needs more Vitamin C to lower inflammation. A/A = Normal.'),

    # Fitness & Musculoskeletal
    'rs1815739': ('ACTN3 (Muscle Fiber)', 'C/C = Fast reflex (Sprint). T/T = Slow reflex (Endurance). C/T = Mixed.'),
    'rs1042713': ('ADRB2 (Exercise Response)', 'A = Endurance responder. G = Strength/Resistance responder.'),
    'rs4341': ('ACE (Blood Pressure/Fitness)', 'G = Power bias / higher BP. C = Endurance bias / lower BP.'),
    'rs12595857': ('COL1A1 (Tendon/Ligament Injury)', 'G = Normal. A = Higher risk of ACL tears and tendon injuries.'),
    'rs12722': ('COL5A1 (Achilles Risk)', 'C = Normal. T = Higher risk of Achilles tendinopathy.'),


    # ================= TRACK C: BEHAVIOR, PSYCHOLOGY, & SLEEP =================
    # Neurotransmitters & Personality
    'rs4680': ('COMT (Warrior vs Worrier)', 'G/G = Warrior (low dopamine, handles stress). A/A = Worrier (high dopamine, high memory, bad under stress).'),
    'rs1611115': ('DBH (Dopamine Beta-Hydroxylase)', 'C = Normal alertness. T = Slower dopamine conversion (prone to brain fog).'),
    'rs1800497': ('DRD2 (Dopamine Receptor)', 'G = Normal. A = Fewer receptors (higher risk of addiction, binge eating/drinking).'),
    'rs1800955': ('DRD4 (Novelty Seeking / ADHD)', 'C = Normal. T = High novelty seeking, easily bored.'),
    
    # Stress, Mood & Empathy
    'rs53576': ('OXTR (Empathy/Oxytocin)', 'G/G = Highly empathetic. A/A = Introverted, less sensitive to emotional stress.'),
    'rs25531': ('SLC6A4 (Serotonin / OCD)', 'Influences serotonin reuptake. Short allele = higher stress reactivity.'),
    'rs6265': ('BDNF (Plasticity / Learning)', 'G = Normal. A = Lower BDNF (slower learning under stress, higher depression risk).'),
    'rs1360780': ('FKBP5 (PTSD / Cortisol Recovery)', 'C = Normal. T = Slower cortisol recovery after trauma (PTSD risk).'),
    'rs1800532': ('TPH1 (Anger / Serotonin Synthesis)', 'A = Normal. C = Impulsive aggression, short temper.'),

    # Sleep & Circadian
    'rs1801260': ('CLOCK (Morning/Evening Type)', 'T/T = Extreme morning lark. C/C = Night owl (sleep phase delay).'),
    'rs518147': ('AANAT (Melatonin Production)', 'G = Normal. C = Lower melatonin (insomnia risk).'),
    'rs3758391': ('SIRT1 (Circadian Aging)', 'T = Normal. C = Disrupted circadian clock aging.'),


    # ================= TRACK D: TRAITS, PHARMA, & APPEARANCE =================
    # Appearance
    'rs12913832': ('HERC2 (Eye Color)', 'A = Brown/Hazel. G = Blue.'),
    'rs1805007': ('MC1R (Red Hair)', 'C = Normal. T = Red hair, high skin cancer risk.'),
    'rs6152': ('AR (Male Pattern Baldness)', 'A = Low risk. G = High risk.'),

    # Senses & Perception
    'rs713598': ('TAS2R38 (Bitter Taste / Cilantro)', 'G = Tastes PTC (brussels sprouts are bitter). C = Cannot taste PTC.'),
    'rs1726866': ('OR6A2 (Cilantro Soap Taste)', 'T = Normal. C = Cilantro tastes like soap.'),

    # Pharmacy & Drugs
    'rs1799971': ('OPRM1 (Pain & Opioids)', 'A = Normal. G = Much higher pain sensitivity, requires more morphine.'),
    'rs1045642': ('ABCB1 (Drug Blood-Brain Barrier)', 'C = Normal. T = Drugs cross into brain easier (higher side effects).'),
    'rs2242480': ('CYP3A4 (Testosterone/Drug Metab)', 'C = Normal. T = Extremely fast metabolism of statins, testosterone.')
}

def analyze_snps(filepath):
    found_snps = {}
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#'): continue
            parts = line.strip().split('\t')
            if len(parts) == 5:
                rsid, chrom, pos, a1, a2 = parts
                if rsid in EXHAUSTIVE_SNPS:
                    found_snps[rsid] = a1 + a2
                    
    results = {
        "Track_A_Clinical": [],
        "Track_B_Optimization": [],
        "Track_C_Behavior": [],
        "Track_D_Traits": []
    }
    
    for rsid, info in EXHAUSTIVE_SNPS.items():
        trait, desc = info
        gt = found_snps.get(rsid, "NOT_FOUND")
        
        entry = {"rsid": rsid, "trait": trait, "genotype": gt, "context": desc}
        
        # Categorization logic
        if rsid in ['rs1801133', 'rs1801131', 'rs1979277', 'rs1801394', 'rs4654748', 'rs7412', 'rs429358', 'rs3818361', 'rs662', 'rs10455872', 'rs10757274', 'rs12255372', 'rs7903146', 'rs1801282', 'rs738409', 'rs1799945', 'rs1800562', 'rs1800629', 'rs1800795', 'rs4686484', 'rs1695']:
            results["Track_A_Clinical"].append(entry)
        elif rsid in ['rs4988235', 'rs1421085', 'rs9939609', 'rs174537', 'rs762551', 'rs1544410', 'rs2406321', 'rs2228145', 'rs1815739', 'rs1042713', 'rs4341', 'rs12595857', 'rs12722']:
            results["Track_B_Optimization"].append(entry)
        elif rsid in ['rs4680', 'rs1611115', 'rs1800497', 'rs1800955', 'rs53576', 'rs25531', 'rs6265', 'rs1360780', 'rs1800532', 'rs1801260', 'rs518147', 'rs3758391']:
            results["Track_C_Behavior"].append(entry)
        elif rsid in ['rs12913832', 'rs1805007', 'rs6152', 'rs713598', 'rs1726866', 'rs1799971', 'rs1045642', 'rs2242480']:
            results["Track_D_Traits"].append(entry)
            
    with open("ultrathink_exhaustive_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("Exhaustive extraction complete. Results saved to ultrathink_exhaustive_results.json")

if __name__ == "__main__":
    analyze_snps(sys.argv[1])
