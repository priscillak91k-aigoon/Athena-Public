import sys

file_path = r'C:\Users\prisc\OneDrive\Desktop\My Health\AncestryDNA.txt'
output_file = r'C:\Users\prisc\Documents\Athena-Public\.context\memories\health\DNA_Obscure_Report.md'

OBSCURE_SNPS = {
    # Neanderthal & Ancient DNA
    'rs11826046': ('TLR1/6/10 Cluster', 'Neanderthal Immune System Variant', {'G G': 'Non-Neanderthal variant', 'A A': 'Neanderthal variant (Hyper-reactive immune system, allergy/asthma prone)', 'A G': 'One Neanderthal variant', 'G A': 'One Neanderthal variant'}),
    'rs11568818': ('EPAS1', 'Denisovan Altitude Adaptation', {'G G': 'Normal', 'A A': 'Denisovan High Altitude adaptation', 'A G': 'Carrier', 'G A': 'Carrier'}),
    'rs3135391': ('HLA-DRB1', 'Neanderthal Autoimmunity / MS Risk', {'A A': 'Normal', 'G G': 'Neanderthal variant (Elevated MS/Autoimmune risk)', 'A G': 'One Neanderthal variant', 'G A': 'One Neanderthal variant'}),
    'rs4849721': ('OAS1', 'Neanderthal Viral Resistance', {'A A': 'Normal', 'G G': 'Neanderthal Variant (Potent resistance against certain RNA viruses like West Nile)', 'A G': 'One Neanderthal Variant', 'G A': 'One Neanderthal Variant'}),

    # Extreme Curiosities
    'rs1799990': ('PRNP', 'Prion Disease Resistance (Mad Cow / Kuru)', {'G G': 'Normal variant', 'A A': 'Highly resistant to prion diseases', 'A G': 'Carrier resistant', 'G A': 'Carrier resistant'}),
    'rs35715456': ('SLC2A2', 'The "Sweet Tooth" Gene', {'T T': 'Very strong preference for sweets', 'C C': 'Normal sugar preference', 'C T': 'Moderate sweet tooth', 'T C': 'Moderate sweet tooth'}),
    'rs2802292': ('FOXO3', 'Centenarian "Longevity" Gene', {'G G': 'Double longevity variant (Statistically lives longer)', 'T T': 'Standard lifespan', 'G T': 'Single longevity variant', 'T G': 'Single longevity variant'}),
    'rs1800955': ('DRD4', 'The "Wanderlust" & Novelty Seeking Gene', {'C C': 'Standard DRD4 receptors', 'T T': 'Very high novelty seeking (Wanderlust)', 'C T': 'Moderate novelty/wanderlust', 'T C': 'Moderate'}),
    'rs4141463': ('MACROD2', 'Mathematical & Spatial Ability', {'T T': 'Higher math/spatial ability', 'C C': 'Standard ability', 'C T': 'Intermediate', 'T C': 'Intermediate'}),
    
    # Stress, Brain, and Emotion
    'rs6903956': ('ADCYAP1R1', 'Stress & Startle Reflex', {'G G': 'Stronger startle reflex & higher PTSD/Stress response', 'A A': 'Lower startle reflex, highly resilient', 'A G': 'Moderate startle reflex', 'G A': 'Moderate'}),
    'rs4820988': ('SCN10A', 'Pain Perception & Cold Hands', {'T T': 'Higher pain threshold, normal temps', 'A A': 'Lower pain threshold, strong tendency for cold hands', 'A T': 'Intermediate', 'T A': 'Intermediate'}),
    'rs1044396': ('CHRM2', 'Performance IQ & Alcohol Dependence Risk', {'T T': 'Higher performance IQ variant', 'A A': 'Standard variant', 'A T': 'Intermediate', 'T A': 'Intermediate'}),
    
    # Weird Physio
    'rs1042522': ('TP53', 'The Guardian of the Genome (Cancer Suppression)', {'G G': 'Standard p53 function', 'C C': 'Enhanced p53 apoptosis (Aggressive cancer fighting, but ages cells faster)', 'C G': 'Mixed function', 'G C': 'Mixed function'}),
    'rs972283': ('KLF14', 'Fat Distribution Base', {'G G': 'Stores fat around hips/thighs (Gynoid)', 'A A': 'Stores fat around organs (Android, higher metabolic risk)', 'A G': 'Mixed', 'G A': 'Mixed'}),
    'rs4588': ('GC', 'Vitamin D Transport Mechanism', {'A A': 'Poor Vitamin D transport (Needs more sun/supplements)', 'C C': 'Excellent Vitamin D transport', 'A C': 'Moderate transport', 'C A': 'Moderate transport'})
}

found = []

def reverse_complement(allele):
    comp = {'A':'T', 'T':'A', 'C':'G', 'G':'C'}
    return comp.get(allele, allele)

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        print("Hunting for deeply obscure traits in AncestryDNA file...")
        for line in f:
            if line.startswith('#') or line.strip() == '': continue
            parts = line.strip().split()
            if len(parts) >= 4:
                rsid = parts[0]
                if rsid in OBSCURE_SNPS:
                    a1 = parts[3]
                    a2 = parts[4] if len(parts) > 4 else a1
                    
                    trait_info = OBSCURE_SNPS[rsid]
                    variants_dict = trait_info[2]
                    
                    combos = [
                        f"{a1} {a2}",
                        f"{a2} {a1}",
                        f"{reverse_complement(a1)} {reverse_complement(a2)}",
                        f"{reverse_complement(a2)} {reverse_complement(a1)}"
                    ]
                    
                    result_text = None
                    for combo in combos:
                        if combo in variants_dict:
                            result_text = variants_dict[combo]
                            break
                            
                    if not result_text:
                        result_text = f"Unmapped Alleles: {a1}/{a2}"

                    found.append({
                        'trait': trait_info[1],
                        'gene': trait_info[0],
                        'rsid': rsid,
                        'result': result_text
                    })

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# 👽 Obscure DNA & Neanderthal Report\n\n")
        
        for item in found:
            out.write(f"### {item['trait']}\n")
            out.write(f"- **Gene**: `{item['gene']}` (`{item['rsid']}`)\n")
            out.write(f"- **Result**: **{item['result']}**\n\n")

    print(f"Extraction complete! Saved to {output_file}")

except Exception as e:
    print(f"Error: {e}")
