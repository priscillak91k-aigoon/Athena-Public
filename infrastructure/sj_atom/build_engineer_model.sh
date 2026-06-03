#!/bin/bash
# Compiles The Engineer identity into a sovereign Ollama model

cd /home/sj/Athena-Public/infrastructure/sj_atom

echo "==========================================="
echo "⚙️ Compiling 'the-engineer' Ollama Model..."
echo "==========================================="

# Create the Modelfile
cat << 'EOF' > Modelfile.engineer
FROM qwen2.5-coder:32b
PARAMETER temperature 0.1
PARAMETER num_ctx 32768
SYSTEM """
EOF

# Inject the laws directly into the SYSTEM prompt
cat atom_brain_seed/Core_Identity.md >> Modelfile.engineer
echo -e "\n\n" >> Modelfile.engineer
cat atom_brain_seed/convictions.md >> Modelfile.engineer
echo -e "\n\n" >> Modelfile.engineer
cat atom_brain_seed/heuristics.md >> Modelfile.engineer

# Close the SYSTEM prompt block
echo '"""' >> Modelfile.engineer

echo "Building model via Ollama..."
ollama create the-engineer -f Modelfile.engineer

echo "Cleaning up..."
rm Modelfile.engineer

echo "✅ Compilation Complete! You can now run boot_engineer.sh"
