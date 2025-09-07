import csv
from datetime import datetime
from pathlib import Path

# ==== CONFIG ====
CSV_FILE = "Image Metadata.csv"
SPRITE_FILE = "sprite.svg"
OUTPUT_FILE = "index.html"
VIEWBOX = "0 0 1000 1000"
LAYER_ORDER = ["cheese", "vegetable", "egg", "meat", "dressing","bread"]
# =================

def parse_date(date_str):
    """Parse EXIF-like date 'YYYY:MM:DD HH:MM:SS' into datetime"""
    try:
        date_str = date_str.strip()
        if " " in date_str:
            date_part, time_part = date_str.split(" ", 1)
        else:
            date_part, time_part = date_str, "00:00:00"
        iso_str = date_part.replace(":", "-") + "T" + time_part
        return datetime.fromisoformat(iso_str)
    except Exception:
        return datetime.min

def normalize_bool(val):
    s = str(val or "").strip().upper()
    return "TRUE" if s == "TRUE" else "FALSE"

def main():
    # Read CSV
    sandwiches = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_date"] = parse_date(row.get("DateTaken", ""))
            row["egg"] = normalize_bool(row.get("egg"))
            row["cheese"] = normalize_bool(row.get("cheese"))
            sandwiches.append(row)

    # Normalize price
    prices = [float(r.get("price") or 0) for r in sandwiches if r.get("price")]
    if prices:
        min_price, max_price = min(prices), max(prices)
    else:
        min_price, max_price = 0, 1

    # Sort by DateTaken
    sandwiches.sort(key=lambda r: r["_date"])

    # Read sprite SVG
    sprite_content = Path(SPRITE_FILE).read_text(encoding="utf-8")
    # Hide the sprite SVG visually
    sprite_content = sprite_content.replace('<svg', '<svg style="display:none"', 1)

    # Generate sandwich blocks
    # Build sandwich SVG blocks with hover overlay
    sandwich_blocks = []
    for s in sandwiches:
        uses = []
        for attr in LAYER_ORDER:
            value = (s.get(attr) or "").strip()
            if not value:
                continue
            if attr in ("egg", "cheese"):
                value = normalize_bool(value)
            uses.append('    <use href="#{}={}"/>'.format(attr, value))
        
        # Price opacity
        try:
            price_val = float(s.get("price") or 0)
            if max_price > min_price:
                opacity = 0.1 + 0.9 * (price_val - min_price) / (max_price - min_price)
            else:
                opacity = 1
        except:
            opacity = 1

        uses.append(f'    <use href="#price" opacity="{opacity}"/>')
        
        # Use local images folder and FileName column
        img_file = s.get("FileName", "").strip()
        img_url = f"images/{img_file}"

        # Generate the sandwich block
        block = """
        <div class="sandwich" 
            data-bread="{bread}" 
            data-meat="{meat}" 
            data-egg="{egg}" 
            data-vegetable="{vegetable}" 
            data-dressing="{dressing}" 
            data-cheese="{cheese}"
            data-price="{price}">
        <svg viewBox="{viewbox}">
        {uses}
        </svg>
        <img class="overlay" src="{img_url}" alt="Sandwich"/>
        <p class="layer-text"></p>
        </div>
        """.format(
            viewbox=VIEWBOX,
            uses="\n".join(uses),
            img_url=f"images/{s.get('FileName','').strip()}",
            bread=s.get("bread","").strip(),
            meat=s.get("meat","").strip(),
            egg=s.get("egg","").strip(),
            vegetable=s.get("vegetable","").strip(),
            dressing=s.get("dressing","").strip(),
            cheese=s.get("cheese","").strip(),
            price=s.get("price","").strip()
        )
        sandwich_blocks.append(block)
    


    # Build final HTML
    html = """<!DOCTYPE html>

<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Master Degree of Sandwich Making</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Simonetta:ital,wght@0,400;0,900;1,400;1,900&family=Work+Sans:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: "Work Sans", sans-serif;
      font-weight: 400;
      margin: 2rem;
      background: #FAFAF4;
    }}
    h1 {{
        font-family: "Work Sans", sans-serif;
        font-weight: 300;
        font-size: 32px;
        text-align: center;

    }}
    h2 {{
        font-family: "Work Sans", sans-serif;
        font-weight: 600;
        font-size: 24px;
        line-height: 1.1;
        text-align: center;
    }}
    p {{
        font-family: "Work Sans", sans-serif;
        font-weight: 400;
        font-size: 16px;
        text-align: center;
        color: #000000;
        width: 100%;
    }}
    .container {{
        max-width: 1400px;
        margin: 0 auto;
    }}
    .two-col {{
    display: flex;
    flex-direction: row;
    gap: 4rem;
    align-items: flex-start;
    justify-content: center;
    margin-bottom: 4rem;
    margin-top: 4rem;
    max-width: 900px;
    }}

    .two-col .text-col {{
        flex: 1 1 0;
        max-width: 1000px;
        text-align: left;
    }}
    .two-col .svg-col {{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    @media (max-width: 800px) {{
        .two-col {{
        flex-direction: column;
        gap: 1.5em;
        }}
        .two-col .svg-col {{
        justify-content: flex-start;
        }}
    }}


    .custom-text-block {{
    margin-bottom: 1em; /* or any space you want */
    font-family: "Work Sans", sans-serif;
    font-size: 16px;
    color: #000;
    text-align: left;
    font-weight: 400;
    }}
    .svg-alone {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 4rem;
    margin-top: 4rem;
    gap: 0.5em; /* or your preferred spacing */
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    }}
    .svg-alone h2,
    .svg-alone p {{
    margin: 0;
    }}

    .footer {{
        text-align: center;
        font-family: "Work Sans", sans-serif;
        font-weight: 400;
        font-size: 12px;
    }}

    .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        justify-content: center; /* center the grid when extra space */
        gap: 0px; /* fixed gap between sandwiches */
        max-width: calc(200px * 7 + 0px * 6); /* max width for 7 columns */
        margin: 0 auto; /* center the grid container */
    }}
    .sandwich {{
        position: relative;
        width: 100%;      /* fills the grid column */
        aspect-ratio: 1/1; /* keeps square */
        max-width: 160px;  /* max size */
        min-width: 75px;   /* min size */
    }}
    svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}
        /* Filters */
    .filters {{
      margin: 1em 0;
      text-align: center;
      font-family: "Work Sans", sans-serif;
      font-weight: 400;
      padding-bottom: 1.5em;
    }}
    .filters button {{
      background: none;
      border: none;
      color: #111;
      font-size: 1rem;
      font-family: "Work Sans", sans-serif;
      font-weight: 400;
      margin: 0 0.6em;
      padding: 0;
      cursor: pointer;
      outline: none;
      box-shadow: none;
      transition: border-bottom 0.15s;
      border-bottom: 3px solid transparent;
    }}
    .filters button:hover,
    .filters button.active {{
      border-bottom: 2px solid #111;
      color: #111;
      text-underline-offset: 2px;
    }}
    .sandwich .overlay {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: none; /* hidden by default */
      object-fit: cover; /* maintain aspect ratio */
     
    }}
    .sandwich:hover .overlay {{
      display: block; /* show on hover */
      z-index: 10; /* ensure overlay is above SVG layers */
    }}
    .sandwich .layer-text {{
    position: absolute;
    top: 60%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 8pt;
    color: #9C9C9C;
    text-align: center;
    pointer-events: none; /* allow clicks to pass through */
    font-family: "Work Sans", sans-serif;
    font-weight: 400;
    mix-blend-mode: multiply;
    }}
    svg.hidden {{
      display: none;
    }}

    

  </style>
</head>
<body>
  <!-- Inline sprite -->
  {sprite}
 
  <div class="container">
    <p>
    <span style="color: #A3A3A3;">
    All the sandwiches I made (excluding the ones I bought) during my studies in the UK, from October 2024 to September 2025, in chronological order. (Anything with bread on the top and bottom and meat in between is categorized as a sandwich.)
    </span>
    </p>
  </div>

  <div class="container">
    <h1>T Eating out is expensive. My cooking skills are poor. Therefore, 240 meals of sandwiches.</h1>
  </div>

  <!-- Filter buttons -->
  <div class="filters">
    <button data-filter="all" class="active">All</button>
    <button data-filter="bread">Bread</button>
    <button data-filter="meat">Meat</button>
    <button data-filter="egg">Egg</button>
    <button data-filter="vegetable">Vegetable</button>
    <button data-filter="dressing">Dressing</button>
    <button data-filter="cheese">Cheese</button>
    <button data-filter="price">Price</button>
  </div>

  <div class="grid">
    {sandwiches}
  </div>

  <div class="container two-col">
    <div class="text-col">
        <div class="custom-text-block">
        When it comes to cooking, I’m very confident I could rank in the top 100 laziest people in the world.
        </div>
        <div class="custom-text-block">
        When I first moved to the UK and realized that Subway (the sandwich place, not the train) was just a 3-minute walk from my room, I planned to depend on them for 80% of my meals (the other 20% going to Domino’s, which was only 30 seconds away from Subway). Subway’s best promo, around £5, was still within my budget, and I’ve always liked their sandwiches no matter what people say about the quality (yes, my food standards are pretty low).
        </div>
        <div class="custom-text-block">
        However, my plan lasted only two days. I found out the promo was limited to just three uses. As paying £10 per meal for 60 meals a month was insane, I went to the supermarket and bought the same ingredients I usually ordered from Subway. That’s when I realized how much money I could save while keeping the same level of laziness in cooking (maybe even with better quality).
        </div>
        <div class="custom-text-block">
        I haven’t bought Subway since (except for that one time I was rushing to catch a train and had no choice).
        </div>
    </div>
    <div class="svg-col">
      <img src="price_chart.svg" alt="Price Chart" style="width:90vw;max-width:390px;">
    </div>
  </div>
  
  <div class="svg-alone">
    <h2>Days with self-made sandwiches</h2>
    <p>
    220 out of 341 days, including 22 days when I had them twice.
    </p>
    <img src="day_chart.svg" alt="Day Chart" style="width:90vw;max-width:900px;">
  </div>

  <div class="svg-alone">
    <h2>Top Combination</h2>
    <p>
    Processed meats (ex. bacon, ham, salami) are chosen more often than raw ingredients (ex. pork mince, fish, prawns), showing just how low my health awareness is...
    </p>
    <img src="combination_chart.svg" alt="Day Chart" style="width:90vw;max-width:900px;">
  </div>

  </div class="footer">
  <p>
  <a href="https://www.instagram.com/namsaisupavong/">Namsai Supavong</a> (2025)
  </p>
  </div>

  
  
  

  <script>
  // Hide price layer by default on page load
    document.querySelectorAll('.sandwich use[href="#price"]').forEach(use => {{
        use.style.display = 'none';
    }});

  // --- Filter buttons ---
  const buttons = document.querySelectorAll('.filters button');
  buttons.forEach(btn => {{
    btn.addEventListener('click', () => {{
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      document.querySelectorAll('.sandwich use').forEach(use => {{
        if (filter === 'all') {{
            if (use.getAttribute('href') === '#price') {{
                use.style.display = 'none'; // hide price layer by default
            }} else {{
                use.style.display = '';
            }}
        }} else if (filter === 'price') {{
            if (use.getAttribute('href') === '#price') {{
                use.style.display = '';
            }} else {{
            use.style.display = 'none';
            }}
        }} else {{
            if (use.getAttribute('href').startsWith('#' + filter + '=')) {{
                use.style.display = '';
            }} else {{
                use.style.display = 'none';
            }}
            }}
      }});
    }});
  }});

  // --- Tap overlay for mobile ---
  const sandwiches = document.querySelectorAll('.sandwich');
  let activeOverlay = null;

  sandwiches.forEach(s => {{
    const img = s.querySelector('.overlay');
    s.addEventListener('click', (e) => {{
      e.stopPropagation(); // prevent triggering document click
      if(activeOverlay && activeOverlay !== img) {{
        activeOverlay.style.display = 'none';
      }}
      if(img.style.display === 'block') {{
        img.style.display = 'none';
        activeOverlay = null;
      }} else {{
        img.style.display = 'block';
        activeOverlay = img;
      }}
    }});
  }});

  // Hide overlay if tapping anywhere else
  document.addEventListener('click', () => {{
    if(activeOverlay) {{
      activeOverlay.style.display = 'none';
      activeOverlay = null;
    }}
  }});

  // --- for layer text display ---
  buttons.forEach(btn => {{
  btn.addEventListener('click', () => {{
    buttons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filter = btn.dataset.filter;

    document.querySelectorAll('.sandwich').forEach(s => {{
      const textEl = s.querySelector('.layer-text');

      if(filter === 'all') {{
        textEl.textContent = ''; // hide text
      }} else {{
        // show value from data-* attribute
        textEl.textContent = s.dataset[filter] || '';
      }}
    }});
  }});
}});
</script>

</body>
</html>""".format(sprite=sprite_content, sandwiches="".join(sandwich_blocks))

    Path(OUTPUT_FILE).write_text(html, encoding="utf-8")
    print("✅ Generated {} with {} sandwiches.".format(OUTPUT_FILE, len(sandwiches)))

if __name__ == "__main__":
    main()
