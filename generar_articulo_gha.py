import requests, json, os, unicodedata, re, random
from datetime import datetime

TEMAS = [
    "Como crear un presupuesto desde cero",
    "Fondo de emergencia: cuanto necesitas realmente",
    "Invertir en ETFs y fondos indexados para principiantes",
    "Eliminar deudas: metodos avalancha vs bola de nieve",
    "Ingresos pasivos: 5 formas de generar dinero sin trabajar",
    "Interes compuesto: la octava maravilla del mundo",
    "Errores financieros que arruinan a los principiantes",
    "Ahorrar vs invertir: cual es la diferencia",
    "Como mejorar tu puntaje crediticio desde cero",
    "Educacion financiera para adolescentes y jovenes",
    "Plan de jubilacion para jovenes: empieza hoy",
    "Impuestos para freelancers y autonomos en LATAM",
    "Seguros que todo joven deberia tener",
    "Finanzas personales para parejas: como administrar en equipo",
    "Hipoteca vs alquiler: cual conviene mas",
    "Como negociar tu salario y aumentar ingresos",
    "Criptomonedas para principiantes: lo basico",
    "Metas financieras SMART: como fijarlas y cumplirlas",
    "Minimalismo financiero: gasta menos sin sacrificar felicidad",
    "Libertad financiera: hoja de ruta paso a paso",
    "Como ensenar finanzas a tus hijos",
    "Gig economy: como manejar ingresos irregulares",
    "Finanzas personales en tiempos de inflacion",
    "Los mejores habitos financieros para el 2025",
    "Como automatizar tus finanzas personales",
]

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
HEADERS = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN', '')}"}


def slugify(text):
    text = text.lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:80].rstrip("-")


def hf_generate(prompt, max_tokens=1024):
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens, "temperature": 0.7}}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    data = resp.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"].replace(prompt, "").strip()
    raise Exception(f"API error: {data}")


# Select theme deterministically by week
week_num = datetime.now().isocalendar()[1]
seed = week_num + datetime.now().year * 100
random.seed(seed)
tema = random.choice(TEMAS)
print(f"Tema: {tema}")

# Generate title
title_prompt = (
    "Generate ONLY a catchy Spanish title (max 12 words) for a blog post about: "
    f"{tema}. No quotes, no prefixes, no explanations."
)
raw_title = hf_generate(title_prompt, max_tokens=50)
title = raw_title.strip().strip("\"'")
if len(title.split()) < 3:
    title = tema
print(f"Titulo: {title}")

# Generate full article
slug = slugify(title)
today = datetime.now()
fecha = today.strftime("%Y-%m-%d")
filename = f"_posts/{fecha}-{slug}.md"

article_prompt = f"""Eres un escritor experto en finanzas personales. Escribe un articulo completo en espanol.

Titulo: {title}

Estructura:
1. INTRODUCCION (250-300 palabras) - Engancha al lector sobre {tema}
2. IMPORTANCIA (200-250 palabras) - Por que las finanzas personales importan hoy
3. PRESUPUESTO 50/30/20 (250-300 palabras) - Explica el metodo con ejemplos
4. FONDO DE EMERGENCIA (200-250 palabras) - Como construir 3-6 meses de gastos
5. ELIMINACION DE DEUDAS (200-250 palabras) - Deuda buena vs mala, metodos
6. INVERSION BASICA (250-300 palabras) - ETFs, interes compuesto para principiantes
7. INGRESOS PASIVOS (200-250 palabras) - Dividendos, contenido digital, crowdfunding
8. ERRORES COMUNES + CONCLUSION (250-300 palabras) - 5 errores y resumen motivador

Incluye EXACTAMENTE estas frases en el texto (distribuidas naturalmente):
- te recomiendo llevar un registro con esta [plantilla de presupuesto](https://amzn.to/4cV3nFg)
- El libro [Padre Rico Padre Pobre](https://amzn.to/4aXy2Kp) es un excelente punto de partida
- Para empezar a invertir, te sugiero leer [El Pequeno Libro para Invertir con Sentido Comun](https://amzn.to/3ZxY9Qm)
- Una [calculadora financiera basica](https://amzn.to/4dE5hRj) puede ayudarte a proyectar tus ahorros
- Usar una [aplicacion de ahorro automatizado](https://amzn.to/4bW8JrL) elimina la tentacion de gastar

Escribe SOLO el articulo completo, sin explicaciones adicionales."""

print("Generando articulo...")
article = hf_generate(article_prompt, max_tokens=3072)
word_count = len(article.split())
print(f"Palabras: {word_count}")

tags_list = ["finanzas", "principiantes", "educacion financiera", slug[:20]]
tags_yaml = ", ".join(f'"{t}"' for t in tags_list)

os.makedirs("_posts", exist_ok=True)

with open(filename, "w", encoding="utf-8") as f:
    f.write(f"""---
layout: post
title: "{title}"
date: {fecha} 05:00:00 -0300
categories: Finanzas Personales
tags: [{tags_yaml}]
author: Admin Financiero
description: "Articulo automatizado sobre {tema.lower()}."
---

{article}

---
*Este articulo contiene enlaces de afiliado. Si compras a traves de ellos, recibo una comision sin costo adicional para ti.*
""")

print(f"Articulo guardado: {filename}")
