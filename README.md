# Modi-Cogitandi
Modes of thought

In order to launch it from the command line or as a Python subprocess:
```bash
echo "Theodotos-Alexandreus: What mode of thought should we use, machine?" \
  | uvx modi-cogitandi \
    --provider-api-key=sk-proj-... \
    --github-token=ghp_... 
```

Or, with a local pip installation:
```bash
pip install modi-cogitandi
```
Set the environment variables:
```bash
export PROVIDER_API_KEY="sk-proj-..."
export GITHUB_TOKEN="ghp_..."
```
Then:
```bash
modi-cogitandi multilogue.txt
```
Or:
```bash
modi-cogitandi multilogue.txt > output.txt
```
Or:
```bash
modi-cogitandi multilogue.txt > tmp && mv tmp multilogue.txt
```
Or:
```bash
cat multilogue.txt new_turn.txt | modi-cogitandi
```
Or:
```bash
cat multilogue.txt new_turn.txt | modi-cogitandi > tmp && mv tmp multilogue.txt
```
Or: 
```bash
(cat multilogue.txt; echo:"Theodotos: What do you think, Modi-Cogitandi?") \
  | modi-cogitandi
```
Or:
```bash
cat multilogue.txt new_turn.txt | modi-cogitandi > tmp && mv tmp multilogue.txt
```
Or, if you have installed other machines:
```bash
cat multilogue.md | modi-cogitandi \
  | summarizing-machine | judging-machine > summary_judgment.md
```

Or use it in your Python code:
```Python
# Python
import modi_cogitandi
```
