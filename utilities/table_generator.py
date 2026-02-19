import requests, os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter


TWITCH_PURPLE = (145, 70, 255)
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
FONT_PATH = "arialbd.ttf"

BACKGROUND_IMAGE_URL = "https://nitthenat.com/image/offline"

SCALE = 0.4



def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def load_image(url):
    try:
        r = requests.get(url, timeout=5)
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except:
        return None


def get_flag(code):
    url = f"https://flagcdn.com/w80/{code.lower()}.png"
    img = load_image(url)
    if img:
        img.thumbnail(FLAG_SIZE)
    return img


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_medal(base, x, y, color, size=50):

    medal = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(medal)

    draw.polygon([(size*0.3, 0), (size*0.7, 0), (size*0.5, size*0.3)],
                 fill=(200, 0, 0))

    draw.ellipse([size*0.15, size*0.25,
                  size*0.85, size*0.95],
                 fill=color)

    base.paste(medal, (x, y), medal)


def generate_war_image(data, output):

    teams = data["teams"]

    for team in teams:
        team["total"] = sum(p["score"] for p in team["members"])

    teams = sorted(teams, key=lambda t: t["total"], reverse=True)

    all_players = []
    for team in teams:
        for p in team["members"]:
            all_players.append(p)

    top_players = sorted(all_players,
                         key=lambda p: p["score"],
                         reverse=True)[:3]

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

    title_font = load_font(135)
    team_font = load_font(85)
    player_font = load_font(80)
    total_font = load_font(170)
    diff_font = load_font(110)
    watermark_font = load_font(26)

    title_text = "WAR RESULTS"
    title_x = WIDTH // 2
    title_y = PADDING

    draw.text((title_x, title_y),
              title_text,
              font=title_font,
              fill=TWITCH_PURPLE,
              anchor="mm",
              stroke_width=4,
              stroke_fill=(0, 0, 0))

    start_y = PADDING + TITLE_HEIGHT - 40
    panel_positions = []


    for i, team in enumerate(teams):

        x = PADDING + i * (col_width + COLUMN_GAP)
        y = start_y
        panel_positions.append([x, y, x+col_width, y+panel_height])

        radius = 60

        panel = Image.new("RGBA",
                          (col_width, panel_height),
                          TWITCH_GRAY + (255,))

        if "icon" in team and team["icon"]:
            icon = load_image(team["icon"])
            if icon:
                icon = icon.resize((col_width, panel_height))

                dim_layer = Image.new(
                    "RGBA",
                    (col_width, panel_height),
                    (40, 40, 45, 140)
                )

                icon = Image.alpha_composite(icon, dim_layer)
                panel.paste(icon, (0, 0), icon)

        mask = Image.new("L", (col_width, panel_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [0, 0, col_width, panel_height],
            radius=radius,
            fill=255
        )

        panel.putalpha(mask)
        img.paste(panel, (x, y), panel)

        draw.rounded_rectangle(
            [x, y, x+col_width, y+panel_height],
            radius=radius,
            outline=TWITCH_PURPLE,
            width=6
        )

        name_y = y + 75
        name_text = team["name"]
        name_w,_ = text_size(draw, name_text, team_font)

        draw.text((x + col_width//2, name_y),
                  name_text,
                  font=team_font,
                  fill=WHITE,
                  anchor="mm")

        medal_x = x + col_width//2 - (name_w // 2) - 80
        medal_y = name_y - 40

        if i == 0:
            draw_medal(img, medal_x, medal_y, (255,215,0))
        elif i == 1:
            draw_medal(img, medal_x, medal_y, (200,200,200))

        draw.line((x+60, y+TEAM_HEADER_HEIGHT-25,
                   x+col_width-60, y+TEAM_HEADER_HEIGHT-25),
                  fill=TWITCH_PURPLE,
                  width=4)

        members = sorted(team["members"],
                         key=lambda p: p["score"],
                         reverse=True)

        py = y + TEAM_HEADER_HEIGHT

        for player in members:

            name = player["name"]
            score = str(player["score"])

            name_w, name_h = text_size(draw, name, player_font)

            flag = get_flag(player["country"])
            if flag:
                flag_y = py + (ROW_HEIGHT-FLAG_SIZE[1])//2
                img.paste(flag, (x+60, flag_y), flag)

            text_y = py + (ROW_HEIGHT-name_h)//2

            draw.text((x+180, text_y),
                      name,
                      font=player_font,
                      fill=WHITE)

            if id(player) in player_medals:
                medal_x = x+180 + name_w + 15
                medal_y = text_y - 10
                draw_medal(img,
                           medal_x,
                           medal_y,
                           player_medals[id(player)],
                           size=45)

            score_w,_ = text_size(draw, score, player_font)

            draw.text((x+col_width-80-score_w, text_y),
                      score,
                      font=player_font,
                      fill=WHITE)

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

        box_width = text_w + padding_x
        box_height = text_h + padding_y

        box_center_x = (left[2] + right[0]) // 2
        box_center_y = left[3]

        box = [
            box_center_x - box_width//2,
            box_center_y - box_height//2,
            box_center_x + box_width//2,
            box_center_y + box_height//2
        ]

        draw.rounded_rectangle(
            box,
            radius=60,
            fill=TWITCH_GRAY,
            outline=TWITCH_PURPLE,
            width=6
        )

        draw.text((box_center_x, box_center_y),
                  diff_text,
                  font=diff_font,
                  fill=WHITE,
                  anchor="mm")


    draw.text(
        (WIDTH-40, height-30),
        "Developed by TMoney19 | nitthenat.com",
        font=watermark_font,
        fill=(200, 200, 200),
        anchor="rd",
        stroke_width=3,
        stroke_fill=(0, 0, 0)
    )

    final = Image.new("RGB", img.size, TWITCH_DARK)
    final.paste(img, (0, 0))

    if SCALE != 1.0:
        new_width = int(final.width * SCALE)
        new_height = int(final.height * SCALE)
        final = final.resize((new_width, new_height), Image.LANCZOS)

    final.save(output)

    print("Saved to", output)



if __name__ == "__main__":

    sample_data = {
        "teams": [
            {
                "name": "TrivialMatters",
                "icon": "https://media.discordapp.net/attachments/1324861899262656512/1324863245022003290/TMLogoV3test_1.png?ex=699833cc&is=6996e24c&hm=cbb57e584aeea3b56c929f5406a5fdcafbfb9aa12965729a70521d804e287152&=&format=webp&quality=lossless",
                "members": [
                    {"name": "Nat", "country": "gb", "score": 14},
                    {"name": "Alex", "country": "us", "score": 140},
                    {"name": "Liam", "country": "ca", "score": 130},
                    {"name": "Mia", "country": "au", "score": 120},
                    {"name": "Ethan", "country": "de", "score": 110},
                    {"name": "Chloe", "country": "fr", "score": 100}
                ]
            },
            {
                "name": "Yoshi Nuggets",
                "icon": "https://media.discordapp.net/attachments/1231262246873727086/1283909605138759750/logo_yn_png_mano.webp?ex=6998303f&is=6996debf&hm=83ae1d6ce299be2208b98bbc916b4c272173856c8053f32a7102e1b96b1b8bd4&=&format=webp",
                "members": [
                    {"name": "Hawkey", "country": "ca", "score": 160},
                    {"name": "Chrin", "country": "us", "score": 150},
                    {"name": "Choko", "country": "ca", "score": 140},
                    {"name": "Sparky", "country": "pr", "score": 120},
                    {"name": "Azusa", "country": "us", "score": 110},
                    {"name": "May", "country": "gb", "score": 90}
                ]
            }
        ]
    }

    generate_war_image(sample_data)
