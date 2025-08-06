import re

import pandas as pd

df = pd.read_csv("smartphone_qa.csv")

prompts = []
references = []

# 2. Para cada fila, extrae user y assistant
for text in df["text"]:
    # extrae lo que esté entre <|im_start|>user y <|im_end|>
    u = re.search(r"<\|im_start\|>user\\n(.*?)<\|im_end\|>", text, re.DOTALL)
    # extrae lo que esté entre <|im_start|>assistant y <|im_end|>
    a = re.search(r"<\|im_start\|>assistant\\n(.*?)<\|im_end\|>", text, re.DOTALL)

    if u and a:
        prompts.append(u.group(1).strip())
        references.append(a.group(1).strip())
    else:
        # si no se encuentra alguno, lo saltamos o manejamos como quieras
        continue

# 3. Crea el DataFrame de evaluación
df_eval = pd.DataFrame({"prompt": prompts, "reference": references})

# 4. Guarda a CSV
df_eval.to_csv("eval.csv", index=False, encoding="utf-8")

print(f"Generado eval.csv con {len(df_eval)} ejemplos.")
