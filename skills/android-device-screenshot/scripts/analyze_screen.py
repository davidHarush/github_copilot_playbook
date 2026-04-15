#!/usr/bin/env python3
"""
analyze_screen.py  (v3 — Combined Vision)
==========================================
Combines TWO complementary data sources into one unified screen report:

  SOURCE 1 — uiautomator XML dump
    Reads the real Android accessibility tree.
    Gives 100% accurate text in ANY language (Hebrew, Arabic, RTL).
    Provides: text, element type, position, clickability, package name.

  SOURCE 2 — Screenshot (PNG) visual analysis
    Analyzes the actual pixels of the screenshot.
    Provides: theme (dark/light), dominant colors per zone,
              image/icon count estimate, layout density.

Together they give a complete picture:
  "What does the screen SAY" (uiautomator) +
  "What does the screen LOOK LIKE" (screenshot)

Usage:
    python3 analyze_screen.py <screenshot.png> [ui_dump.xml] [--json]
"""

import sys, os, json, argparse, re, collections
from pathlib import Path


# ── dependency bootstrap ────────────────────────────────────────────────────
def _ensure(pkg, import_name=None):
    import importlib
    try:
        importlib.import_module(import_name or pkg)
    except ImportError:
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg,
             "--break-system-packages", "-q"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

_ensure("pillow", "PIL")
_ensure("pytesseract")

from PIL import Image, ImageEnhance, ImageOps
import pytesseract


# ══════════════════════════════════════════════════════════════════════════════
# DIMENSION UTILITIES  (px ↔ dp / sp)
# ══════════════════════════════════════════════════════════════════════════════

def px_to_dp(px: float, density: int) -> float:
    """Convert pixels to density-independent pixels (dp).
    Formula: dp = px * 160 / dpi
    """
    return round(px * 160.0 / density, 1) if density > 0 else round(float(px), 1)


def px_to_sp(px: float, density: int, font_scale: float = 1.0) -> float:
    """Estimate scale-independent pixels (sp) from pixel height.
    sp = dp / font_scale  (height of element ≈ font size at default scale)
    """
    return round(px_to_dp(px, density) / max(font_scale, 0.1), 1)


def _dpi_class(dpi: int) -> str:
    """Return the Android density bucket name for a given DPI value."""
    if dpi < 145:   return "ldpi"
    elif dpi < 210: return "mdpi"
    elif dpi < 280: return "hdpi"
    elif dpi < 400: return "xhdpi"
    elif dpi < 560: return "xxhdpi"
    else:           return "xxxhdpi"


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 1 — uiautomator XML
# ══════════════════════════════════════════════════════════════════════════════

def parse_ui_dump(xml_path: str, density: int = 420, font_scale: float = 1.0) -> dict:
    """Parse uiautomator XML → structured element list with full metadata and px/dp/sp dimensions."""
    import xml.etree.ElementTree as ET
    tree    = ET.parse(xml_path)
    package = ""
    items   = []

    # Classes for which height ≈ font size → report height_sp
    _TEXT_CLASSES = {
        "TextView", "Button", "ImageButton", "EditText",
        "CheckBox", "RadioButton", "Switch", "ToggleButton",
    }

    for node in tree.iter("node"):
        text      = node.get("text", "").strip()
        desc      = node.get("content-desc", "").strip()
        cls       = node.get("class", "").split(".")[-1]
        pkg       = node.get("package", "")
        res_id    = node.get("resource-id", "").split("/")[-1]
        bounds    = node.get("bounds", "")
        clickable = node.get("clickable", "false") == "true"
        scrollable= node.get("scrollable", "false") == "true"
        enabled   = node.get("enabled",   "true")  == "true"

        if pkg and not package:
            package = pkg

        label = text or desc
        if not label:
            continue

        # Parse pixel coordinates from bounds string "[x1,y1][x2,y2]"
        x1, y1, x2, y2, cx, cy = _bounds_rect(bounds)
        w_px = max(x2 - x1, 0)
        h_px = max(y2 - y1, 0)

        items.append({
            "text":       label,
            "class":      cls,
            "resource":   res_id,
            "bounds":     bounds,
            "clickable":  clickable,
            "scrollable": scrollable,
            "enabled":    enabled,
            # Raw pixel coordinates & dimensions
            "x1_px": x1,   "y1_px": y1,
            "x2_px": x2,   "y2_px": y2,
            "cx_px": cx,   "cy_px": cy,
            "width_px":  w_px,
            "height_px": h_px,
            # Density-independent pixels (dp)
            "x_dp":      px_to_dp(x1,   density),
            "y_dp":      px_to_dp(y1,   density),
            "width_dp":  px_to_dp(w_px, density),
            "height_dp": px_to_dp(h_px, density),
            # Scale-independent pixels (sp) — only for text/button elements
            "height_sp": px_to_sp(h_px, density, font_scale) if cls in _TEXT_CLASSES else None,
        })

    return {
        "package":  package,
        "app_name": _guess_screen_name(items, package),
        "items":    items,
        "texts":    [i["text"] for i in items],
    }


