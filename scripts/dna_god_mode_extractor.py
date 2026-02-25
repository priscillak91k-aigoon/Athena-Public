import sys
import os

file_path = r'C:\Users\prisc\OneDrive\Desktop\My Health\AncestryDNA.txt'
output_file = r'C:\Users\prisc\Documents\Athena-Public\.context\memories\health\DNA_God_Mode_Report.md'

# Dictionary structure:
# 'rsid': ('Gene', 'Trait/Disease', {'G/G': 'Description', 'A/A': 'Description'}, 'Category', 'Layman Context')
MASTER_SNPS = {
    # ========================================================
    # 🫀 CARDIOLOGY & LIPIDOLOGY
    # ========================================================
    'rs7412': ('APOE', 'Alzheimers & Cardiovascular Plaque Risk (e2/e3/e4)', {'C/C': 'Normal Risk (protective allele present)', 'T/T': 'Elevated Plaque Risk', 'C/T': 'Carrier'}, 'Cardiology & Lipidology', 'The APOE gene determines how your body packages and clears cholesterol. Certain variants (like e4) make it harder for the body to clear plaque from arteries and the brain, increasing the long-term risk for heart disease and Alzheimer\'s.'),
    'rs429358': ('APOE', 'Alzheimers Risk Component (e4 marker)', {'T/T': 'No e4 allele (Standard risk)', 'C/C': 'Double e4 allele (High Alzheimer\'s/Cardio risk)', 'C/T': 'Single e4 allele (Elevated risk)'}, 'Cardiology & Lipidology', 'This is the specific marker used to detect the notorious APOE4 variant. Having no e4 allele is the standard baseline, while having one or two can significantly raise the likelihood of plaque buildup over a lifetime.'),
    'rs10455872': ('LPA', 'Lipoprotein(a) Clotting Risk', {'A/A': 'Normal limits', 'G/G': 'Highly elevated Lp(a) / Massive clot & heart attack risk', 'A/G': 'Elevated Lp(a)'}, 'Cardiology & Lipidology', 'Lipoprotein(a) is a dangerous, sticky type of cholesterol that acts like a blood patch for damaged arteries. High genetic levels drastically increase the risk of blood clots, strokes, and early heart attacks, regardless of your diet.'),
    'rs10757274': ('9p21 (CDKN2A/B)', 'Coronary Artery Disease Predisposition', {'A/A': 'Low risk', 'G/G': 'High risk (2x chance of heart attack)', 'A/G': 'Moderate risk'}, 'Cardiology & Lipidology', 'Known as the "Heart Attack Gene," this region controls cell cycles in artery walls. The risk variant makes arteries weaker and more prone to forming dangerous blockages (atherosclerosis) independent of cholesterol levels.'),
    'rs1799983': ('NOS3', 'Endothelial Function & Blood Pressure', {'G/G': 'Standard nitric oxide production', 'T/T': 'Reduced NO / Stiff vessels (High BP risk)', 'G/T': 'Intermediate NO'}, 'Cardiology & Lipidology', 'This gene determines how well your body produces Nitric Oxide, a gas that relaxes and widens blood vessels. Reduced NO means stiffer arteries, which often leads to age-related high blood pressure and poor circulation.'),
    'rs1801133': ('MTHFR', 'Homocysteine & Vascular Damage', {'C/C': 'Normal B-vitamin metabolism (Low homocysteine)', 'T/T': 'Severe reduction in methylfolate (High homocysteine/clot risk)', 'C/T': 'Moderate reduction'}, 'Cardiology & Lipidology', 'MTHFR controls your body\'s ability to convert B-vitamins from food into their active, usable forms. A bad variant causes a toxic amino acid called homocysteine to build up and scratch the inside of blood vessels, promoting clots.'),

    # ========================================================
    # 🧠 NEUROLOGY, PSYCHIATRY & BEHAVIOR
    # ========================================================
    'rs4680': ('COMT', 'Dopamine Clearance (Warrior vs Worrier)', {'G/G': 'Warrior (Fast clearance, cool under pressure, bored easily)', 'A/A': 'Worrier (Slow clearance, high anxiety, high memory capacity)', 'A/G': 'Balanced'}, 'Neurology & Behavior', 'The COMT enzyme clears dopamine from your brain\'s prefrontal cortex. "Warriors" clear it too fast, leaving them bored in everyday life but hyper-focused during crises. "Worriers" clear it slowly, leading to higher anxiety but superior memory capacity.'),
    'rs6265': ('BDNF', 'Brain Plasticity & Memory', {'C/C': 'Standard brain plasticity', 'T/T': 'Reduced brain plasticity (Struggles to learn under stress)', 'C/T': 'Moderate plasticity reduction'}, 'Neurology & Behavior', 'BDNF is like "Miracle-Gro" for the brain—it helps grow new neural connections. Reduced plasticity means it takes more effort to learn complex new physical or mental skills, especially when you are sleep-deprived or stressed.'),
    'rs53576': ('OXTR', 'Empathy & Oxytocin Receptor', {'G/G': 'Highly empathetic, seeks social support', 'A/A': 'Independent, introverted, less easily stressed by others', 'A/G': 'Balanced'}, 'Neurology & Behavior', 'This dictates how your brain binds to oxytocin (the "love/bonding" hormone). Independent variants mean you do not easily absorb the emotional stress of people around you and require less social validation to feel content.'),
    'rs1800497': ('ANKK1 / DRD2', 'Dopamine D2 Receptor (Addiction / Reward)', {'C/C': 'Normal dopamine receptors', 'T/T': 'Fewer dopamine receptors (Higher risk for addiction, obesity, reward-seeking)', 'C/T': 'Intermediate risk'}, 'Neurology & Behavior', 'This controls how many D2 receptors your brain has to "catch" dopamine. Fewer receptors mean you experience less satisfaction from everyday joys, predisposing you to seek out extreme thrills, junk food, or addictions to feel "normal."'),
    'rs909525': ('MAOA', 'The "Warrior Gene" (Monoamine Oxidase A)', {'T/T': 'Low MAOA activity (More impulsive, higher aggression, higher serotonin/dopamine baseline)', 'C/C': 'High MAOA activity (Placid, lower baseline neurotransmitters)', 'C/T': 'Intermediate'}, 'Neurology & Behavior', 'MAOA cleans up serotonin and adrenaline. Low activity (the famous "Warrior Gene") leaves a higher baseline of these neurotransmitters, which can lead to impulsivity and aggressive responses to provocation, but also immense drive.'),
    'rs1611115': ('DBH', 'Dopamine to Norepinephrine Conversion', {'C/C': 'Normal alertness conversion', 'T/T': 'Lower conversion (Prone to fatigue/ADHD)', 'C/T': 'Moderate'}, 'Neurology & Behavior', 'This gene turns dopamine into norepinephrine (which drives alertness and focus). A poor conversion rate means your brain might struggle to "wake up" and stay sharp during boring tasks, a common trait in ADHD.'),

    # ========================================================
    # 💊 PHARMACOGENOMICS (Toxin & Drug Clearance)
    # ========================================================
    'rs762551': ('CYP1A2', 'Caffeine Metabolism', {'A/A': 'Fast metabolizer (Coffee has little effect on sleep after a few hours)', 'C/C': 'Ultra-slow metabolizer (Coffee causes extreme anxiety/insomnia)', 'A/C': 'Slow metabolizer'}, 'Pharmacogenomics', 'Your liver uses this enzyme to clear caffeine from the bloodstream. Slow metabolizers hold onto caffeine for over 10 hours, meaning a 2 PM coffee will destroy deep sleep architecture that night.'),
    'rs1065852': ('CYP2D6', 'Codeine & SSRI Metabolism', {'G/G': 'Extensive (Normal) Metabolizer', 'A/A': 'Poor metabolizer (Standard drug doses will be toxic/build up)', 'A/G': 'Intermediate'}, 'Pharmacogenomics', 'CYP2D6 processes 25% of all prescription drugs, including antidepressants and painkillers. If you are a poor metabolizer, a "normal" dose prescribed by a doctor will build up to toxic levels in your body.'),
    'rs1799853': ('CYP2C9', 'Warfarin & NSAID (Ibuprofen) Clearance', {'C/C': 'Normal clearance', 'T/T': 'Poor clearance (High risk of bleeding on blood thinners/NSAIDs)', 'C/T': 'Slow clearance'}, 'Pharmacogenomics', 'This enzyme breaks down NSAID painkillers (like ibuprofen) and blood thinners. Poor clearance means taking these drugs can lead to dangerous stomach bleeding, as the drug stays active in your system for far too long.'),
    'rs2242480': ('CYP3A4', 'Statin & Testosterone Clearance', {'T/T': 'Normal clearance', 'C/C': 'Ultra-rapid metabolizer (Burns through drugs too quickly, meaning standard doses are ineffective)', 'C/T': 'Rapid metabolizer'}, 'Pharmacogenomics', 'CYP3A4 handles over 50% of all medicines, including statins and testosterone. Ultra-rapid metabolism means your liver destroys the drug so fast it never gets a chance to work properly, requiring much higher prescribed doses.'),
    'rs1695': ('GSTP1', 'Glutathione Detoxification (Plastics/Heavy Metals)', {'A/A': 'Normal detox ability', 'G/G': 'Poor detox (Prone to chemical sensitivity, must supplement NAC)', 'A/G': 'Reduced detox'}, 'Pharmacogenomics', 'Glutathione is the body\'s master antioxidant, responsible for sweeping out toxins, plastics, and smoke. A poor GSTP1 variant means your liver struggles to attach glutathione to these toxins, allowing them to accumulate and damage DNA.'),

    # ========================================================
    # 🏃 ATHLETIC PERFORMANCE & METABOLISM
    # ========================================================
    'rs1815739': ('ACTN3', 'The Alpha-Actinin-3 "Sprint" Gene', {'C/C': 'Sprint/Power athlete (Produces protein for explosive force)', 'T/T': 'Endurance athlete (Completely lacks sprint protein)', 'C/T': 'Mixed muscle fibers'}, 'Athletics & Fitness', 'This gene determines if you produce a specific protein found exclusively in fast-twitch (sprint) muscle fibers. Lacking the protein means you are naturally built for marathon-style endurance rather than explosive weightlifting.'),
    'rs1042713': ('ADRB2', 'Beta-2 Adrenergic (Fat burning & Power)', {'G/G': 'Power/Sprint dominant (Burns fat well during heavy resistance training)', 'A/A': 'Endurance dominant', 'A/G': 'Mixed'}, 'Athletics & Fitness', 'These receptors control how your body responds to adrenaline during workouts. The power variant means adrenaline triggers massive fat burning and power output during heavy, low-rep resistance training rather than steady cardio.'),
    'rs4341': ('ACE', 'Angiotensin Converting Enzyme (Blood Flow)', {'G/G': 'Power variant (Cardiac hypertrophy response to lifting)', 'C/C': 'Endurance variant (Extreme stamina)', 'C/G': 'Mixed'}, 'Athletics & Fitness', 'ACE controls blood vessel constriction. The endurance variant keeps vessels wide open, delivering massive oxygen efficiency during long runs. The power variant allows the heart to thicken and pump harder for explosive strength.'),
    'rs8192678': ('PPARGC1A', 'Mitochondrial Biogenesis', {'G/G': 'Excellent mitochondrial response to exercise', 'A/A': 'Poor mitochondrial generation (Tires easily)', 'A/G': 'Moderate response'}, 'Athletics & Fitness', 'Mitochondria are the powerplants of your cells. This gene controls how efficiently your body builds new mitochondria in response to aerobic exercise. Poor biogenesis means cardio improvements are slow and hard-earned.'),
    'rs12722': ('COL5A1', 'Collagen & Achilles Injury Risk', {'C/C': 'Strong tendons', 'T/T': 'High risk of Achilles tendinopathy (Requires extremely slow eccentric training)', 'C/T': 'Elevated tendon risk'}, 'Athletics & Fitness', 'This codes the specific type of collagen used in tendons. A weak variant means your Achilles and other major tendons stretch poorly and are highly susceptible to tearing under heavy or sudden loads.'),

    # ========================================================
    # 🥗 NUTRITION, DIET, & LONGEVITY
    # ========================================================
    'rs9939609': ('FTO', 'The Master "Obesity" Gene (Satiety)', {'T/T': 'Normal satiety (Knows when to stop eating)', 'A/A': 'Broken satiety (Never feels full, exceptionally high obesity risk)', 'A/T': 'Moderate satiety issues'}, 'Nutrition & Diet', 'FTO is the strongest known genetic risk factor for obesity. It controls your brain\'s "I am full" signaling. The risk variant means you never truly feel satisfied after a meal, making portion control a constant, intense conscious effort.'),
    'rs7903146': ('TCF7L2', 'Type 2 Diabetes Risk (Pancreatic Function)', {'C/C': 'Low diabetes risk', 'T/T': 'High diabetes risk (Pancreas prone to burnout from carbs)', 'C/T': 'Elevated risk'}, 'Nutrition & Diet', 'This determines the durability of the insulin-secreting cells in your pancreas. A high risk means that chronic sugar spikes will physically exhaust and destroy your pancreas cells much earlier than the average person, accelerating diabetes.'),
    'rs4988235': ('MCM6', 'Lactose Tolerance Base', {'G/G': 'Lactose Intolerant (As adult)', 'A/A': 'Lactose Tolerant', 'A/G': 'Tolerant'}, 'Nutrition & Diet', 'Historically, humans stopped producing the lactose-digesting enzyme after weaning. A genetic mutation in European and some African herding populations keeps the enzyme active for life, allowing milk consumption without stomach distress.'),
    'rs1544410': ('VDR', 'Vitamin D Receptor', {'A/A': 'Poor Vitamin D binding (Needs much higher blood levels)', 'G/G': 'Excellent Vitamin D binding', 'A/G': 'Moderate'}, 'Nutrition & Diet', 'Your body needs Vitamin D to execute thousands of commands, but it can only do so by attaching to VDR receptors. Poor binding means even if your blood levels look "normal," your cells aren\'t absorbing it, requiring mass supplementation.'),
    'rs2802292': ('FOXO3', 'Centenarian Longevity Gene', {'G/G': 'Double longevity variant (Statistically lives ~10% longer)', 'T/T': 'Standard lifespan', 'G/T': 'Single longevity variant'}, 'Nutrition & Diet', 'FOXO3 is the "master switch" for cellular cleanup (autophagy) and DNA repair. People with the longevity variant have fiercely aggressive cellular repair systems, making them statistically far more likely to live past 100 years old.'),
    'rs3758391': ('SIRT1', 'Circadian Aging', {'T/T': 'Normal circadian function', 'C/C': 'Disrupted circadian aging (Shift work ages cells rapidly)', 'C/T': 'Intermediate'}, 'Nutrition & Diet', 'SIRT1 repairs DNA based on strict biological clock rhythms. Disrupted aging means that violating your sleep schedule (like working night shifts or jet lag) profoundly damages your cells and accelerates biological aging.'),

    # ========================================================
    # 🛡️ IMMUNOLOGY & AUTOIMMUNE
    # ========================================================
    'rs1800629': ('TNF-Alpha', 'Baseline Tissue Inflammation', {'G/G': 'Normal inflammation', 'A/A': 'Extremely high baseline inflammation (Joints, gut, brain)', 'A/G': 'High baseline inflammation'}, 'Immunology', 'TNF-Alpha is a chemical fire alarm used to attack infections. A high baseline means your alarm is always slightly ringing, causing low-grade chronic inflammation throughout your body, leading to achy joints and brain fog.'),
    'rs1800795': ('IL-6', 'Cytokine Response (Interleukin 6)', {'G/G': 'Normal cytokine response', 'C/C': 'Protective (Lower inflammatory response to stress)', 'C/G': 'Intermediate'}, 'Immunology', 'IL-6 is another inflammatory messenger. A protective variant means that when you get sick or stressed, your body doesn\'t "overreact" with a massive inflammatory storm, protecting your own tissues from friendly fire.'),
    'rs2395182': ('HLA-B27', 'Ankylosing Spondylitis & Joint Pain Risk', {'G/G': 'Standard risk', 'T/T': 'Massive risk for autoimmune joint fusion', 'G/T': 'Elevated risk'}, 'Immunology', 'This is a notorious autoimmune marker. Having it means your immune cells often mistake your own spine, pelvis, and severe joints for foreign invaders, relentlessly attacking them and eventually causing the bones to permanently fuse together.'),
    'rs3135388': ('HLA-DRB1 / HLA-DQA1', 'Celiac Disease / Gluten Autoimmunity', {'T/T': 'Low risk for Celiac', 'A/A': 'High genetic risk for Celiac (Gluten destroys gut lining)', 'A/T': 'Carrier / Moderate risk'}, 'Immunology', 'This determines if a harmless protein in wheat (gluten) triggers an autoimmune attack. If you have the high-risk genes, eating a single slice of bread commands your white blood cells to literally burn down the lining of your intestines.'),
    'rs1143627': ('IL-1B', 'Interleukin 1 Beta (Periodontal & Chronic Inflammation)', {'T/T': 'Normal', 'C/C': 'Severe chronic inflammation responder (Gums, arteries)', 'C/T': 'Moderate'}, 'Immunology', 'IL-1B regulates bone and gum inflammation. High responders often suffer from severe, untreatable gum disease and have a significantly higher risk of arterial inflammation, intimately connecting dental health with heart attacks.'),

    # ========================================================
    # 👽 CURIOSITIES, PHYSICAL TRAITS, & NEANDERTHAL
    # ========================================================
    'rs17822931': ('ABCC11', 'Body Odor & Earwax Type', {'C/C': 'Standard body odor / Wet earwax', 'T/T': 'Zero body odor (No deodorant needed) / Dry earwax', 'C/T': 'Standard body odor'}, 'Curiosities & Traits', 'This quirky gene controls a pump that pushes sweat into your armpits. If the pump is genetically broken (T/T), the bacteria in your armpit have no food to eat, resulting in literally zero body odor. It also turns your earwax dry and flaky.'),
    'rs12913832': ('HERC2', 'Eye Color Determinant', {'A/A': 'Brown eyes', 'G/G': 'Blue/Lighter eyes', 'A/G': 'Mixed/Green'}, 'Curiosities & Traits', 'HERC2 acts as a genetic switch for melanin production in the iris. If the switch is broken (G/G), the eye defaults to blue—a mutation that actually originated from a single human ancestor near the Black Sea 10,000 years ago.'),
    'rs1805007': ('MC1R', 'Red Hair & Sun Sensitivity', {'C/C': 'Tans normally', 'T/T': 'Red hair phenotype / Burns easily', 'C/T': 'Carrier'}, 'Curiosities & Traits', 'MC1R controls the type of melanin your skin makes. The red hair variant forces your body to make pheomelanin (red/yellow) instead of eumelanin (brown/black), leaving your skin virtually defenseless against UV radiation from the sun.'),
    'rs1129038': ('HTR2A', 'Photic Sneeze Reflex', {'T/T': 'Sneezes in bright sunlight', 'C/C': 'Unlikely to sneeze', 'C/T': 'Moderate chance'}, 'Curiosities & Traits', 'Known as ACHOO Syndrome, this is a literal crossed wire in the brain. The optic nerve (which senses bright light) accidentally fires the trigeminal nerve (which controls the nose), causing an involuntary sneeze when looking at the sun.'),
    'rs1726866': ('OR6A2', 'Cilantro Aversion', {'A/A': 'Cilantro tastes like soap', 'A/G': 'May taste soapy', 'G/G': 'Cilantro tastes normal'}, 'Curiosities & Traits', 'Some people possess a specific olfactory (smell) receptor that is hypersensitive to the aldehyde chemicals present in cilantro. To them, these chemicals completely overwhelm the herb taste and make the plant taste exactly like dish soap.'),
    'rs2890908': ('TAS2R38', 'Asparagus Anosmia (Urine Smell)', {'A/A': 'Cannot smell it', 'A/G': 'Might smell it', 'G/G': 'Can definitely smell it'}, 'Curiosities & Traits', 'When you eat asparagus, it breaks down into sulfurous compounds. Up to 60% of people have a specific mutation in their smell receptors that makes them fully "blind" to the scent of this sulfur in urine.'),
    'rs4849721': ('OAS1', 'Neanderthal Viral Resistance', {'A/A': 'Normal', 'G/G': 'Neanderthal Variant (Potent resistance against RNA viruses)', 'A/G': 'One Neanderthal Variant'}, 'Curiosities & Traits', 'When modern humans migrated out of Africa, they mated with Neanderthals who had already adapted to Eurasian diseases. This Neanderthal gene snippet provides a potent, ancient immune defense against severe RNA viruses like West Nile.'),
    'rs11568818': ('EPAS1', 'Denisovan Altitude Adaptation', {'G/G': 'Normal', 'A/A': 'Denisovan High Altitude adaptation', 'A/G': 'Carrier'}, 'Curiosities & Traits', 'This is an archaic "super-gene" inherited from the mysterious Denisovan hominids. It prevents blood from becoming dangerously thick at extreme high altitudes, a trait found almost exclusively in modern Tibetan populations.'),
    'rs1799990': ('PRNP', 'Prion Disease Resistance (Mad Cow)', {'G/G': 'Normal variant', 'A/A': 'Highly resistant to prion diseases', 'A/G': 'Carrier resistant'}, 'Curiosities & Traits', 'This mutation alters the shape of your brain\'s prion proteins so they cannot "fold" incorrectly. It provides extreme immunity to horrific neurological prion diseases like Mad Cow Disease and Kuru (which was historically spread through cannibalism).')
}

