from pathlib import Path
import json

from build_lib import (
    ROOT, load_all, load_aliases_map, slugify, human_porte,
    score_atividade, score_grooming, score_clima, get_aliases_for_breed
)

def main():
    site, rules, racas = load_all()
    aliases_map = load_aliases_map()

    client = []
    for r in racas:
        slug = slugify(r["nome"])
        grupo = r["atributos"].get("fci_grupo")
        porte_slug = (r["atributos"].get("porte") or "").lower()
        porte_label = human_porte(porte_slug)

        atividade_val, _txtA, factsA = score_atividade(r, rules)
        grooming_val,  _txtG, factsG = score_grooming(r, rules)
        clima_val,     _txtC, factsC = score_clima(r, rules, atividade_val)

        client.append({
            "slug": slug,
            "nome": r["nome"],
            "foto": r.get("foto",""),
            "origem": r.get("origem","—"),
            "fci": {"grupo": grupo, "descricao": rules["fci_grupos"].get(str(grupo), "—")},
            "porte": {"slug": porte_slug, "label": porte_label},
            "medidas": {
              "altura_cm": r["medidas"]["altura_cm"],
              "peso_kg":   r["medidas"]["peso_kg"],
              "expectativa_anos": r["medidas"].get("expectativa_anos","—")
            },
            "energia":  {"valor": atividade_val, **factsA},
            "pelagem":  {"valor": grooming_val,  **factsG},
            "clima":    {"valor": clima_val,     **factsC},
            "aliases":  get_aliases_for_breed(r, aliases_map),
        })

    out = ROOT/"data"; out.mkdir(exist_ok=True)
    (out/"breeds-client.json").write_text(
        json.dumps(client, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

if __name__ == "__main__":
    main()
