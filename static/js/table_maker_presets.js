function setValue(selector, value) {
  const el = document.querySelector(selector);
  if (!el) return;

  if (el.tagName === "SELECT") {
    if (window.jQuery && $(el).hasClass("select2-hidden-accessible")) {
      $(el).val(value).trigger("change");
    } else {
      el.value = value;
    }
  } else {
    el.value = value;
  }
}

function resetSelect(select) {
  if (window.jQuery && $(select).hasClass("select2-hidden-accessible")) {
    $(select).val(null).trigger("change");
  } else {
    select.selectedIndex = 0;
  }
}



function applyPreset(preset) {
    document.querySelectorAll("input").forEach(input => {
      if (input.type === "color") {
        input.value = "#9146ff";
      } else if (input.name && input.name.includes("_pen")) {
        input.value = 0;
      } else {
        input.value = "";
      }
    });

    document.querySelectorAll("select:not(#preset)").forEach(select => {
      resetSelect(select);
    });


  if (preset === "Development") {
    setValue("[name='title_text']", "DEV WAR");
    setValue("[name='subtitle']", "Test Match");
    setValue("[name='background_url']", "https://i.redd.it/wallpapers-last-ones-my-fav-v0-5m9xra3qz2re1.jpg?width=1920&format=pjpg&auto=webp&s=30a6565d4d6d7a8da0293350ac18691470dde51b");
    setValue("[name='favcolor']", "#e76464");

    setValue("[name='team1_name']", "Team Alpha");
    setValue("[name='team1_icon']", "https://static.wikia.nocookie.net/frieren/images/3/35/Frieren_anime_profile.png/revision/latest/smart/width/250/height/250?cb=20230521074853");

    for (let i = 0; i < 6; i++) {
      setValue(`[name='team1_p${i}_name']`, `A_Player_${i+1}`);
      setValue(`[name='team1_p${i}_score']`, 50 + i);
      setValue(`[name='team1_p${i}_pen']`, 0);
      setValue(`[name='team1_p${i}_country']`, "Wales");
    }

    setValue("[name='team2_name']", "Team Beta");
    setValue("[name='team2_icon']", "https://static.wikia.nocookie.net/frieren/images/1/12/Stark_anime_portrait_%28Season_2%29.png/revision/latest?cb=20260118202106");

    for (let i = 0; i < 6; i++) {
      setValue(`[name='team2_p${i}_name']`, `B_Player_${i+1}`);
      setValue(`[name='team2_p${i}_score']`, 45 + i);
      setValue(`[name='team2_p${i}_pen']`, 0);
      setValue(`[name='team2_p${i}_country']`, "Wales");
    }
  }

   if (preset === "TM") {
    setValue("[name='title_text']", "War #XXXX");
    setValue("[name='background_url']", "https://nitthenat.com/image/tmtablebackground");
    setValue("[name='favcolor']", "#FFFFFF");

    setValue("[name='team1_name']", "Trivial Matters (™)");
    setValue("[name='team1_icon']", "https://nitthenat.com/image/tmlogo");

  }

  if (preset === "ARC") {
    setValue("[name='title_text']", "Arcadia Terra vs ___");
    setValue("[name='background_url']", "https://nitthenat.com/image/arctablebackground");
    setValue("[name='favcolor']", "#FFD700");

    setValue("[name='team1_name']", "Arcadia Terra (ARC)");
    setValue("[name='team1_icon']", "https://nitthenat.com/image/arclogo");

  }

  if (preset === "CB") {
    setValue("[name='title_text']", "Caledonbria vs ___");
    setValue("[name='background_url']", "https://nitthenat.com/image/cbtablebackground");
    setValue("[name='favcolor']", "#33E8CD");

    setValue("[name='team1_name']", "Caledonbria (CB)");
    setValue("[name='team1_icon']", "https://nitthenat.com/image/cblogo");

  }

  if (preset === "VSP") {
    setValue("[name='title_text']", "Vespertine vs ___");
    setValue("[name='background_url']", "https://nitthenat.com/image/vsptablebackground");
    setValue("[name='favcolor']", "#FFFFFF");

    setValue("[name='team1_name']", "Vespertine (νsρ)");
    setValue("[name='team1_icon']", "https://nitthenat.com/image/vsplogo");

  }
}

document.addEventListener("DOMContentLoaded", function () {
  const presetDropdown = document.getElementById("preset");

  presetDropdown.addEventListener("change", function () {
    applyPreset(this.value);
  });
});