categories = {
    'Cardiology & Lipidology': [],
    'Neurology & Behavior': [],
    'Pharmacogenomics': [],
    'Athletics & Fitness': [],
    'Nutrition & Diet': [],
    'Immunology': [],
    'Curiosities & Traits': []
}

def reverse_complement(allele):
    comp = {'A':'T', 'T':'A', 'C':'G', 'G':'C', 'I':'I', 'D':'D'}
    return comp.get(allele, allele)

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        print("Initializing GOD MODE extraction with Layman Descriptions...")
        
        for line in f:
            if line.startswith('#') or line.strip() == '': continue
            parts = line.strip().split()
            if len(parts) >= 4:
                rsid = parts[0]
                if rsid in MASTER_SNPS:
                    allele1 = parts[3]
                    allele2 = parts[4] if len(parts) > 4 else allele1
                    
                    trait_info = MASTER_SNPS[rsid]
                    variants_dict = trait_info[2]
                    category = trait_info[3]
                    layman_expl = trait_info[4]
                    
                    combinations = [
                        f"{allele1}/{allele2}",
                        f"{allele2}/{allele1}",
                        f"{reverse_complement(allele1)}/{reverse_complement(allele2)}",
                        f"{reverse_complement(allele2)}/{reverse_complement(allele1)}"
                    ]
                    
                    result_text = None
                    for combo in combinations:
                        if combo in variants_dict:
                            result_text = variants_dict[combo]
                            break
                            
                    if not result_text:
                        result_text = f"Unmapped/Rare Allele Configuration: {allele1}/{allele2} (Needs clinical sequencing to verify)"

                    categories[category].append({
                        'trait': trait_info[1],
                        'gene': trait_info[0],
                        'rsid': rsid,
                        'genotype': f"{allele1}/{allele2}",
                        'result': result_text,
                        'explanation': layman_expl
                    })

    # Write massive report
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# 🏛️ ULTRATHINK DNA: The Master Blueprint (God Mode)\n\n")
        out.write("> **Source Data**: `AncestryDNA.txt`\n")
        out.write("> **Analysis Mode**: Exhaustive Deep-Dive Mapping with Plain English Context\n")
        out.write("> **Warning**: This is an unedited, exhaustive extraction of highly impactful human genes. Use for informational/fitness/optimization purposes only, not clinical diagnostics.\n\n")
        
        for category, items in categories.items():
            if not items: continue
            out.write(f"## {category}\n\n")
            for item in items:
                out.write(f"### {item['trait']}\n")
                out.write(f"- **Gene (rsID)**: `{item['gene']}` (`{item['rsid']}`)\n")
                out.write(f"- **Your Genetic Code**: `{item['genotype']}`\n")
                out.write(f"- **Your Result**: **{item['result']}**\n")
                out.write(f"- **What This Means**: {item['explanation']}\n\n")

    print(f"\nExtraction complete! Master Document Saved:\n{output_file}")

except Exception as e:
    print(f"Error executing extraction: {e}")
