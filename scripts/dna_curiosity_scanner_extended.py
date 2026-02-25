import sys
import os
import json

file_path = r'C:\Users\prisc\OneDrive\Desktop\My Health\AncestryDNA.txt'
output_file = r'C:\Users\prisc\Documents\Athena-Public\.context\memories\health\DNA_Exhaustive_Curiosities.md'

# Dictionary of "fun/curiosity" SNPs
# Format: rsid: (gene_name, trait_description, genotype_variations, category)
FUN_SNPS = {
    # Neanderthal & Ancestral DNA
    'rs3917862': ('BNC2', 'Neanderthal Variant: Skin Pigment & Freckling', {'A/A': 'Zero variants', 'C/C': 'Double Neanderthal variant', 'A/C': 'One Neanderthal variant'}, 'Neanderthal Origins'),
    'rs1048868': ('LEPR', 'Neanderthal Variant: Leptin Receptor', {'C/C': 'Non-Neanderthal', 'G/G': 'Neanderthal variant (Cold adaptation)', 'C/G': 'One Neanderthal variant'}, 'Neanderthal Origins'),

    # Physical Traits & Senses
    'rs1129038': ('HTR2A', 'Photic Sneeze Reflex (Sneezing in bright sunlight)', {'T/T': 'Likely to sneeze', 'C/C': 'Unlikely to sneeze', 'C/T': 'Moderate chance'}, 'Senses & Quirks'),
    'rs1726866': ('OR6A2', 'Cilantro Aversion', {'A/A': 'Cilantro tastes like soap', 'A/G': 'May taste soapy', 'G/G': 'Cilantro tastes normal'}, 'Senses & Quirks'),
    'rs2890908': ('TAS2R38', 'Asparagus Anosmia (Can you smell asparagus pee?)', {'A/A': 'Cannot smell it', 'A/G': 'Might smell it', 'G/G': 'Can definitely smell it'}, 'Senses & Quirks'),
    'rs713598': ('TAS2R38', 'Bitter Taste Perception (Brussels Sprouts/Coffee)', {'G/G': 'Super-taster (extremely bitter)', 'C/G': 'Moderate taster', 'C/C': 'Non-taster (vegetables taste fine)'}, 'Senses & Quirks'),

    # Appearance
    'rs12913832': ('HERC2', 'Eye Color Determinant', {'A/A': 'Likely Brown eyes', 'G/G': 'Likely Blue eyes', 'A/G': 'Mixed/Green probability'}, 'Appearance'),
    'rs1805007': ('MC1R', 'Red Hair Variant 1', {'C/C': 'No red hair variant', 'T/T': 'Red hair phenotype', 'C/T': 'Carrier'}, 'Appearance'),
    'rs1805008': ('MC1R', 'Red Hair Variant 2', {'C/C': 'No red hair variant', 'T/T': 'Red hair phenotype', 'C/T': 'Carrier'}, 'Appearance'),
    'rs3827760': ('EDAR', 'Thick/Straight Hair', {'A/A': 'Typical hair thickness', 'G/G': 'Extremely thick, straight hair (Classic East Asian variant)', 'A/G': 'Intermediate thickness'}, 'Appearance'),
    'rs17822931': ('ABCC11', 'Body Odor & Earwax', {'C/C': 'Produces standard body odor / Wet earwax', 'T/T': 'No body odor / Dry earwax', 'C/T': 'Standard body odor / Wet earwax'}, 'Appearance'),

    # Muscle & Fitness
    'rs1815739': ('ACTN3', 'The "Speed/Power" Gene', {'C/C': 'Sprint/Power athlete variant (Produces Alpha-actinin-3)', 'T/T': 'Endurance variant (Deficient in Alpha-actinin-3)', 'C/T': 'Mixed muscle fiber type'}, 'Muscle & Fitness'),
    'rs1042713': ('ADRB2', 'Beta-2 Adrenergic Receptor', {'G/G': 'Power/Sprint dominant', 'A/A': 'Endurance dominant', 'A/G': 'Mixed muscle fiber type'}, 'Muscle & Fitness'),

    # Personality, Empathy, & Stress
    'rs4680': ('COMT', 'The Warrior vs Worrier', {'G/G': 'Warrior (Fast dopamine clearance, highly resilient)', 'A/A': 'Worrier (Slow dopamine clearance, higher anxiety but better memory)', 'A/G': 'Intermediate'}, 'Neuro & Behavior'),
    'rs53576': ('OXTR', 'Empathy & Oxytocin Receptor', {'G/G': 'Highly empathetic, seeks social support', 'A/A': 'Independent, introverted, less easily stressed by others', 'A/G': 'Intermediate'}, 'Neuro & Behavior'),
    'rs1800497': ('DRD2', 'Dopamine D2 Receptor (Risk/Reward)', {'A/A': 'Fewer dopamine receptors (Reward seeking / addictive personality risks)', 'G/G': 'Normal dopamine receptors', 'A/G': 'Intermediate'}, 'Neuro & Behavior'),

    # Diet & Sleep
    'rs1801260': ('CLOCK', 'Circadian Rhythm', {'A/A': 'Extreme Morning Lark', 'G/G': 'Extreme Night Owl', 'A/G': 'Nuetral/Adaptable'}, 'Diet & Sleep'),
    'rs4988235': ('MCM6', 'Lactose Tolerance', {'A/A': 'Can drink milk forever', 'A/G': 'Can drink milk', 'G/G': 'Lactose Intolerant'}, 'Diet & Sleep'),
    'rs1229984': ('ADH1B', 'Alcohol Flush', {'T/T': 'Severe flushing', 'C/C': 'Normal alcohol processing', 'C/T': 'Moderate flushing'}, 'Diet & Sleep'),
    'rs35715456': ('SLC2A2', 'Sweet Tooth Indicator', {'T/T': 'Very strong preference for sweets', 'C/C': 'Normal sugar preference', 'C/T': 'Moderate sweet tooth'}, 'Diet & Sleep'),
    
    # Random & Aging
    'rs2802292': ('FOXO3', 'Longevity Gene', {'G/G': 'Double longevity variant (Statistically lives longer)', 'T/T': 'Standard lifespan', 'G/T': 'Single longevity variant'}, 'Metabolism & Longevity'),
    'rs1799971': ('OPRM1', 'Pain Sensitivity', {'G/G': 'High pain tolerance (Requires more anesthesia)', 'A/A': 'Standard pain tolerance', 'A/G': 'Intermediate'}, 'Senses & Quirks')
}

