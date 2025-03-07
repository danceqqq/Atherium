(function() {{
  var ColorThief = function() {{}};

  ColorThief.prototype.getDominantColor = function(image, quality) {{
    quality = quality || 10;
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');

    canvas.width = image.width / quality;
    canvas.height = image.height / quality;
    context.drawImage(image, 0, 0, canvas.width, canvas.height);

    var data = context.getImageData(0, 0, canvas.width, canvas.height).data;
    const palette = [];

    for (let i = 0; i < data.length; i += 4) {{
      palette.push({{
        r: data[i],
        g: data[i + 1],
        b: data[i + 2]
      }});
    }}

    let counts = {{}};
    palette.forEach(color => {{
      const key = `${{color.r}},${{color.g}},${{color.b}}`;
      counts[key] = (counts[key] || 0) + 1;
    }});

    let dominant = palette[0];
    let maxCount = 0;

    for (const key in counts) {{
      if (counts[key] > maxCount) {{
        maxCount = counts[key];
        dominant = key.split(',').map(Number);
      }}
    }}

    return {{ r: dominant[0], g: dominant[1], b: dominant[2] }};
  }};

  window.ColorThief = ColorThief;
}})();