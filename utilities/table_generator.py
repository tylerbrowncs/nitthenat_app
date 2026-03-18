import requests
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from datetime import datetime

# ============================
# THEME
# ============================

ACCENTS = (145, 70, 255)
TWITCH_GRAY = (40, 40, 45)
TWITCH_DARK = (24, 24, 27)
WHITE = (255, 255, 255)

WIDTH = 2600
PADDING = 120
COLUMN_GAP = 120
TEAM_HEADER_HEIGHT = 160
ROW_HEIGHT = 140
TITLE_HEIGHT = 160
BOTTOM_PADDING = 200

FLAG_SIZE = (85, 55)
SCALE = 0.4

# ============================
# FONT LOADER
# ============================

PROJECT_FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    "fonts",
    "Montserrat-Bold.ttf"
)

SYSTEM_FONT_PATHS = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/Arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
]

def find_font():
    if os.path.exists(PROJECT_FONT_PATH):
        return PROJECT_FONT_PATH
    for path in SYSTEM_FONT_PATHS:
        if os.path.exists(path):
            return path
    return None

FONT_PATH = find_font()

def load_font(size):
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()

# ============================
# HELPERS
# ============================

def load_image(url):
    try:
        r = requests.get(url, timeout=5)
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except:
        return None

def get_flag(code):
    url = f"https://flagcdn.com/w80/{code.lower()}.png"
    img = load_image(url)
    if not img:
        return None

    width = 100
    height = 65
    radius = 30
    border = 4

    scale = max(width / img.width, height / img.height)
    img = img.resize(
        (int(img.width * scale), int(img.height * scale)),
        Image.LANCZOS
    )

    left = (img.width - width) // 2
    top = (img.height - height) // 2
    img = img.crop((left, top, left + width, top + height))

    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, width, height),
        radius=radius,
        fill=255
    )
    img.putalpha(mask)

    final_w = width + border * 2
    final_h = height + border * 2

    result = Image.new("RGBA", (final_w, final_h), (0, 0, 0, 0))

    border_mask = Image.new("L", (final_w, final_h), 0)
    ImageDraw.Draw(border_mask).rounded_rectangle(
        (0, 0, final_w, final_h),
        radius=radius + border,
        fill=255
    )

    border_shape = Image.new("RGBA", (final_w, final_h), (255, 255, 255, 255))
    border_shape.putalpha(border_mask)

    result.paste(border_shape, (0, 0), border_shape)
    result.paste(img, (border, border), img)

    return result

def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_medal(base, x, y, color, size=50):
    medal = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(medal)

    d.polygon([(size*0.3, 0), (size*0.7, 0), (size*0.5, size*0.3)],
              fill=(200, 0, 0))
    d.ellipse([size*0.15, size*0.25, size*0.85, size*0.95],
              fill=color)

    base.paste(medal, (x, y), medal)

# ============================
# MAIN GENERATOR
# ============================

