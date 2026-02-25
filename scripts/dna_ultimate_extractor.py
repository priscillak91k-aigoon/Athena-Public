import sys
import os

file_path = r'C:\Users\prisc\OneDrive\Desktop\My Health\AncestryDNA.txt'
output_file = r'C:\Users\prisc\Documents\Athena-Public\.context\memories\health\DNA_God_Mode_Report.md'

# Dictionary structure:
# 'rsid': ('Gene', 'Trait/Disease', {'G/G': 'Description', 'A/A': 'Description'}, 'Category', 'Layman Context', 'Mitigation/Action')
MASTER_SNPS = {
    # ========================================================
    # 🫀 CARDIOLOGY, LIPIDOLOGY, & CIRCULATION
    # ========================================================
    'rs7412': ('APOE', 'Alzheimer\'s & Cardiovascular Plaque Risk (e2/e3/e4)', {'C/C': 'Normal Risk (protective allele present)', 'T/T': 'Elevated Plaque Risk', 'C/T': 'Carrier'}, 'Cardiology & Lipidology', 
               'The APOE gene determines how your body packages and clears cholesterol. Certain variants (like e4) make it harder for the body to clear plaque from arteries and the brain, increasing the long-term risk for heart disease and Alzheimer\'s.',
               'You have the protective `C/C` (e3/e3 or e2) baseline! Your body naturally clears lipid plaques from your brain and arteries at a normal or superior rate. You do not need extreme saturated-fat restrictions compared to an APOE4 carrier.'),
    
    'rs429358': ('APOE', 'Alzheimer\'s Risk Component (e4 marker)', {'T/T': 'No e4 allele (Standard risk)', 'C/C': 'Double e4 allele (High Alzheimer\'s/Cardio risk)', 'C/T': 'Single e4 allele (Elevated risk)'}, 'Cardiology & Lipidology', 
                 'This is the specific marker used to detect the notorious APOE4 variant. Having no e4 allele is the standard baseline, while having one or two can significantly raise the likelihood of plaque buildup over a lifetime.',
                 'Confirming the above: you are `T/T` at this marker. You carry ZERO copies of the Alzheimer\'s e4 gene. Your blood-brain barrier is naturally highly efficient at clearing amyloid plaques.'),
    
    'rs10455872': ('LPA', 'Lipoprotein(a) Clotting Risk', {'A/A': 'Normal limits', 'G/G': 'Highly elevated Lp(a) / Massive clot & heart attack risk', 'A/G': 'Elevated Lp(a)'}, 'Cardiology & Lipidology', 
                   'Lipoprotein(a) is a dangerous, sticky type of cholesterol that acts like a blood patch for damaged arteries. High genetic levels drastically increase the risk of blood clots, strokes, and early heart attacks, regardless of your diet.',
                   'You are `A/A` (Normal). You do not possess the terrifying genetic mutation that causes rampant microscopic blood clots. Your cardiovascular risk is entirely dictated by your diet and exercise, not a genetic death-sentence.'),
    
    'rs10757274': ('9p21 (CDKN2A/B)', 'Coronary Artery Disease Predisposition', {'A/A': 'Low risk', 'G/G': 'High risk (2x chance of heart attack)', 'A/G': 'Moderate risk'}, 'Cardiology & Lipidology', 
                   'Known as the "Heart Attack Gene," this region controls cell cycles in artery walls. The risk variant makes arteries weaker and more prone to forming dangerous blockages (atherosclerosis) independent of cholesterol levels.',
                   '**VULNERABILITY DETECTED (`G/G`)**: This is one of your most dangerous markers. Your coronary arteries are genetically prone to stiffening and retaining plaque. **Action**: You must keep your Apolipoprotein B (ApoB) blood levels near the 5th percentile (<60 mg/dL) for life, as your arteries lack the natural Teflon coating to deflect it. Aggressive Zone 2 cardio is mandatory to force vascular elasticity.'),

    'rs1799983': ('NOS3', 'Endothelial Function & Blood Pressure', {'G/G': 'Standard nitric oxide production', 'T/T': 'Reduced NO / Stiff vessels (High BP risk)', 'G/T': 'Intermediate NO'}, 'Cardiology & Lipidology', 
                  'This gene determines how well your body produces Nitric Oxide, a gas that relaxes and widens blood vessels. Reduced NO means stiffer arteries, which often leads to age-related high blood pressure and poor circulation.',
                  '**ACTION REQUIRED (`T/T` or `G/T`)**: If you carry the risk variant, your blood vessels struggle to physically dilate under stress. **Mitigation**: Consume high dietary nitrates (beetroot juice, arugula, spinach) daily. L-Citrulline supplementation (3-6g before workouts) acts as a direct bypass to force vasodilation and protect your heart.'),
    
    'rs1801133': ('MTHFR', 'Homocysteine & Vascular Damage', {'C/C': 'Normal B-vitamin metabolism (Low homocysteine)', 'T/T': 'Severe reduction in methylfolate (High homocysteine/clot risk)', 'C/T': 'Moderate reduction'}, 'Cardiology & Lipidology', 
                  'MTHFR controls your body\'s ability to convert B-vitamins from food into their active, usable forms. A bad variant causes a toxic amino acid called homocysteine to build up and scratch the inside of blood vessels, promoting clots.',
                  '**VULNERABILITY DETECTED (`C/T` / `A/G`)**: Your vitamin conversion engine runs at ~65% speed. **Action**: Completely avoid cheap supplements or fortified foods containing synthetic "Folic Acid". You must only consume the pre-converted form: **L-Methylfolate (5-MTHF)**. When getting blood work, specifically request a Homocysteine test; target levels are < 9 µmol/L to prevent artery scratching.'),
    
    'rs671': ('ALDH2', 'Aldehyde Dehydrogenase (Alcohol & Heart Protection)', {'G/G': 'Normal alcohol clearance', 'A/A': 'Severe "Asian Glow" (Toxic acetaldehyde buildup)', 'A/G': 'Moderate flushing'}, 'Cardiology & Lipidology', 
              'This gene clears the toxic byproduct of alcohol (acetaldehyde). If broken, alcohol causes extreme facial flushing and rapid heart rate. The broken variant actually protects the heart from alcoholism, as drinking becomes incredibly physically unpleasant.',
              'You are `G/G` (Normal). You process the toxic byproducts of alcohol efficiently without the "Asian Glow". However, remember that alcohol is still a class-1 carcinogen; your body is simply better at hiding the immediate toxicity.'),

    # ========================================================
    # 🧠 NEUROLOGY, PSYCHIATRY & BEHAVIOR
    # ========================================================
    'rs4680': ('COMT', 'Dopamine Clearance (Warrior vs Worrier)', {'G/G': 'Warrior (Fast clearance, cool under pressure, bored easily)', 'A/A': 'Worrier (Slow clearance, high anxiety, high memory capacity)', 'A/G': 'Balanced'}, 'Neurology & Behavior', 
               'The COMT enzyme clears dopamine from your brain\'s prefrontal cortex. "Warriors" clear it too fast, leaving them bored in everyday life but hyper-focused during crises. "Worriers" clear it slowly, leading to higher anxiety but superior memory capacity.',
               '**TRAIT DETECTED (`G/G` Warrior)**: Your brain violently sweeps dopamine away, leaving your baseline prefrontal cortex under-stimulated. **Impact**: You will experience profound boredom with mundane, repetitive tasks. You require high-stakes, crisis-level environments, intense physical stress, or deep-work flow states to actually feel "awake". Caffeine and L-Tyrosine will dramatically spike your baseline dopamine to help you function during boring tasks.'),
    
    'rs6265': ('BDNF', 'Brain Plasticity & Memory', {'C/C': 'Standard brain plasticity', 'T/T': 'Reduced brain plasticity (Struggles to learn under stress)', 'C/T': 'Moderate plasticity reduction'}, 'Neurology & Behavior', 
               'BDNF is like "Miracle-Gro" for the brain—it helps grow new neural connections. Reduced plasticity means it takes more effort to learn complex new physical or mental skills, especially when you are sleep-deprived or stressed.',
               '**VULNERABILITY DETECTED (`C/T`)**: Your brain secretes slightly less "Miracle-Gro" than average. When you are sleep-deprived or highly stressed, your ability to learn new skills or form deep memories plummets. **Mitigation**: Vigorous cardiovascular exercise (Zone 5 / Sprinting) naturally triggers massive BDNF release. Sprinting *before* attempting complex cognitive tasks will literally rewrite your brain to learn faster.'),
               
    'rs53576': ('OXTR', 'Empathy & Oxytocin Receptor', {'G/G': 'Highly empathetic, seeks social support', 'A/A': 'Independent, introverted, less easily stressed by others', 'A/G': 'Balanced'}, 'Neurology & Behavior', 
                'This dictates how your brain binds to oxytocin (the "love/bonding" hormone). Independent variants mean you do not easily absorb the emotional stress of people around you and require less social validation to feel content.',
                '**TRAIT DETECTED (`A/A`)**: You do not metabolize the social bonding hormone (oxytocin) like highly empathetic people. **Impact**: You require dramatically less social validation than peers. You are highly resistant to peer-pressure and group-think, but partners or friends may perceive you as cold or distant. Use this extreme independence as a shield during chaotic group situations.'),
                
    'rs1800497': ('ANKK1 / DRD2', 'Dopamine D2 Receptor (Addiction / Reward)', {'C/C': 'Normal dopamine receptors', 'T/T': 'Fewer dopamine receptors (Higher risk for addiction, obesity, reward-seeking)', 'C/T': 'Intermediate risk'}, 'Neurology & Behavior', 
                  'This controls how many D2 receptors your brain has to "catch" dopamine. Fewer receptors mean you experience less satisfaction from everyday joys, predisposing you to seek out extreme thrills, junk food, or addictions to feel "normal."',
                  'You possess normal density `C/C` dopamine receptors! You do not have the genetic urge to constantly hunt for extreme, self-destructive thrills (drugs, gambling, binge eating) just to feel a baseline level of satisfaction.'),

    'rs1044396': ('CHRNA4', 'Attention, Nicotine Response & Neuroticism', {'C/C': 'Higher visuospatial attention / Higher neuroticism baseline', 'T/T': 'Greater internet gaming disorder protection / Smoking cessation success', 'C/T': 'Balanced/Moderate baseline'}, 'Neurology & Behavior', 
                  'This builds nicotinic acetylcholine receptors in the brain, controlling memory and attention. The T/T variant offers protective buffering against video game addiction and helps with smoking cessation, while C/C correlates with a slightly higher baseline for neuroticism and visuospatial attention.',
                  '**TRAIT DETECTED (`C/T` / `A/G`)**: Completely balanced! You have one copy leaning toward hyper-vigilant attention, and one copy acting as a buffer against compulsive neurochemical addictions like chain-smoking or binge-gaming.'),

    'rs909525': ('MAOA', 'The "Warrior Gene" (Monoamine Oxidase A)', {'T/T': 'Low MAOA activity (More impulsive, higher aggression, higher serotonin/dopamine baseline)', 'C/C': 'High MAOA activity (Placid, lower baseline neurotransmitters)', 'C/T': 'Intermediate'}, 'Neurology & Behavior', 
                 'MAOA cleans up serotonin and adrenaline. Low activity (the famous "Warrior Gene") leaves a higher baseline of these neurotransmitters, which can lead to impulsivity and aggressive responses to provocation, but also immense drive.',
                 '**TRAIT DETECTED (`T/T` "Warrior Gene" )**: You produce much less of the clean-up enzyme for serotonin, dopamine, and adrenaline. **Impact**: Your brain is constantly "flooded" with neurochemicals. This grants immense drive, willpower, and fearlessness, but you are highly prone to sudden aggressive, impulsive outbursts if provoked. You must actively redirect this volatile aggression into disciplined physical labor (lifting) or intense career ambition, or it will manifest as destructive impulsivity.'),

    'rs1611115': ('DBH', 'Dopamine to Norepinephrine Conversion', {'C/C': 'Normal alertness conversion', 'T/T': 'Lower conversion (Prone to fatigue/ADHD)', 'C/T': 'Moderate'}, 'Neurology & Behavior', 
                  'This gene turns dopamine into norepinephrine (which drives alertness and focus). A poor conversion rate means your brain might struggle to "wake up" and stay sharp during boring tasks, a common trait in ADHD.',
                  'You are `C/C` (Normal)! Your brain flawlessly converts dopamine into pure chemical wakefulness. You do not suffer from genetic, chronic brain-fog.'),

    'rs1800955': ('DRD4', 'The "Wanderlust" & Novelty Seeking Gene', {'C/C': 'Standard DRD4 receptors', 'T/T': 'Very high novelty seeking (Wanderlust)', 'C/T': 'Moderate novelty/wanderlust'}, 'Neurology & Behavior', 
                  'A variant of the DRD4 receptor makes the brain physically crave novelty and new environments to feel stimulated. It is strongly associated with a desire to travel, immigrate, and explore new places rather than staying rooted in one hometown.',
                  '**TRAIT DETECTED (`C/C`)**: You crave stability over chaos. You do not feel the agonizing, constant genetic urge to blindly throw away your structured life to travel aimlessly or move to foreign cities for the sake of novelty.'),
                  
    'rs6903956': ('ADCYAP1R1', 'Stress & Startle Reflex', {'G/G': 'Stronger startle reflex & higher PTSD/Stress response', 'A/A': 'Lower startle reflex, highly resilient', 'A/G': 'Moderate startle reflex'}, 'Neurology & Behavior', 
                  'This gene controls sympathetic nervous system arousal. You are genetically wired to jump higher at loud noises and retain a stronger stress-imprint from traumatic events, keeping you overly vigilant after a shock.',
                  '**VULNERABILITY DETECTED (`G/G`)**: Your nervous system is hair-triggered. A sudden loud noise will flood you with significantly more adrenaline than a normal person, and traumatic events carve far deeper grooves into your psyche (drastically elevating PTSD risk). **Mitigation**: You must aggressively utilize Box Breathing (4 seconds in, 4 hold, 4 out, 4 hold) immediately following a shock to manually lower your heart rate and prevent your amygdala from entering a prolonged, exhausted freeze-state.'),

    # ========================================================
    # 💊 PHARMACOGENOMICS (Toxin & Drug Clearance)
    # ========================================================
    'rs762551': ('CYP1A2', 'Caffeine Metabolism', {'A/A': 'Fast metabolizer (Coffee has little effect on sleep after a few hours)', 'C/C': 'Ultra-slow metabolizer (Coffee causes extreme anxiety/insomnia)', 'A/C': 'Slow metabolizer'}, 'Pharmacogenomics', 
                 'Your liver uses this enzyme to clear caffeine from the bloodstream. Slow metabolizers hold onto caffeine for over 10 hours, meaning a 2 PM coffee will destroy deep sleep architecture that night.',
                 '**VULNERABILITY DETECTED (`A/C`)**: You clear caffeine incredibly slowly! **Action**: A strict 10:00 AM hard cutoff for ALL caffeine is utterly mandatory. A cup of coffee at 2 PM means 50% of the drug is still bound to your brain receptors at midnight, utterly destroying your restorative deep wave sleep, even if you "feel" like you can fall asleep.'),
                 
    'rs1065852': ('CYP2D6', 'Codeine & SSRI Metabolism', {'G/G': 'Extensive (Normal) Metabolizer', 'A/A': 'Poor metabolizer (Standard drug doses will be toxic/build up)', 'A/G': 'Intermediate'}, 'Pharmacogenomics', 
                  'CYP2D6 processes 25% of all prescription drugs, including antidepressants and painkillers. If you are a poor metabolizer, a "normal" dose prescribed by a doctor will build up to toxic levels in your body.',
                  'You possess normal `G/G` codeine/SSRI metabolism. Standard medical guidelines and textbook dosages for painkillers will work exactly as intended on your liver without accidentally poisoning you.'),

    'rs1799853': ('CYP2C9', 'Warfarin & NSAID (Ibuprofen) Clearance', {'C/C': 'Normal clearance', 'T/T': 'Poor clearance (High risk of bleeding on blood thinners/NSAIDs)', 'C/T': 'Slow clearance'}, 'Pharmacogenomics', 
                  'This enzyme breaks down NSAID painkillers (like ibuprofen) and blood thinners. Poor clearance means taking these drugs can lead to dangerous stomach bleeding, as the drug stays active in your system for far too long.',
                  'You have proper `C/C` clearance for NSAIDS! Taking standard 400mg doses of Ibuprofen for headaches or muscle pain is perfectly safe and will clear out of your stomach lining before causing horrific ulcerations.'),

    'rs2242480': ('CYP3A4', 'Statin & Testosterone Clearance', {'T/T': 'Normal clearance', 'C/C': 'Ultra-rapid metabolizer (Burns through drugs too quickly, meaning standard doses are ineffective)', 'C/T': 'Rapid metabolizer'}, 'Pharmacogenomics', 
                  'CYP3A4 handles over 50% of all medicines, including statins and testosterone. Ultra-rapid metabolism means your liver destroys the drug so fast it never gets a chance to work properly, requiring much higher prescribed doses.',
                  '**VULNERABILITY DETECTED (`C/T`)**: Your liver is a hyper-active incinerator! **Action**: If your doctor ever prescribes you a statin for your high-risk `9p21` heart gene, or if you ever require Hormone Replacement Therapy, you must warn your doctor that standard starting doses will likely be utterly destroyed by your liver before reaching your muscles. You will likely require higher, frequent doses.'),

    'rs1695': ('GSTP1', 'Glutathione Detoxification (Plastics/Heavy Metals)', {'A/A': 'Normal detox ability', 'G/G': 'Poor detox (Prone to chemical sensitivity, must supplement NAC)', 'A/G': 'Reduced detox'}, 'Pharmacogenomics', 
              'Glutathione is the body\'s master antioxidant, responsible for sweeping out toxins, plastics, and smoke. A poor GSTP1 variant means your liver struggles to attach glutathione to these toxins, allowing them to accumulate and damage DNA.',
              '**VULNERABILITY DETECTED (`A/G`)**: Your liver is slightly impaired at attaching its master detoxifier (Glutathione) to microplastics, BPA, and heavy metals. **Action**: You must aggressively eliminate daily toxin exposure (switch all plastic tupperware to glass, never drink from plastic water bottles in the sun). Supplementing with 600mg of NAC (N-Acetyl Cysteine) gives your liver the exact raw precursor it needs to force the creation of more Glutathione to compensate.'),

    # ========================================================
    # 🏃 ATHLETIC PERFORMANCE & METABOLISM
    # ========================================================
    'rs1815739': ('ACTN3', 'The Alpha-Actinin-3 "Sprint" Gene', {'C/C': 'Sprint/Power athlete (Produces protein for explosive force)', 'T/T': 'Endurance athlete (Completely lacks sprint protein)', 'C/T': 'Mixed muscle fibers'}, 'Athletics & Fitness', 
                  'This gene determines if you produce a specific protein found exclusively in fast-twitch (sprint) muscle fibers. Lacking the protein means you are naturally built for marathon-style endurance rather than explosive weightlifting.',
                  '**TRAIT DETECTED (`C/T`)**: You have a perfectly mixed 50/50 muscle fiber distribution. **Impact**: You will never be an olympic powerlifter, nor will you win the Tour de France. However, your body responds incredibly well to hybrid training (Crossfit, Hyrox, MMA) as you possess the rare capacity to build both heavy muscle mass *and* deep VO2 max cardiovascular endurance simultaneously.'),

    'rs1042713': ('ADRB2', 'Beta-2 Adrenergic (Fat burning & Power)', {'G/G': 'Power/Sprint dominant (Burns fat well during heavy resistance training)', 'A/A': 'Endurance dominant', 'A/G': 'Mixed'}, 'Athletics & Fitness', 
                  'These receptors control how your body responds to adrenaline during workouts. The power variant means adrenaline triggers massive fat burning and power output during heavy, low-rep resistance training rather than steady cardio.',
                  '**TRAIT DETECTED (`G/G`)**: A massive athletic advantage! Your beta-2 receptors are violently responsive to adrenaline. **Action**: Stop jogging on the treadmill to lose fat. Your specific genetic sequence dictates that heavy, explosive weightlifting or high-intensity sprints will shred body fat drastically faster than steady-state cardio. Your adrenaline actually "unlocks" your fat cells for fuel.'),

    'rs4341': ('ACE', 'Angiotensin Converting Enzyme (Blood Flow)', {'G/G': 'Power variant (Cardiac hypertrophy response to lifting)', 'C/C': 'Endurance variant (Extreme stamina)', 'C/G': 'Mixed'}, 'Athletics & Fitness', 
               'ACE controls blood vessel constriction. The endurance variant keeps vessels wide open, delivering massive oxygen efficiency during long runs. The power variant allows the heart to thicken and pump harder for explosive strength.',
               '**TRAIT DETECTED (`C/G`)**: Mixed response. Your cardiovascular system adapts equally to high-rep endurance loads and explosive max-power loads. Continue training in all rep ranges (1-5 reps for strength, 12-20 for hypertrophy).'),

    'rs8192678': ('PPARGC1A', 'Mitochondrial Biogenesis', {'G/G': 'Excellent mitochondrial response to exercise', 'A/A': 'Poor mitochondrial generation (Tires easily)', 'A/G': 'Moderate response'}, 'Athletics & Fitness', 
                  'Mitochondria are the powerplants of your cells. This gene controls how efficiently your body builds new mitochondria in response to aerobic exercise. Poor biogenesis means cardio improvements are slow and hard-earned.',
                  '**VULNERABILITY DETECTED (`A/G` / `C/T`)**: Your body is slightly resistant to building new mitochondrial powerplants. **Action**: You cannot rely on gentle jogging to improve your cardio. You must force mechanical stress via Zone 5 / V02 Max intervals (e.g. 4 minutes agonizingly hard cycling, 4 minutes rest, repeat 4x) to violently force your cells to multiply their mitochondria count.'),

    'rs12722': ('COL5A1', 'Collagen & Achilles Injury Risk', {'C/C': 'Strong tendons', 'T/T': 'High risk of Achilles tendinopathy (Requires extremely slow eccentric training)', 'C/T': 'Elevated tendon risk'}, 'Athletics & Fitness', 
                  'This codes the specific type of collagen used in tendons. A weak variant means your Achilles and other major tendons stretch poorly and are highly susceptible to tearing under heavy or sudden loads.',
                  '**VULNERABILITY DETECTED (`C/T`)**: Your tendons are brittle. **Action**: You must utterly abandon explosive plyometrics (like aggressive box jumps). To prevent your Achilles or patellar tendon from snapping, you must perform Heavy Slow Resistance (HSR) training—specifically focusing on the `eccentric` (lowering) phase of lifts for 4-5 seconds to painfully force the collagen fibers to remodel thicker.'),

    # ========================================================
    # 🥗 NUTRITION, DIET, & LONGEVITY
    # ========================================================
    'rs9939609': ('FTO', 'The Master "Obesity" Gene (Satiety)', {'T/T': 'Normal satiety (Knows when to stop eating)', 'A/A': 'Broken satiety (Never feels full, exceptionally high obesity risk)', 'A/T': 'Moderate satiety issues'}, 'Nutrition & Diet', 
                 'FTO is the strongest known genetic risk factor for obesity. It controls your brain\'s "I am full" signaling. The risk variant means you never truly feel satisfied after a meal, making portion control a constant, intense conscious effort.',
                 'You are perfectly `T/T` (Normal). You effortlessly know when to put the fork down. You do not possess the broken leptin-signaling pathway that makes millions of people feel physically starving directly after eating a 1000-calorie burger.'),

    'rs7903146': ('TCF7L2', 'Type 2 Diabetes Risk (Pancreatic Function)', {'C/C': 'Low diabetes risk', 'T/T': 'High diabetes risk (Pancreas prone to burnout from carbs)', 'C/T': 'Elevated risk'}, 'Nutrition & Diet', 
                  'This determines the durability of the insulin-secreting cells in your pancreas. A high risk means that chronic sugar spikes will physically exhaust and destroy your pancreas cells much earlier than the average person, accelerating diabetes.',
                  '**VULNERABILITY DETECTED (`C/T`)**: Your pancreas beta-cells are somewhat fragile. **Action**: You absolutely must not eat naked carbohydrates. If you eat bread, pasta, or sugar, you must pair it with dense protein, fat, or a preceding bowl of fiber (vegetables) to blunt the glucose spike. Frequent, massive insulin spikes will fry your pancreas ten years earlier than average.'),

    'rs4988235': ('MCM6', 'Lactose Tolerance Base', {'G/G': 'Lactose Intolerant (As adult)', 'A/A': 'Lactose Tolerant', 'A/G': 'Tolerant'}, 'Nutrition & Diet', 
                  'Historically, humans stopped producing the lactose-digesting enzyme after weaning. A genetic mutation in European and some African herding populations keeps the enzyme active for life, allowing milk consumption without stomach distress.',
                  'You possess the mutant `A/A` "Herder Engine". You can drink pure milk into your old age without gas, bloating, or stomach destruction. Leverage milk and whey protein as high-quality, cheap muscle-building blocks.'),

    'rs1544410': ('VDR', 'Vitamin D Receptor', {'A/A': 'Poor Vitamin D binding (Needs much higher blood levels)', 'G/G': 'Excellent Vitamin D binding', 'A/G': 'Moderate'}, 'Nutrition & Diet', 
                  'Your body needs Vitamin D to execute thousands of commands, but it can only do so by attaching to VDR receptors. Poor binding means even if your blood levels look "normal," your cells aren\'t absorbing it, requiring mass supplementation.',
                  '**TRAIT DETECTED (`C/C` / `G/G`)**: Perfect receptor binding! Your cells eagerly vacuum up any Vitamin D floating in your blood. You do not require dangerous mega-doses of supplements to achieve cellular immunity.'),

    'rs4588': ('GC', 'Vitamin D Transport Mechanism', {'A/A': 'Poor Vitamin D transport (Needs more sun/supplements)', 'C/C': 'Excellent Vitamin D transport', 'A/C': 'Moderate transport'}, 'Nutrition & Diet', 
               'Even if Vitamin D binds well to receptors, it must first be transported through the bloodstream by GC proteins. A poor transport gene means less Vitamin D actually reaches your peripheral tissues, leaving you deficient during winters.',
               '**VULNERABILITY DETECTED (`T/T` / `A/A`)**: Even though your receptors work, your blood is terrible at *transporting* the Vitamin D from your skin to your organs. **Action**: In the winter, you will become critically deficient fast. You absolutely must supplement 4,000 to 5,000 IUs of Vitamin D3 (always taken with Vitamin K2 and a fatty meal for absorption) daily between October and April.'),

    'rs3758391': ('SIRT1', 'Circadian Aging', {'T/T': 'Normal circadian function', 'C/C': 'Disrupted circadian aging (Shift work ages cells rapidly)', 'C/T': 'Intermediate'}, 'Nutrition & Diet', 
                  'SIRT1 repairs DNA based on strict biological clock rhythms. Disrupted aging means that violating your sleep schedule (like working night shifts or jet lag) profoundly damages your cells and accelerates biological aging.',
                  '**VULNERABILITY DETECTED (`C/C`)**: You physically cannot handle shifting your sleep schedule. **Action**: You must wake up and go to sleep at the exact same hour every single day, including weekends. Pulling all-nighters or rotating shift work will literally shred your telomeres and induce rapid biological aging and cellular dysfunction.'),

    # ========================================================
    # 🛡️ IMMUNOLOGY & AUTOIMMUNE
    # ========================================================
    'rs1800629': ('TNF-Alpha', 'Baseline Tissue Inflammation', {'G/G': 'Normal inflammation', 'A/A': 'Extremely high baseline inflammation (Joints, gut, brain)', 'A/G': 'High baseline inflammation'}, 'Immunology', 
                  'TNF-Alpha is a chemical fire alarm used to attack infections. A high baseline means your alarm is always slightly ringing, causing low-grade chronic inflammation throughout your body, leading to achy joints and brain fog.',
                  '**VULNERABILITY DETECTED (`A/G`)**: Your immune fire-alarm is broken and constantly ringing. **Action**: You are prone to random joint aches, brain fog, and chronic internal swelling. You must aggressively manage systemic inflammation by consuming 2-3g of EPA/DHA Omega-3 fish oil daily, entirely eliminating seed oils (which spike omega-6 arachidonic acid pathways), and ensuring deep sleep.'),

    'rs1800795': ('IL-6', 'Cytokine Response (Interleukin 6)', {'G/G': 'Normal cytokine response', 'C/C': 'Protective (Lower inflammatory response to stress)', 'C/G': 'Intermediate'}, 'Immunology', 
                  'IL-6 is another inflammatory messenger. A protective variant means that when you get sick or stressed, your body doesn\'t "overreact" with a massive inflammatory storm, protecting your own tissues from friendly fire.',
                  'You possess the protective `C/C` response! When you get the flu or undergo massive physical trauma, your body kills the infection without releasing a lethal "cytokine storm" that shreds your own lungs and tissues.'),

    'rs2395182': ('HLA-B27', 'Ankylosing Spondylitis & Joint Pain Risk', {'G/G': 'Standard risk', 'T/T': 'Massive risk for autoimmune joint fusion', 'G/T': 'Elevated risk'}, 'Immunology', 
                  'This is a notorious autoimmune marker. Having it means your immune cells often mistake your own spine, pelvis, and severe joints for foreign invaders, relentlessly attacking them and eventually causing the bones to permanently fuse together.',
                  '**VULNERABILITY DETECTED (`T/T`)**: ALERT: This is a critical finding. You possess the massive genetic liability for Ankylosing Spondylitis. **Action**: The moment you experience chronic, unexplainable lower back pain or morning joint stiffness that lasts for months, you must immediately report this HLA-B27 finding to a Rheumatologist. Do not ignore it, or your spinal discs may literally calcify and fuse into a solid rod over the next decade.'),

    'rs3135388': ('HLA-DRB1 / HLA-DQA1', 'Celiac Disease / Gluten Autoimmunity', {'T/T': 'Low risk for Celiac', 'A/A': 'High genetic risk for Celiac (Gluten destroys gut lining)', 'A/T': 'Carrier / Moderate risk'}, 'Immunology', 
                  'This determines if a harmless protein in wheat (gluten) triggers an autoimmune attack. If you have the high-risk genes, eating a single slice of bread commands your white blood cells to literally burn down the lining of your intestines.',
                  '**TRAIT UNMAPPED (`G/G` / Needs Sequencing)**: While `AncestryDNA` often struggles with sequencing the insanely complex HLA cluster, you should monitor your digestion. If you consistently experience brain fog, bloating, or skin rashes after eating pasta or bread, you need clinical serology (tTG-IgA) to test for full-blown Celiac.'),

    'rs1143627': ('IL-1B', 'Interleukin 1 Beta (Periodontal & Chronic Inflammation)', {'T/T': 'Normal', 'C/C': 'Severe chronic inflammation responder (Gums, arteries)', 'C/T': 'Moderate'}, 'Immunology', 
                  'IL-1B regulates bone and gum inflammation. High responders often suffer from severe, untreatable gum disease and have a significantly higher risk of arterial inflammation, intimately connecting dental health with heart attacks.',
                  '**VULNERABILITY DETECTED (`C/T` / `A/G`)**: This gene intimately connects your mouth to your heart. **Action**: You must be utterly ruthless about dental hygiene. Floss every single night and use a waterpick. Because of this gene AND your high-risk `9p21` heart gene, any plaque bacteria slipping through your bleeding gums will instantly flood your bloodstream and attach to your weakened coronary arteries.'),

    'rs1042522': ('TP53', 'The Guardian of the Genome (Cancer Suppression)', {'G/G': 'Standard p53 function', 'C/C': 'Enhanced p53 apoptosis (Aggressive cancer fighting, but ages cells faster)', 'C/G': 'Mixed function'}, 'Immunology', 
                  'TP53 is the ultimate tumor-suppressing gene. The enhanced variant commands any slightly damaged cell to immediately commit suicide (apoptosis) before it can turn into cancer. The tradeoff is that this aggressive cell-death rapidly accelerates physical aging.',
                  '**TRAIT DETECTED (`C/G`)**: You have a mixed guardian engine! Your cells strike a beautiful balance—aggressively fighting off microscopic pre-cancerous mutations without causing the rapid, rampant cell death that would prematurely age your body and skin.'),

    # ========================================================
    # 👽 CURIOSITIES, PHYSICAL TRAITS, & NEANDERTHAL
    # ========================================================
    'rs17822931': ('ABCC11', 'Body Odor & Earwax Type', {'C/C': 'Standard body odor / Wet earwax', 'T/T': 'Zero body odor (No deodorant needed) / Dry earwax', 'C/T': 'Standard body odor'}, 'Curiosities & Traits', 
                   'This quirky gene controls a pump that pushes sweat into your armpits. If the pump is genetically broken (T/T), the bacteria in your armpit have no food to eat, resulting in literally zero body odor. It also turns your earwax dry and flaky.',
                   'You are a perfectly normal `C/C`! You need to buy deodorant and Q-tips just like the rest of humanity. You unfortunately did not inherit the legendary "stink-free" mutation.'),

    'rs1805007': ('MC1R', 'Red Hair & Sun Sensitivity', {'C/C': 'Tans normally', 'T/T': 'Red hair phenotype / Burns easily', 'C/T': 'Carrier'}, 'Curiosities & Traits', 
                  'MC1R controls the type of melanin your skin makes. The red hair variant forces your body to make pheomelanin (red/yellow) instead of eumelanin (brown/black), leaving your skin virtually defenseless against UV radiation from the sun.',
                  'You possess the standard `C/C` eumelanin engine. When exposed to the sun, your skin correctly ramps up dark brown pigment production as an elite biological shield to protect your DNA from UV radiation, allowing you to tan safely instead of catastrophically bursting into sunburns.'),

    'rs1129038': ('HTR2A', 'Photic Sneeze Reflex', {'T/T': 'Sneezes in bright sunlight', 'C/C': 'Unlikely to sneeze', 'C/T': 'Moderate chance'}, 'Curiosities & Traits', 
                  'Known as ACHOO Syndrome, this is a literal crossed wire in the brain. The optic nerve (which senses bright light) accidentally fires the trigeminal nerve (which controls the nose), causing an involuntary sneeze when looking at the sun.',
                  'You do not have the crossed trigeminal wire (`C/C`)! You can walk out of a dark movie theater directly into the blazing afternoon sun without aggressively sneezing. '),

    'rs1726866': ('OR6A2', 'Cilantro Aversion', {'A/A': 'Cilantro tastes like soap', 'A/G': 'May taste soapy', 'G/G': 'Cilantro tastes normal'}, 'Curiosities & Traits', 
                  'Some people possess a specific olfactory (smell) receptor that is hypersensitive to the aldehyde chemicals present in cilantro. To them, these chemicals completely overwhelm the herb taste and make the plant taste exactly like dish soap.',
                  '**TRAIT DETECTED (`A/G`)**: You have a moderate aversion. Mild amounts might be okay, but heavy concentrations of aldehydes in Mexican or Asian dishes will overwhelm your olfactory bulb and taste strongly like chemical dish soap.'),

    'rs713598': ('TAS2R38', 'Bitter Taste Perception (Brussels Sprouts/Coffee)', {'G/G': 'Super-taster (extremely bitter)', 'C/G': 'Moderate taster', 'C/C': 'Non-taster (vegetables taste fine)'}, 'Curiosities & Traits', 
                 'This gene determines how sensitive your tongue is to glucosinolates (the bitter compounds in dark vegetables and coffee). "Super-tasters" find broccoli and black coffee physically repulsive and unbearably bitter due to an excess of these receptors.',
                 '**TRAIT DETECTED (`C/G`)**: You are a moderate taster. You can detect the extreme bitterness of glucosinolates natively found in Brussels sprouts and kale, but it is not enough to physically repel you. A pinch of salt chemically turns these receptors off, allowing you to eat healthily without disgust!'),

    'rs11568818': ('EPAS1', 'Denisovan Altitude Adaptation', {'G/G': 'Normal', 'A/A': 'Denisovan High Altitude adaptation', 'A/G': 'Carrier'}, 'Curiosities & Traits', 
                   'This is an archaic "super-gene" inherited from the mysterious Denisovan hominids. It prevents blood from becoming dangerously thick at extreme high altitudes, a trait found almost exclusively in modern Tibetan populations.',
                   '**TRAIT DETECTED (`A/G` / `T/C`)**: You carry one copy of the ancient archaic hominid super-gene! If you climb Mount Everest, your blood viscosity is genetically protected from rapidly thickening into a lethal sludge, granting you a tiny evolutionary advantage at high elevations.'),

    'rs1799990': ('PRNP', 'Prion Disease Resistance (Mad Cow)', {'G/G': 'Normal variant', 'A/A': 'Highly resistant to prion diseases', 'A/G': 'Carrier resistant'}, 'Curiosities & Traits', 
                  'This mutation alters the shape of your brain\'s prion proteins so they cannot "fold" incorrectly. It provides extreme immunity to horrific neurological prion diseases like Mad Cow Disease and Kuru (which was historically spread through cannibalism).',
                  '**TRAIT DETECTED (`A/G`)**: You are a defensive carrier! Your brain\'s prion proteins are genetically mis-shapen. While slightly eerie, this is an immense survival trait that prevents horrific, incurable zombie-like prion diseases transmitted through infected meat from taking hold in your brain architecture.')
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
        print("Initializing ULTIMATE EXHAUSTIVE GOD MODE extraction with MITIGATION ACTION PLANS...")
        
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
                    personal_impact = trait_info[5]
                    
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
                        'explanation': layman_expl,
                        'impact': personal_impact
                    })

    # Write massive report
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# 🏛️ ULTRATHINK DNA: The Ultimate Master Blueprint (Exhaustive God Mode)\n\n")
        out.write("> **Source Data**: `AncestryDNA.txt`\n")
        out.write("> **Analysis Mode**: Absolute Exhaustive Deep-Dive Mapping with Personal Mitigation Strategies\n")
        out.write("> **Warning**: This is an unedited, exhaustive extraction of highly impactful human genes. Use for informational/fitness/optimization purposes only, not clinical diagnostics.\n\n")
        
        for category, items in categories.items():
            if not items: continue
            out.write(f"## {category}\n\n")
            for item in items:
                out.write(f"### {item['trait']}\n")
                out.write(f"- **Gene (rsID)**: `{item['gene']}` (`{item['rsid']}`)\n")
                out.write(f"- **Your Genetic Code**: `{item['genotype']}`\n")
                out.write(f"- **Your Result**: **{item['result']}**\n")
                out.write(f"- **What This Means & How Hack it**: {item['explanation']} {item['impact']}\n\n")

    print(f"\nExtraction complete! Ultimate Master Document Saved:\n{output_file}")

except Exception as e:
    print(f"Error executing extraction: {e}")
