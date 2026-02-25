import sys

file_path = r'C:\Users\prisc\OneDrive\Desktop\My Health\AncestryDNA.txt'

# Dictionary of "fun/curiosity" SNPs
# Format: rsid: (gene_name, trait_description, genotype_variations)
FUN_SNPS = {
    # 1. Physical Traits & Senses
    'rs1129038': ('HTR2A', 'Photic Sneeze Reflex (Sneezing in bright sunlight)', {'T/T': 'Likely to sneeze', 'C/C': 'Unlikely to sneeze', 'C/T': 'Moderate chance'}),
    'rs1726866': ('OR6A2', 'Cilantro Aversion (Soapy taste)', {'A/A': 'Cilantro tastes like soap', 'A/G': 'May taste a bit soapy', 'G/G': 'Cilantro tastes normal'}),
    'rs2890908': ('TAS2R38', 'Asparagus Anosmia (Can you smell asparagus pee?)', {'A/A': 'Cannot smell it', 'A/G': 'Might smell it slightly', 'G/G': 'Can definitely smell it'}),
    'rs1800407': ('OCA2', 'Eye Color Determinant', {'C/C': 'Likely lighter eyes (Blue/Green)', 'T/T': 'Likely darker eyes (Brown)', 'C/T': 'Mixed probability'}),
    'rs429358': ('APOE', 'Earwax Type', {'C/C': 'Wet earwax', 'T/T': 'Dry earwax (common in East Asian populations)', 'C/T': 'Wet earwax'}), # APOE also correlates to earwax!
    
    # 2. Quirks & Behaviors
    'rs1042713': ('ADRB2', 'The "Sprinter" vs "Endurance" Muscle Type', {'G/G': 'Power/Sprint dominant', 'A/A': 'Endurance dominant', 'A/G': 'Mixed muscle fiber type'}),
    'rs17822931': ('ABCC11', 'Body Odor (Underarm)', {'C/C': 'Produces standard body odor', 'T/T': 'Lacks the chemical that causes body odor (No deodorant needed!)', 'C/T': 'Produces standard body odor'}),
    
    # 3. Neanderthal & Ancestral DNA (High frequency Neanderthal variants)
    'rs3917862': ('BNC2', 'Neanderthal Variant: Freckling & Skin Pigment', {'A/A': 'Zero variants', 'C/C': 'Double Neanderthal variant', 'A/C': 'One Neanderthal variant'}),
    'rs1229984': ('ADH1B', 'Alcohol Flush Reaction', {'T/T': 'Severe flushing (Asian glow)', 'C/C': 'Normal alcohol processing', 'C/T': 'Moderate flushing'}),
    
    # 4. Sleep & Diet Quirks
    'rs1801260': ('CLOCK', 'Morning Person vs Night Owl', {'A/A': 'Extreme Morning Lark', 'G/G': 'Extreme Night Owl', 'A/G': 'Neutral/Adaptable'}),
    'rs4988235': ('MCM6', 'Lactose Persistence', {'A/A': 'Can drink milk forever', 'A/G': 'Can drink milk', 'G/G': 'Lactose Intolerant as an adult'})
}

found_traits = []

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        print(f"Scanning {file_path} for curiosities...")
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            
            parts = line.strip().split()
            if len(parts) >= 4:
                rsid = parts[0]
                if rsid in FUN_SNPS:
                    allele1 = parts[3]
                    allele2 = parts[4] if len(parts) > 4 else parts[3] # Sometimes reported as one letter if identical
                    genotype = f"{allele1}/{allele2}"
                    
                    # Account for strand flips (AncestryDNA sometimes reports the opposite strand)
                    # For a simple curiosity script, we'll try direct match first.
                    trait_info = FUN_SNPS[rsid]
                    result_text = trait_info[2].get(genotype, f"Genotype {genotype} (Varied expression)")
                    
                    found_traits.append({
                        'trait': trait_info[1],
                        'gene': trait_info[0],
                        'rsid': rsid,
                        'genotype': genotype,
                        'result': result_text
                    })

    print("\n\n--- 🧬 YOUR DNA CURIOSITY REPORT 🧬 ---")
    print("These are raw, non-actionable biological quirks hidden in your DNA:\n")
    
    if not found_traits:
        print("No curiosity markers found in this specific raw file version.")
    
    for item in found_traits:
        print(f"🔹 {item['trait']} (Gene: {item['gene']})")
        print(f"   Your Code: {item['genotype']} --> {item['result']}\n")

except FileNotFoundError:
    print(f"Error: Could not find file at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
