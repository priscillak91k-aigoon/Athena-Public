import sys
from collections import defaultdict

def parse_ancestry_dna_pure(filepath):
    print(f"Parsing {filepath}...")
    
    total_snps = 0
    chromosomes = set()
    genotypes = defaultdict(int)
    no_calls = 0
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Header row
                if line.startswith('rsid'):
                    continue
                
                parts = line.split('\t')
                if len(parts) != 5:
                    continue
                
                rsid, chrom, pos, a1, a2 = parts
                
                total_snps += 1
                chromosomes.add(chrom)
                
                gt = a1 + a2
                genotypes[gt] += 1
                
                if a1 == '0' or a2 == '0':
                    no_calls += 1
                    
        print(f"Successfully loaded {total_snps} SNPs.")
        
        print("\n--- Basic Stats ---")
        print(f"Chromosomes present: {sorted(list(chromosomes))}")
        
        print("\n--- Top 10 Genotypes by Frequency ---")
        sorted_gts = sorted(genotypes.items(), key=lambda k: k[1], reverse=True)[:10]
        for gt, count in sorted_gts:
            print(f"{gt}: {count} ({count/total_snps*100:.2f}%)")
            
        print(f"\n--- No-Calls (Missing Data) ---")
        print(f"Total no-call SNPs: {no_calls} ({no_calls/total_snps*100:.2f}%)")
        
    except Exception as e:
        print(f"Error parsing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_ancestry_dna_pure(sys.argv[1])
    else:
        print("Please provide the file path.")