def _guess_screen_name(items: list, package: str) -> str:
    for item in items:
        if any(k in item["resource"].lower()
               for k in ("title", "toolbar", "header", "app_name")):
            if len(item["text"]) > 1:
                return item["text"]
    for item in items:
        if item["class"] == "TextView" and len(item["text"]) > 2:
            return item["text"]
    return package.split(".")[-1] if package else "Unknown"


def _bounds_rect(bounds: str):
    m = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
    if m:
        x1,y1,x2,y2 = map(int, m.groups())
        return x1, y1, x2, y2, (x1+x2)//2, (y1+y2)//2
    return 0,0,0,0,0,0


def _zone_label(cy: int, h: int) -> str:
    p = cy / h if h else 0.5
    if p < 0.06:   return "STATUS_BAR"
    if p < 0.15:   return "TOP_BAR"
    if p > 0.92:   return "NAVIGATION_BAR"
    if p > 0.80:   return "BOTTOM_ACTION_BAR"
    return "CONTENT"


def _group_by_zone(items: list, h: int) -> dict:
    zones = {z: [] for z in
             ["STATUS_BAR","TOP_BAR","CONTENT","BOTTOM_ACTION_BAR","NAVIGATION_BAR"]}
    for item in items:
        *_, cx, cy = _bounds_rect(item["bounds"])
        zones[_zone_label(cy, h)].append(item)
    return zones


def _ui_stats(items: list) -> dict:
    classes = collections.Counter(i["class"] for i in items)
    return {
        "total_elements":   len(items),
        "clickable":        sum(1 for i in items if i["clickable"]),
        "scrollable":       sum(1 for i in items if i["scrollable"]),
        "text_views":       classes.get("TextView", 0),
        "buttons":          classes.get("Button", 0)
                          + classes.get("ImageButton", 0),
        "images":           classes.get("ImageView", 0),
        "edit_texts":       classes.get("EditText", 0),
        "lists":            classes.get("RecyclerView", 0)
                          + classes.get("ListView", 0),
    }


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 2 — Screenshot visual analysis
# ══════════════════════════════════════════════════════════════════════════════

def _detect_theme(img: Image.Image) -> str:
    strip = img.crop((0, 0, img.width, min(80, img.height))).convert("L")
    avg   = sum(strip.tobytes()) / max(len(strip.tobytes()), 1)
    return "dark" if avg < 128 else "light"


def _hex(r, g, b) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def _zone_avg_color(img: Image.Image, box: tuple) -> tuple:
    region = img.crop(box).convert("RGB").resize((50, 50))
    raw    = list(region.tobytes())
    n      = 50 * 50
    r = sum(raw[i]   for i in range(0, len(raw), 3)) // n
    g = sum(raw[i+1] for i in range(0, len(raw), 3)) // n
    b = sum(raw[i+2] for i in range(0, len(raw), 3)) // n
    return r, g, b


def _dominant_colors(img: Image.Image, n: int = 5) -> list:
    small  = img.convert("RGB").resize((80, 160))
    raw    = small.tobytes()
    pixels = [tuple(raw[i:i+3]) for i in range(0, len(raw), 3)]
    counts = collections.Counter(pixels).most_common(n)
    return [{"hex": _hex(*rgb), "rgb": rgb, "count": cnt}
            for rgb, cnt in counts]


def _brightness(r, g, b) -> int:
    return (r * 299 + g * 587 + b * 114) // 1000


def visual_analysis(img: Image.Image, h: int) -> dict:
    """Extract visual properties from the screenshot pixels."""
    w     = img.width
    theme = _detect_theme(img)

    zones_colors = {
        "status_bar":       _zone_avg_color(img, (0, 0,          w, int(h*0.06))),
        "top_bar":          _zone_avg_color(img, (0, int(h*0.06),w, int(h*0.15))),
        "content":          _zone_avg_color(img, (0, int(h*0.15),w, int(h*0.80))),
        "bottom_action_bar":_zone_avg_color(img, (0, int(h*0.80),w, int(h*0.92))),
        "navigation_bar":   _zone_avg_color(img, (0, int(h*0.92),w, h)),
    }

    return {
        "theme":         theme,
        "dominant_colors": _dominant_colors(img),
        "zone_colors":   {k: {"hex": _hex(*v), "brightness": _brightness(*v)}
                          for k, v in zones_colors.items()},
    }