def generate_war_image(data, output, BACKGROUND_IMAGE_URL, title, sub_text=datetime.now().strftime("%b %d, %Y"), ACCENTS = (145, 70, 255)):

    teams = data["teams"]

    title_font = load_font(115)
    team_font = load_font(75)
    player_font = load_font(80)
    total_font = load_font(170)
    diff_font = load_font(110)
    watermark_font = load_font(26)
    date_font = load_font(40)

    for team in teams:
        team["total"] = sum(p["score"] for p in team["members"])

    teams = sorted(teams, key=lambda t: t["total"], reverse=True)

    all_players = [p for t in teams for p in t["members"]]
    top_players = sorted(all_players, key=lambda p: p["score"], reverse=True)[:3]

    medal_colors = [(255,215,0), (200,200,200), (205,127,50)]
    player_medals = {id(p): medal_colors[i] for i,p in enumerate(top_players)}

    columns = 2
    col_width = (WIDTH - PADDING*2 - COLUMN_GAP) // columns
    max_players = max(len(t["members"]) for t in teams)

    panel_height = TEAM_HEADER_HEIGHT + max_players*ROW_HEIGHT + BOTTOM_PADDING
    height = PADDING*2 + TITLE_HEIGHT + panel_height

    base = Image.new("RGBA", (WIDTH, height), TWITCH_DARK + (255,))
    background = load_image(BACKGROUND_IMAGE_URL)
    if background:
        background = background.resize((WIDTH, height))
        base.paste(background, (0, 0))

    img = base.copy()
    draw = ImageDraw.Draw(img)


    draw.text((WIDTH//2, PADDING-25), title,
              font=title_font,
              fill=ACCENTS,
              anchor="mm",
              stroke_width=4,
              stroke_fill=(0,0,0))
    

    draw.text((WIDTH//2, PADDING+60), sub_text,
              font=date_font,
              fill=WHITE,
              anchor="mm",
              stroke_width=4,
              stroke_fill=(0,0,0))
    
    start_y = PADDING + TITLE_HEIGHT - 40
    panel_positions = []

    for i, team in enumerate(teams):

        x = PADDING + i * (col_width + COLUMN_GAP)
        y = start_y
        panel_positions.append([x, y, x+col_width, y+panel_height])

        radius = 60

        if len(team["name"]) > 18:
            team_font = load_font(55)
        else:
            team_font = load_font(75)


        panel = Image.new("RGBA", (col_width, panel_height), (0,0,0,0))

        if team.get("icon"):
            icon = load_image(team["icon"])
            if icon:
                icon = icon.resize((col_width, panel_height), Image.LANCZOS)
                overlay = Image.new("RGBA", icon.size, (40,40,45,200))
                icon = Image.alpha_composite(icon, overlay)
                panel.paste(icon, (0,0), icon)

        mask = Image.new("L", (col_width, panel_height), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0,0,col_width,panel_height],
            radius=radius,
            fill=255
        )

        rounded_panel = Image.new("RGBA", (col_width, panel_height))
        rounded_panel.paste(panel, (0,0), mask)

        img.paste(rounded_panel, (x,y), rounded_panel)

        draw.rounded_rectangle(
             [x,y,x+col_width,y+panel_height],
             radius=radius,
             outline=ACCENTS,
             width=6
         )

        name_y = y + 75
        name = team["name"]
        name_w,_ = text_size(draw, name, team_font)

        draw.text((x+col_width//2, name_y),
                  name, font=team_font, fill=WHITE, anchor="mm")

        medal_x = x + col_width//2 - (name_w//2) - 80
        medal_y = name_y - 40

        if i == 0:
            draw_medal(img, medal_x, medal_y, (255,215,0))
        elif i == 1:
            draw_medal(img, medal_x, medal_y, (200,200,200))

        draw.line((x+60, y+TEAM_HEADER_HEIGHT-25,
                   x+col_width-60, y+TEAM_HEADER_HEIGHT-25),
                  fill=ACCENTS, width=4)

        py = y + TEAM_HEADER_HEIGHT

        for player in sorted(team["members"], key=lambda p:p["score"], reverse=True):

            name = player["name"]

            if len(name) > 18:
                player_font = load_font(45)
            else:
                player_font = load_font(80)

            score = str(player["score"])

            name_w, name_h = text_size(draw, name, player_font)

            flag = get_flag(player["country"])
            if flag:
                img.paste(flag, (x+60, py+(ROW_HEIGHT-FLAG_SIZE[1])//2), flag)

            text_y = py + (ROW_HEIGHT-name_h)//2

            draw.text((x+180, text_y),
                      name, font=player_font, fill=WHITE)

            if id(player) in player_medals:
                draw_medal(img,
                           x+180+name_w+15,
                           text_y-10,
                           player_medals[id(player)],
                           45)

            score_w,_ = text_size(draw, score, player_font)

            draw.text((x+col_width-80-score_w, text_y),
                      score, font=player_font, fill=WHITE)

            py += ROW_HEIGHT

        draw.text((x+col_width//2, y+panel_height-130),
                  str(team["total"]),
                  font=total_font,
                  fill=WHITE,
                  anchor="mm")

    if len(teams) == 2:
        diff = teams[0]["total"] - teams[1]["total"]
        diff_text = f"+{diff}" if diff > 0 else str(diff)

        left = panel_positions[0]
        right = panel_positions[1]

        text_w,text_h = text_size(draw, diff_text, diff_font)

        padding_x = 200
        padding_y = 100

        box_w = text_w + padding_x
        box_h = text_h + padding_y

        cx = (left[2] + right[0]) // 2
        cy = left[3]

        box = [cx-box_w//2, cy-box_h//2,
               cx+box_w//2, cy+box_h//2]

        draw.rounded_rectangle(box,
                               radius=60,
                               fill=TWITCH_GRAY,
                               outline=ACCENTS,
                               width=6)

        draw.text((cx, cy),
                  diff_text,
                  font=diff_font,
                  fill=WHITE,
                  anchor="mm")

    draw.text((WIDTH-40, height-30),
              "Developed by TMoney19 | nitthenat.com",
              font=watermark_font,
              fill=(200,200,200),
              anchor="rd",
              stroke_width=3,
              stroke_fill=(0,0,0))

    final = img

    if SCALE != 1.0:
        final = final.resize(
            (int(final.width*SCALE), int(final.height*SCALE)),
            Image.LANCZOS
        )

    # Remove transparency completely
    final = final.convert("RGB")

    final.save(output)
    print("Saved to", output)


# ============================
# TEST
# ============================

if __name__ == "__main__":

    sample_data = {
        "teams": [
            {
                "name": "Trivial Matters (TM) xyz12345",
                "icon": "https://media.discordapp.net/attachments/1231262099871633549/1281379714577203312/u44K2BWxA0zseaTzLV8wjLnfnSyBhC5Now432tHA_1.png?ex=699e255a&is=699cd3da&hm=839a8a503ccb8bcf6355f71618cc9d8d59c12dc700a3d4a922e8d38bdeff0318&=&format=webp&quality=lossless",
                "members": [
                    {"name": "NatTheNatFromWalesYippy", "country": "gb-wls", "score": 154},
                    {"name": "Alex", "country": "gb-eng", "score": 140},
                    {"name": "Liam", "country": "gb-sct", "score": 130},
                    {"name": "Mia", "country": "gb-nir", "score": 120},
                    {"name": "Ethan", "country": "de", "score": 110},
                    {"name": "Chloe", "country": "fr", "score": 100}
                ]
            },
            {
                "name": "Influx",
                "icon": "https://media.discordapp.net/attachments/1324872676074061864/1324873171597525003/mTFB7Expbp6dXI9A9JK3Q0U61besy0wEZM5aZmtE.png?ex=699e2bcb&is=699cda4b&hm=eacdc83d6c9c7716a7faed558030e89def8e6d82af153c88ebf7fbeeb7c2a948&=&format=webp&quality=lossless",
                "members": [
                    {"name": "Hawkey", "country": "ca", "score": 160},
                    {"name": "Chrin", "country": "us", "score": 1350},
                    {"name": "Choko", "country": "ca", "score": 140},
                    {"name": "Sparky", "country": "pr", "score": 120},
                    {"name": "Azusa", "country": "us", "score": 110},
                    {"name": "May", "country": "gb", "score": 90}
                ]
            }
        ]
    }

    generate_war_image(sample_data, "test.png", "https://catwithmonocle.com/wp-content/uploads/2023/04/smb-movie-mario-kart-3840x2160-1.jpg", "TM vs Influx | #1921", ACCENTS=(0, 255, 255))