categories = {
    'Neanderthal Origins': [],
    'Appearance': [],
    'Senses & Quirks': [],
    'Muscle & Fitness': [],
    'Neuro & Behavior': [],
    'Diet & Sleep': [],
    'Metabolism & Longevity': []
}

def reverse_complement(genotype):
    comp = {'A':'T', 'T':'A', 'C':'G', 'G':'C', 'I':'I', 'D':'D'}
    if '/' in genotype:
        a, b = genotype.split('/')
        return f"{comp.get(a, a)}/{comp.get(b, b)}"
    return genotype

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        print(f"Scanning {file_path} for an exhaustive curiosity list...")
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            
            parts = line.strip().split()
            if len(parts) >= 4:
                rsid = parts[0].strip()
                if rsid in FUN_SNPS:
                    allele1 = parts[3]
                    allele2 = parts[4] if len(parts) > 4 else parts[3]
                    # Ensure alphabetical sorting for dictionary matching (e.g., A/G instead of G/A unless homozygous)
                    alleles = sorted([allele1, allele2])
                    genotype = f"{alleles[0]}/{alleles[1]}"
                    
                    trait_info = FUN_SNPS[rsid]
                    variants_dict = trait_info[2]
                    category = trait_info[3]
                    
                    # Try direct match
                    result_text = variants_dict.get(genotype)
                    
                    # Try reverse complement strand 
                    if not result_text:
                        rev_genotype = reverse_complement(genotype)
                        rev_genotype_sorted = f"{sorted([rev_genotype[0], rev_genotype[2]])[0]}/{sorted([rev_genotype[0], rev_genotype[2]])[1]}"
                        result_text = variants_dict.get(rev_genotype_sorted)
                    
                    if not result_text:
                        result_text = f"Genotype {genotype} (Varied expression / Unmapped Strand)"

                    categories[category].append({
                        'trait': trait_info[1],
                        'gene': trait_info[0],
                        'rsid': rsid,
                        'genotype': genotype,
                        'result': result_text
                    })

    # Generate Markdown Output
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# Exhaustive DNA Curiosity & Quirks Report\n\n")
        out.write("> **Source Data**: `AncestryDNA.txt`\n")
        out.write("> **Note**: These are non-clinical traits outlining evolutionary biological quirks, physical traits, and sensory variants.\n\n")
        
        for category, items in categories.items():
            if not items: continue
            out.write(f"## {category}\n\n")
            for item in items:
                out.write(f"### {item['trait']}\n")
                out.write(f"- **Gene / Marker**: `{item['gene']}` | `{item['rsid']}`\n")
                out.write(f"- **Your Genotype**: `{item['genotype']}`\n")
                out.write(f"- **Result**: **{item['result']}**\n\n")

    print(f"Complete! Extracted traits saved to:\n{output_file}")

except FileNotFoundError:
    print(f"Error: Could not find file at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