# ══════════════════════════════════════════════════════════════════════════════
# FALLBACK — OCR (only when uiautomator not available)
# ══════════════════════════════════════════════════════════════════════════════

def _tesseract_ok() -> bool:
    try:
        pytesseract.get_tesseract_version(); return True
    except Exception:
        return False


def ocr_fallback(img: Image.Image, theme: str) -> list:
    large = img.resize((img.width*2, img.height*2), Image.LANCZOS).convert("L")
    if theme == "dark":
        large = ImageOps.invert(large)
    large = ImageEnhance.Contrast(large).enhance(1.8)
    lang  = "heb+eng" if _tesseract_ok() else "eng"
    best  = ""
    for cfg in ["--psm 6","--psm 3","--psm 11"]:
        try:
            t = pytesseract.image_to_string(large, lang=lang, config=cfg).strip()
            if len(t) > len(best): best = t
        except Exception:
            pass
    seen, out = set(), []
    for line in best.splitlines():
        k = re.sub(r"\s+", " ", line.strip()).lower()
        if k and k not in seen:
            seen.add(k); out.append(line.strip())
    return out


# ══════════════════════════════════════════════════════════════════════════════
# COMBINED REPORT
# ══════════════════════════════════════════════════════════════════════════════

def analyze(image_path: str, xml_path: str = None, output_json: bool = False,
            density: int = 420, font_scale: float = 1.0) -> dict:
    img    = Image.open(image_path).convert("RGBA")
    w, h   = img.size

    # ── Visual analysis (always runs) ────────────────────────────────────────
    visual = visual_analysis(img.convert("RGB"), h)
    theme  = visual["theme"]

    # ── UI element analysis ───────────────────────────────────────────────────
    ui_data  = None
    method   = "ocr_fallback"
    if xml_path and Path(xml_path).exists():
        ui_data = parse_ui_dump(xml_path, density=density, font_scale=font_scale)
        if len(ui_data["texts"]) >= 3:
            method = "uiautomator"

    if method == "uiautomator":
        zones     = _group_by_zone(ui_data["items"], h)
        stats     = _ui_stats(ui_data["items"])
        app_name  = ui_data["app_name"]
        package   = ui_data["package"]
        all_texts = ui_data["texts"]
    else:
        zones, stats  = {}, {}
        app_name      = "Unknown (OCR fallback)"
        package       = ""
        all_texts     = ocr_fallback(img.convert("RGB"), theme)

    result = {
        "image_path":    image_path,
        "resolution":    f"{w}x{h}",
        "resolution_dp": f"{px_to_dp(w, density)}x{px_to_dp(h, density)}",
        "density":       density,
        "dpi_class":     _dpi_class(density),
        "font_scale":    font_scale,
        "method":        method,
        "app_name":      app_name,
        "package":       package,
        "all_texts":     all_texts,
        "zones":         {k: [i["text"] for i in v] for k, v in zones.items()} if zones else {},
        "zones_with_dims": {
            k: [{"text": i["text"],
                 "width_px": i.get("width_px"), "height_px": i.get("height_px"),
                 "width_dp": i.get("width_dp"), "height_dp": i.get("height_dp"),
                 "height_sp": i.get("height_sp"),
                 "x_dp": i.get("x_dp"),        "y_dp": i.get("y_dp"),
                 "clickable": i.get("clickable")}
                for i in v]
            for k, v in zones.items()
        } if zones else {},
        "ui_stats":      stats,
        "visual":        visual,
    }

    if output_json:
        return result

    # ── Human-readable combined report ───────────────────────────────────────
    SEP  = "─" * 64
    SEP2 = "┄" * 64
    out  = [
        SEP,
        "📱  ANDROID SCREEN ANALYSIS  —  COMBINED REPORT",
        SEP,
        f"  Resolution  : {w}x{h} px  →  {px_to_dp(w, density)}x{px_to_dp(h, density)} dp",
        f"  Density     : {density} dpi ({_dpi_class(density)})  |  font-scale: {font_scale}",
        f"  Scale ratio : 1 dp = {round(density/160.0, 2):.2f} px   |   1 sp = {round(density/160.0 * font_scale, 2):.2f} px",
        f"  Theme       : {theme.upper()}  {visual['zone_colors']['content']['hex']} (content bg)",
        f"  Method      : {'✅ UIAUTOMATOR + VISUAL' if method=='uiautomator' else '⚠️  OCR FALLBACK + VISUAL'}",
        f"  Package     : {package or '—'}",
        f"  Screen/App  : {app_name}",
        "",
    ]

    # ── Visual section ────────────────────────────────────────────────────────
    out += [SEP2, "🎨  VISUAL  (from screenshot pixels)", SEP2]
    zc = visual["zone_colors"]
    out += [
        f"  Status Bar   : {zc['status_bar']['hex']}",
        f"  Top Bar      : {zc['top_bar']['hex']}",
        f"  Content      : {zc['content']['hex']}",
        f"  Bottom Bar   : {zc['bottom_action_bar']['hex']}",
        f"  Nav Bar      : {zc['navigation_bar']['hex']}",
    ]
    dc = visual["dominant_colors"][:3]
    out.append(f"  Top colors   : " + "  ".join(f"{c['hex']}" for c in dc))

    # ── UI Elements section ───────────────────────────────────────────────────
    if stats:
        out += ["", SEP2, "🧩  UI ELEMENTS  (from accessibility tree)", SEP2]
        out += [
            f"  Total elements  : {stats['total_elements']}",
            f"  Clickable       : {stats['clickable']} 🔘",
            f"  Text views      : {stats['text_views']}",
            f"  Buttons         : {stats['buttons']}",
            f"  Images          : {stats['images']}",
            f"  Scrollable lists: {stats['lists']}",
            f"  Input fields    : {stats['edit_texts']}",
        ]

    # ── Zones section ─────────────────────────────────────────────────────────
    if zones:
        out += ["", SEP2, "📍  SCREEN ZONES  (position + content)", SEP2]
        for zone in ["STATUS_BAR","TOP_BAR","CONTENT","BOTTOM_ACTION_BAR","NAVIGATION_BAR"]:
            items = zones.get(zone, [])
            if not items:
                continue
            color = zc.get(zone.lower(), {}).get("hex", "")
            out.append(f"\n  [{zone}]  {color}")
            for item in items:
                mark  = " 🔘" if item["clickable"] else ""
                mark += " 📜" if item["scrollable"] else ""
                mark += " ✏️"  if item["class"] == "EditText" else ""
                out.append(f"    • {item['text']}{mark}")

    # ── Dimensions section ─────────────────────────────────────────────────────
    if zones and density > 0:
        scale = density / 160.0
        out += [
            "",
            SEP2,
            f"📐  DIMENSIONS  (px → dp  @  {density} dpi / {_dpi_class(density)}  |  font-scale {font_scale})",
            SEP2,
            f"  Screen      : {w}x{h} px  →  {px_to_dp(w, density)}x{px_to_dp(h, density)} dp",
            f"  Scale ratio : 1 dp = {scale:.2f} px   |   1 sp = {round(scale * font_scale, 2):.2f} px",
            "",
            "  ELEMENT SIZES  (🔘 = clickable  |  sp = estimated font size for text elements):",
        ]
        for zone_name in ["TOP_BAR", "CONTENT", "BOTTOM_ACTION_BAR", "NAVIGATION_BAR"]:
            zone_items = zones.get(zone_name, [])
            dim_items  = [i for i in zone_items if i.get("width_px", 0) > 0 or i.get("height_px", 0) > 0]
            if not dim_items:
                continue
            zc_hex = zc.get(zone_name.lower(), {}).get("hex", "")
            out.append(f"\n  [{zone_name}]  {zc_hex}")
            for item in dim_items[:15]:
                mark   = "🔘 " if item.get("clickable") else "   "
                label  = item["text"][:30]
                w_px_e = item.get("width_px",  0)
                h_px_e = item.get("height_px", 0)
                w_dp_e = item.get("width_dp",  0.0)
                h_dp_e = item.get("height_dp", 0.0)
                sp_str = f"  ≈{item['height_sp']}sp" if item.get("height_sp") else ""
                out.append(
                    f"    {mark}{label:<30}  {w_px_e:>5}x{h_px_e:<4}px  →  {w_dp_e:>6}x{h_dp_e:<4}dp{sp_str}"
                )

    # ── All text section ──────────────────────────────────────────────────────
    out += ["", SEP, "📝  ALL VISIBLE TEXT  (top → bottom)", SEP]
    for i, t in enumerate(all_texts, 1):
        out.append(f"  {i:>3}. {t}")
    out.append(SEP)

    result["report"] = "\n".join(out)
    return result


# ── entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Android screen analyzer with px/dp/sp dimension reporting")
    parser.add_argument("image")
    parser.add_argument("xml", nargs="?", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--density",    type=int,   default=420,
                        help="Device screen density in DPI (from 'adb shell wm density'). Default: 420")
    parser.add_argument("--font-scale", type=float, default=1.0,
                        help="System font scale factor (from 'adb shell settings get system font_scale'). Default: 1.0")
    args = parser.parse_args()

    if not Path(args.image).exists():
        print(f"❌ File not found: {args.image}", file=sys.stderr); sys.exit(1)

    r = analyze(args.image, args.xml, args.json,
                density=args.density, font_scale=args.font_scale)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(r.get("report", ""))
        print(f"\nSCREENSHOT_PATH={os.path.abspath(args.image)}")
