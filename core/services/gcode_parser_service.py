"""
Servicio de parsing de archivos G-code y 3MF.
Extrae tiempo, peso, longitud filamento, tipo material, impresora, color y thumbnail.
Compatible con slicers: PrusaSlicer, Cura, OrcaSlicer, BambuStudio, SuperSlicer, IdeaMaker, Simplify3D, Creality Print.
"""

import re
import struct
import zipfile
import zlib
import json
import math
import base64
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List

from PySide6.QtGui import QImage

from core.utils.logger import logger


# ─────────────────────────────────────────────
# Mapa de IDs comprimidos de PrusaSlicer → nombre legible
# PrusaSlicer concatena palabras sin espacios en el campo printer_model
# Ej: COREONEL → CORE One L,  MK4S → MK4S (ya legible)
# ─────────────────────────────────────────────
PRUSA_MODEL_ID_MAP: dict[str, str] = {
    # CORE One
    "COREONE":      "CORE One",
    "COREONEHF":    "CORE One HF",
    "COREONEMMU3":  "CORE One",       # CORE One con MMU3 (sin L)
    "COREONEOAK":   "CORE One",       # CORE One variante OAK
    "COREONEL":     "CORE One L",
    "COREONELHF":   "CORE One L HF",
    # MK series
    "MK35":       "MK3.5",
    "MK3S":       "MK3S",
    "MK4":        "MK4",
    "MK4S":       "MK4S",
    "MK4SHF":     "MK4S HF",
    # XL
    "XL":         "XL",
    "XL5T":       "XL 5T",
    # MINI
    "MINI":       "MINI",
    "MINIIS":     "MINI IS",
}

# ─────────────────────────────────────────────
# Tabla de normalización: OrcaSlicer/Slicer → Voxeprint FilamentType
# ─────────────────────────────────────────────
FILAMENT_NORMALIZATION_RULES = [
    # ── Carbon Fiber composites (específicos primero) ──
    (r'PLA[\s-]*CF|PLA[\s-]*Carbon', 'PLA-CF', 'PLA con fibra de carbono'),
    (r'PETG[\s-]*CF|PETG[\s-]*Carbon', 'PETG-CF', 'PETG con fibra de carbono'),
    (r'PET[\s-]*CF', 'PETG-CF', 'PET con fibra de carbono'),
    (r'ASA[\s-]*CF', 'ASA-CF', 'ASA con fibra de carbono'),
    (r'PA[\s-]*CF|PA\d+[\s-]*CF|PAHT[\s-]*CF|PPA[\s-]*CF', 'Nylon CF', 'Nylon con fibra de carbono'),
    (r'PP[\s-]*CF', 'PP-CF', 'PP con fibra de carbono'),
    (r'PE[\s-]*CF', 'CARBON_FIBER', 'PE con fibra de carbono'),
    (r'PPS[\s-]*CF', 'CARBON_FIBER', 'PPS con fibra de carbono'),
    (r'HT[\s-]*PLA[\s-]*GF', 'PLA Pro', 'PLA HT con fibra de vidrio'),

    # ── Glass Fiber composites ──
    (r'ABS[\s-]*GF', 'ABS-GF', 'ABS con fibra de vidrio'),
    (r'PA\d*[\s-]*GF|PPA[\s-]*GF', 'PA-GF', 'Nylon con fibra de vidrio'),
    (r'PP[\s-]*GF', 'PP', 'PP con fibra de vidrio'),

    # ── PLA variants (específicos antes que genérico) ──
    (r'PLA[\s+]*\+|PLA[\s]*Plus|PLA[\s]*PLUS', 'PLA+', 'PLA Plus'),
    (r'PLA[\s-]*Pro|HT[\s-]*PLA', 'PLA Pro', 'PLA Pro / Alta temperatura'),
    (r'PLA[\s-]*Silk', 'PLA Silk', 'PLA Silk'),
    (r'PLA[\s-]*Matte', 'PLA Matte', 'PLA Matte'),
    (r'PLA[\s-]*High[\s-]*Speed', 'PLA High Speed', 'PLA alta velocidad'),
    (r'PLA[\s-]*Wood|Wood[\s-]*PLA', 'WOOD', 'PLA con madera'),
    (r'PLA[\s-]*Metal', 'METAL', 'PLA con partículas metálicas'),
    (r'PLA[\s-]*(Galaxy|Glow|Sparkle|Marble|Aero|Dynamic|Lite|Tough|Translucent|Luminous|Celestial|Neon|Satin|Starlight|Metallic|UV|Temp)', 'PLA', 'PLA variante especial'),

    # ── PETG variants ──
    (r'PETG[\s-]*(?:ESD|rCF)', 'PETG', 'PETG especial'),
    (r'PETG[\s-]*(?:Basic|HF|Translucent)', 'PETG', 'PETG variante'),
    (r'PCTG', 'PCTG', 'PCTG copoliéster'),

    # ── Nylon / PA variants (sin CF/GF) ──
    (r'PA\d{1,3}|PAHT|PPA', 'NYLON', 'Nylon variante'),
    (r'NYLEX', 'NYLON', 'Nylon (NYLEX)'),

    # ── PC variants ──
    (r'PC[\s-]*ABS', 'PC-ABS', 'PC-ABS blend'),
    (r'PC[\s-]*FR', 'PC', 'PC retardante de fuego'),

    # ── TPU variants ──
    (r'TPU[\s-]*\d+[A-Za-z]*|TPU[\s-]*(?:HF|AMS|for)', 'TPU', 'TPU variante'),

    # ── TPE variants ──
    (r'TPE[\s-]*\d+[A-Za-z]*', 'TPE', 'TPE variante'),

    # ── ASA variants (sin CF) ──
    (r'ASA[\s-]*Aero', 'ASA', 'ASA Aero'),

    # ── Soporte ──
    (r'BVOH', 'BVOH', 'Material de soporte BVOH'),
    (r'Support\s+(?:W|G|for)', 'PVA', 'Material de soporte'),

    # ── Materiales específicos ──
    (r'\bSBS\b', 'SBS', 'SBS'),
    (r'\bEVA\b', 'EVA', 'EVA'),
    (r'CoPE', 'FLEX', 'CoPE (copoliéster)'),
    (r'\bPPS\b(?![\s-]*CF)', 'PPS', 'PPS alta temperatura'),
    (r'\bPHA\b', 'PHA', 'PHA biodegradable'),
    (r'\bPE\b(?![TG])', 'PE', 'PE polietileno'),

    # ── Genéricos (match exacto, al final) ──
    (r'\bPLA\b', 'PLA', 'PLA genérico'),
    (r'\bABS\b', 'ABS', 'ABS genérico'),
    (r'\bPETG\b', 'PETG', 'PETG genérico'),
    (r'\bPET\b', 'PET', 'PET genérico'),
    (r'\bASA\b', 'ASA', 'ASA genérico'),
    (r'\bTPU\b', 'TPU', 'TPU genérico'),
    (r'\bTPE\b', 'TPE', 'TPE genérico'),
    (r'\bPA\b|\bNylon\b', 'NYLON', 'Nylon genérico'),
    (r'\bPC\b', 'PC', 'PC genérico'),
    (r'\bPP\b', 'PP', 'PP genérico'),
    (r'\bPVA\b', 'PVA', 'PVA genérico'),
    (r'\bHIPS\b', 'HIPS', 'HIPS genérico'),
    (r'\bPMMA\b', 'PMMA', 'PMMA genérico'),
    (r'\bPOM\b', 'POM', 'POM genérico'),
    (r'\bPEEK\b', 'PEEK', 'PEEK genérico'),
    (r'\bULTEM\b', 'ULTEM', 'ULTEM genérico'),
]

# Tipos de filamento conocidos de Voxeprint
VOXEPRINT_FILAMENT_TYPES = [
    "PLA", "PLA+", "PLA Pro", "PLA Silk", "PLA Matte", "PLA High Speed", "PLA-CF",
    "ABS", "ABS-GF",
    "PETG", "PETG-CF", "PCTG",
    "ASA", "ASA-CF",
    "TPU", "TPE", "FLEX", "SBS", "EVA",
    "WOOD", "METAL", "CARBON_FIBER",
    "NYLON", "Nylon CF", "PA-GF",
    "PC", "PC-ABS",
    "PP", "PP-CF",
    "PVA", "BVOH", "HIPS",
    "PET", "PPS", "PE", "PHA", "PMMA", "POM", "PEEK", "ULTEM",
    "OTHER"
]


# Densidades estándar por tipo de filamento (g/cm³)
# Valores de perfiles Creality Print + estándares industriales
_FILAMENT_DENSITY_MAP = {
    'PLA': 1.24, 'PLA+': 1.24, 'PLA PRO': 1.24, 'PLA SILK': 1.24,
    'PLA MATTE': 1.24, 'PLA HIGH SPEED': 1.24, 'PVB': 1.24,
    'PLA-CF': 1.04,
    'ABS': 1.04, 'ABS-GF': 1.04,
    'ASA': 1.04, 'ASA-CF': 1.04,
    'PC': 1.04, 'PC-CF': 1.04, 'PC-ABS': 1.04,
    'PETG': 1.27, 'PETG-CF': 1.27, 'PCTG': 1.27,
    'TPU': 1.21, 'TPE': 1.21, 'FLEX': 1.21, 'SBS': 1.05,
    'NYLON': 1.14, 'PA': 1.14, 'NYLON CF': 1.14, 'PA-GF': 1.14,
    'HIPS': 1.04,
    'PVA': 1.23, 'BVOH': 1.23,
    'PP': 0.90, 'PP-CF': 0.90,
    'WOOD': 1.28,
}
_DEFAULT_DENSITY = 1.24  # PLA como fallback genérico

# ─────────────────────────────────────────────
# Dataclasses
# ─────────────────────────────────────────────
@dataclass
class ThumbnailInfo:
    """Un thumbnail individual con sus metadatos."""
    data: bytes = field(default=b"", repr=False)
    format: str = ""       # png, jpg
    width: int = 0
    height: int = 0
    source: str = ""       # "gcode_base64", "3mf_file", etc.
    file_name: str = ""    # nombre dentro del zip (para 3mf)

    @property
    def pixels(self) -> int:
        return self.width * self.height

    @property
    def size_kb(self) -> float:
        return len(self.data) / 1024

    @property
    def label(self) -> str:
        quality = "HD" if self.width >= 400 or self.height >= 400 else (
            "Media" if self.width >= 200 or self.height >= 200 else "Baja"
        )
        return f"{self.width}×{self.height} px  •  {self.format.upper()}  •  {self.size_kb:.1f} KB  •  [{quality}]"

    @property
    def pdf_suitable(self) -> bool:
        return self.width >= 200 and self.height >= 200


@dataclass
class FilamentSlotData:
    """Datos de un slot de filamento extraídos del G-code multicolor."""
    slot_index: int = 0
    filament_type: str = ""        # tipo normalizado (PLA, ASA, etc.)
    colour_hex: str = ""           # color HEX del slot (#RRGGBB)
    weight_grams: float = 0.0      # gramos usados por este slot
    percentage: float = 0.0        # % respecto al total (0-100)
    # Campos asignados en runtime por el presenter (no se persisten en BD)
    filament_id: int = 0           # ID del filamento asignado del catálogo
    price_per_gram: float = 0.0    # precio/gramo del filamento asignado
    slot_cost: float = 0.0         # costo calculado de este slot


@dataclass
class GcodeData:
    print_time_hours: float = 0.0
    filament_weight_grams: float = 0.0
    filament_length_mm: float = 0.0
    printer_model: str = ""
    filament_colour: str = ""
    filament_type: str = ""  # PLA, PETG, ABS, etc.
    thumbnail: bytes = field(default=b"", repr=False)
    thumbnail_format: str = ""  # png, jpg
    all_thumbnails: List[ThumbnailInfo] = field(default_factory=list)
    file_name: str = ""
    slicer: str = ""
    layer_height: float = 0.0
    nozzle_diameter: float = 0.0
    bed_temperature: float = 0.0
    hotend_temperature: float = 0.0
    fill_density: float = 0.0
    surface_area_mm2: float = 0.0
    raw_comments: str = ""
    # Campos de normalización
    normalized_type: str = ""
    normalization_rule: str = ""
    normalization_confidence: str = ""
    # Campos multicolor (poblados cuando hay más de un slot activo)
    is_multicolor: bool = False
    filament_slots: List['FilamentSlotData'] = field(default_factory=list)
    multifilament_system: str = ""  # Sistema multifilamento detectado (MMU3, MMU2, AMS, etc.)


# ─────────────────────────────────────────────
# Normalización de filamento
# ─────────────────────────────────────────────
def normalize_filament_type(raw_type: str) -> tuple:
    """
    Normaliza un string de tipo de filamento del G-code/slicer
    al FilamentType de Voxeprint.

    Retorna: (voxeprint_type, rule_description, confidence)
    """
    if not raw_type:
        return ('OTHER', 'Sin tipo de material', 'baja')

    cleaned = raw_type.strip()
    # Quitar prefijos de marca comunes
    brand_prefixes = [
        r'^(?:Creality|Bambu|BambuLab|Generic|eSUN|SUNLU|Overture|Polymaker|'
        r'PolyLite|PolyTerra|Panchroma|Fiberon|Numakers|COEX|AliZ|FusRock|'
        r'Inland|Hatchbox|Prusament|Prusa|Eryone|JAYO|Elegoo|Anycubic|'
        r'FlashForge|Qidi|Kingroon|Geeetech|Voxelab|Phrozen|Anker|'
        r'CR|Hyper)'
        r'[\s-]*',
    ]
    for prefix_pattern in brand_prefixes:
        cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE).strip()

    # Quitar sufijos de impresora
    cleaned = re.sub(r'\s*@.*$', '', cleaned).strip()
    cleaned = cleaned.strip('"\'')

    for pattern, voxeprint_type, description in FILAMENT_NORMALIZATION_RULES:
        if re.search(pattern, cleaned, re.IGNORECASE):
            if cleaned.upper() == voxeprint_type.upper():
                confidence = 'alta'
            elif len(cleaned) < 15:
                confidence = 'alta'
            else:
                confidence = 'media'
            return (voxeprint_type, description, confidence)

    for vtype in VOXEPRINT_FILAMENT_TYPES:
        if cleaned.upper() == vtype.upper():
            return (vtype, 'Coincidencia directa', 'alta')

    return ('OTHER', f'No reconocido: "{cleaned}"', 'baja')


# ─────────────────────────────────────────────
# Parser de G-code (.gcode)
# ─────────────────────────────────────────────
_HEADER_LINES = 3000
_FOOTER_LINES = 3000


def _get_headers(content: str) -> tuple[str, str]:
    """Extrae el encabezado Y el pie del G-code.
    Algunos slicers (PrusaSlicer MMU2, etc.) ponen la metadata al FINAL del archivo.
    """
    # Header: primeras N líneas
    header = content
    newline_pos = -1
    for _ in range(_HEADER_LINES):
        newline_pos = content.find('\n', newline_pos + 1)
        if newline_pos == -1:
            break
    if newline_pos != -1:
        header = content[:newline_pos]

    # Footer: últimas N líneas
    footer = content
    newline_pos = len(content)
    for _ in range(_FOOTER_LINES):
        newline_pos = content.rfind('\n', 0, newline_pos)
        if newline_pos == -1:
            break
    if newline_pos != -1:
        footer = content[newline_pos + 1:]

    return header, footer


def parse_gcode(content: str) -> GcodeData:
    data = GcodeData()
    header, footer = _get_headers(content)
    # Buscar en header U footer (footer: necesario para MMU2/Prusa que pone metadata al final)
    search_text = f"{header}\n{footer}"

    # Recopilar primeras líneas de comentario para debug
    comment_lines = []
    for line in header.split('\n')[:200]:
        stripped = line.strip()
        if stripped.startswith(';'):
            comment_lines.append(stripped)
    data.raw_comments = '\n'.join(comment_lines[:80])

    # ── Detección de slicer ──
    slicer_patterns = [
        (r';\s*generated by PrusaSlicer', 'PrusaSlicer'),
        (r';\s*Generated by OrcaSlicer', 'OrcaSlicer'),
        (r';\s*generated by Creality_Print', 'Creality Print'),
        (r';\s*Creality Print', 'Creality Print'),
        (r';Generated with Cura', 'Cura'),
        (r';\s*SuperSlicer', 'SuperSlicer'),
        (r';\s*Simplify3D', 'Simplify3D'),
        (r';\s*generated by ideaMaker', 'IdeaMaker'),
        (r';\s*BambuStudio', 'BambuStudio'),
        (r';\s*AnkerMake', 'AnkerMake Slicer'),
        (r';\s*FlashPrint', 'FlashPrint'),
    ]
    for pattern, name in slicer_patterns:
        if re.search(pattern, search_text, re.IGNORECASE):
            data.slicer = name
            break

    # ── Peso del filamento (gramos) ──
    # Caso multicolor OrcaSlicer/Creality/PrusaSlicer: "filament used [g] = v1, v2, v3, ..."
    _slot_g_vals: List[float] = []
    multicolor_g_match = re.search(
        r';\s*filament used \[g\]\s*=\s*([\d.,\s]+)', search_text, re.IGNORECASE
    )
    if multicolor_g_match:
        raw_g = multicolor_g_match.group(1)
        _slot_g_vals = [float(v.strip()) for v in raw_g.split(',') if v.strip()]
        total_g = sum(_slot_g_vals)
        if total_g > 0:
            data.filament_weight_grams = total_g

    # Caso multicolor BambuStudio: "; total filament weight [g] : 125.01,78.77,..."
    if not _slot_g_vals:
        bambu_weight_m = re.search(
            r';\s*total filament weight \[g\]\s*:\s*([\d.,\s]+)', search_text, re.IGNORECASE
        )
        if bambu_weight_m:
            vals = [float(v.strip()) for v in bambu_weight_m.group(1).split(',') if v.strip()]
            if vals:
                _slot_g_vals = vals
                data.filament_weight_grams = round(sum(vals), 1)

    # Si no se encontró o fue 0, intentar patrones de valor único
    if data.filament_weight_grams == 0:
        weight_patterns = [
            r'total filament weight\s*\[g\]\s*[:=]\s*([\d.]+)',
            r'total filament used\s*\[g\]\s*[:=]\s*([\d.]+)',
            r'total filament used\s*[:=]\s*([\d.]+)\s*g',
            r'filament used\s*[:=]\s*([\d.]+)\s*g',
            r';\s*total\s*filament\s*weight\s*=\s*([\d.]+)',
            r';\s*filament_weight\s*[:=]\s*([\d.]+)',
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                if val > 0:
                    data.filament_weight_grams = val
                    break

    # Caso Cura Cheetah (Ultimaker): EXTRUDER_TRAIN.N.MATERIAL.VOLUME_USED en mm³ → gramos
    if data.filament_weight_grams == 0:
        vol_matches = re.findall(
            r'^;EXTRUDER_TRAIN\.\d+\.MATERIAL\.VOLUME_USED:(\d+)', search_text, re.MULTILINE
        )
        if vol_matches:
            total_vol_mm3 = sum(int(v) for v in vol_matches)
            data.filament_weight_grams = round(total_vol_mm3 / 1000 * _DEFAULT_DENSITY, 1)

    # ── Longitud del filamento ──
    # Caso multicolor OrcaSlicer/PrusaSlicer: "filament used [mm] = v1, v2, v3, ..."
    multicolor_mm_match = re.search(
        r';\s*filament used \[mm\]\s*=\s*([\d.,\s]+)', search_text, re.IGNORECASE
    )
    if multicolor_mm_match:
        raw_vals = multicolor_mm_match.group(1)
        vals = [float(v.strip()) for v in raw_vals.split(',') if v.strip()]
        if vals:
            data.filament_length_mm = sum(vals)
    else:
        # BambuStudio: "; total filament length [mm] : 47681.28,31491.02,..."
        bambu_mm_m = re.search(
            r';\s*total filament length \[mm\]\s*:\s*([\d.,\s]+)', search_text, re.IGNORECASE
        )
        if bambu_mm_m:
            vals = [float(v.strip()) for v in bambu_mm_m.group(1).split(',') if v.strip()]
            if vals:
                data.filament_length_mm = round(sum(vals), 1)
        else:
            length_patterns = [
                (r'filament\s*used\s*[:=]\s*([\d.]+)\s*m(?!m)', 'meters'),
                (r'filament\s*used\s*[:=]\s*([\d.]+)\s*mm', 'mm'),
                (r';\s*filament_used_mm\s*[:=]\s*([\d.]+)', 'mm'),
                (r';\s*Filament length\s*[:=]\s*([\d.]+)\s*mm', 'mm'),
                (r';\s*Filament length\s*[:=]\s*([\d.]+)\s*m(?!m)', 'meters'),
                (r'^;Filament used:\s*([\d.]+)\s*m$', 'meters'),
            ]
            for pattern, unit in length_patterns:
                match = re.search(pattern, search_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = float(match.group(1))
                    data.filament_length_mm = value * 1000 if unit == 'meters' else value
                    break

    # Caso Cura Cheetah (Ultimaker): derivar longitud desde VOLUME_USED (mm³) con filamento 1.75 mm
    if data.filament_length_mm == 0:
        vol_matches = re.findall(
            r'^;EXTRUDER_TRAIN\.\d+\.MATERIAL\.VOLUME_USED:(\d+)', search_text, re.MULTILINE
        )
        if vol_matches:
            total_vol_mm3 = sum(int(v) for v in vol_matches)
            data.filament_length_mm = round(total_vol_mm3 / (math.pi * 0.875 ** 2), 1)

    # ── Tiempo de impresión ──
    time_string = None
    time_patterns = [
        r';\s*total estimated time:\s*(.+)',  # BambuStudio: "; total estimated time: 1d 11h 54m 13s"
        r'estimated printing time\s*(?:\(normal mode\))?\s*[:=]\s*(.+)',
        r'estimated time\s*[:=]\s*(.+)',
        r';\s*TIME:\s*(\d+)',
        r'print time\s*[:=]\s*(.+)',
        r';\s*estimated_time\s*[:=]\s*(\d+)',
        r';\s*Build time\s*[:=]\s*(.+)',
        r';\s*Time\s*[:=]\s*(.+)',
        r';\s*print_time\s*[:=]\s*(\d+)',
        r'^;TIME:(\d+)$',
        r';\s*PRINT\.TIME:(\d+)',  # Cura Cheetah (Ultimaker): ";PRINT.TIME:5579"
    ]
    for pattern in time_patterns:
        match = re.search(pattern, search_text, re.IGNORECASE | re.MULTILINE)
        if match:
            time_string = match.group(1).strip()
            break

    if time_string:
        if re.match(r'^\d+$', time_string):
            data.print_time_hours = int(time_string) / 3600
        else:
            d = re.search(r'(\d+)\s*d', time_string, re.IGNORECASE)
            h = re.search(r'(\d+)\s*h', time_string, re.IGNORECASE)
            m = re.search(r'(\d+)\s*m(?!s)', time_string, re.IGNORECASE)
            s = re.search(r'(\d+)\s*s', time_string, re.IGNORECASE)
            data.print_time_hours = (
                (float(d.group(1)) * 24 if d else 0) +
                (float(h.group(1)) if h else 0) +
                (float(m.group(1)) / 60 if m else 0) +
                (float(s.group(1)) / 3600 if s else 0)
            )

    # Caso multicolor OrcaSlicer/PrusaSlicer: "filament used [cm3] = v1, v2, v3, ..."
    # Usar cm³ × densidad por slot cuando total [g] = 0 (densidad no configurada en slicer)
    if data.filament_weight_grams == 0:
        multicolor_cm3_match = re.search(
            r';\s*filament used \[cm3\]\s*=\s*([\d.,\s]+)', search_text, re.IGNORECASE
        )
        if multicolor_cm3_match:
            raw_cm3 = multicolor_cm3_match.group(1)
            cm3_vals = [float(v.strip()) for v in raw_cm3.split(',') if v.strip()]
            if cm3_vals:
                # 1) Densidades reales del gcode por slot (Creality: "; filament_density: X,X,...")
                slot_densities = []
                density_m = re.search(
                    r';\s*filament_density\s*[:=]\s*([\d.,\s]+)', search_text, re.IGNORECASE
                )
                if density_m:
                    slot_densities = [
                        float(v.strip()) for v in density_m.group(1).split(',') if v.strip()
                    ]
                # 2) Tipos de filamento por slot (OrcaSlicer/Creality: "; filament_type = PLA;ASA;...")
                slot_types = []
                type_m = re.search(
                    r';\s*filament_type\s*[:=]\s*(.+)', search_text, re.IGNORECASE
                )
                if type_m:
                    raw_types = type_m.group(1).strip().rstrip(';')
                    slot_types = [t.strip().upper() for t in raw_types.split(';') if t.strip()]
                # 3) Calcular peso: densidad gcode > tabla por tipo > default 1.24
                total_weight = 0.0
                for i, cm3 in enumerate(cm3_vals):
                    if i < len(slot_densities) and slot_densities[i] > 0:
                        dens = slot_densities[i]
                    elif i < len(slot_types) and slot_types[i] in _FILAMENT_DENSITY_MAP:
                        dens = _FILAMENT_DENSITY_MAP[slot_types[i]]
                    else:
                        dens = _DEFAULT_DENSITY
                    total_weight += cm3 * dens
                data.filament_weight_grams = round(total_weight, 2)

    # Si aún no hay peso, estimar desde longitud (PLA 1.75mm: ~0.00298 g/mm)
    if data.filament_length_mm > 0 and data.filament_weight_grams == 0:
        data.filament_weight_grams = data.filament_length_mm * 0.00298

    # ── Multicolor: construir slots si hay más de uno ──
    _raw_types_m = re.search(r';\s*filament_type\s*[:=]\s*(.+)', search_text, re.IGNORECASE)
    _raw_colours_m = re.search(
        r';\s*(?:filament_colour|filament_color|extruder_colour|extruder_color)\s*[:=]\s*(.+)',
        header, re.IGNORECASE
    )
    _slot_types: List[str] = []
    _slot_colours: List[str] = []
    if _raw_types_m:
        _slot_types = [
            t.strip().upper() for t in _raw_types_m.group(1).strip().rstrip(';').split(';')
            if t.strip()
        ]
    if _raw_colours_m:
        _slot_colours = [
            c.strip() for c in _raw_colours_m.group(1).strip().split(';')
            if c.strip()
        ]

    # Si no tenemos gramos por slot desde el header, pero sí cm3, derivarlos
    if not _slot_g_vals:
        _cm3_m = re.search(
            r';\s*filament used \[cm3\]\s*=\s*([\d.,\s]+)', search_text, re.IGNORECASE
        )
        if _cm3_m:
            cm3_vals = [float(v.strip()) for v in _cm3_m.group(1).split(',') if v.strip()]
            _dens_m = re.search(r';\s*filament_density\s*[:=]\s*([\d.,\s]+)', search_text, re.IGNORECASE)
            slot_densities_build = (
                [float(v.strip()) for v in _dens_m.group(1).split(',') if v.strip()]
                if _dens_m else []
            )
            for i, cm3 in enumerate(cm3_vals):
                if i < len(slot_densities_build) and slot_densities_build[i] > 0:
                    dens = slot_densities_build[i]
                elif i < len(_slot_types) and _slot_types[i] in _FILAMENT_DENSITY_MAP:
                    dens = _FILAMENT_DENSITY_MAP[_slot_types[i]]
                else:
                    dens = _DEFAULT_DENSITY
                _slot_g_vals.append(round(cm3 * dens, 2))

    if len(_slot_g_vals) > 1 and data.filament_weight_grams > 0:
        total_g_slots = sum(_slot_g_vals)
        data.is_multicolor = True
        for i, g in enumerate(_slot_g_vals):
            slot_type = _slot_types[i] if i < len(_slot_types) else ""
            slot_colour = _slot_colours[i] if i < len(_slot_colours) else ""
            norm_type, _, _ = normalize_filament_type(slot_type)
            slot = FilamentSlotData(
                slot_index=i,
                filament_type=norm_type,
                colour_hex=slot_colour,
                weight_grams=round(g, 2),
                percentage=round((g / total_g_slots * 100), 4) if total_g_slots > 0 else 0.0,
            )
            data.filament_slots.append(slot)

    # ── Modelo de impresora ──
    printer_patterns = [
        r';\s*printer_model\s*[:=]\s*(.+)',
        r';\s*machine_model\s*[:=]\s*(.+)',
        r';\s*printer_type\s*[:=]\s*(.+)',
        r';\s*printer\s*[:=]\s*(.+)',
        r';\s*machine\s*[:=]\s*(.+)',
        r';\s*device\s*[:=]\s*(.+)',
        r';\s*TARGET_MACHINE\.NAME:\s*(.+)',
    ]
    for pattern in printer_patterns:
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            data.printer_model = match.group(1).strip()
            break

    # ── Color del filamento ──
    colour_patterns = [
        r';\s*filament_colour\s*[:=]\s*(.+)',
        r';\s*filament_color\s*[:=]\s*(.+)',
        r';\s*extruder_colour\s*[:=]\s*(.+)',
        r';\s*extruder_color\s*[:=]\s*(.+)',
    ]
    for pattern in colour_patterns:
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            data.filament_colour = match.group(1).strip()
            break

    # ── Tipo de material ──
    material_patterns = [
        r';\s*filament_settings_id\s*[:=]\s*(.+)',
        r';\s*filament_type\s*[:=]\s*(.+)',
        r';\s*material_type\s*[:=]\s*(.+)',
        r';\s*material_name\s*[:=]\s*(.+)',
        r';\s*MATERIAL\s*[:=]\s*(.+)',
    ]
    for pattern in material_patterns:
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            data.filament_type = match.group(1).strip()
            break

    # ── Parámetros adicionales ──
    lh_match = re.search(r';\s*layer_height\s*[:=]\s*([\d.]+)', search_text, re.IGNORECASE)
    if lh_match:
        data.layer_height = float(lh_match.group(1))

    nz_match = re.search(r';\s*nozzle_diameter\s*[:=]\s*([\d.]+)', search_text, re.IGNORECASE)
    if nz_match:
        data.nozzle_diameter = float(nz_match.group(1))

    bed_match = re.search(r';\s*(?:bed_temperature|first_layer_bed_temperature)\s*[:=]\s*([\d.]+)', search_text, re.IGNORECASE)
    if bed_match:
        data.bed_temperature = float(bed_match.group(1))
    # Fallback: extraer de comando M190 (Cura)
    if data.bed_temperature == 0:
        m190_match = re.search(r'M190\s+S([\d.]+)', search_text, re.IGNORECASE)
        if m190_match:
            data.bed_temperature = float(m190_match.group(1))

    hotend_match = re.search(r';\s*(?:temperature|first_layer_temperature|nozzle_temperature)\s*[:=]\s*([\d.]+)', search_text, re.IGNORECASE)
    if hotend_match:
        data.hotend_temperature = float(hotend_match.group(1))
    # Fallback: extraer de comando M109 (Cura)
    if data.hotend_temperature == 0:
        m109_match = re.search(r'M109\s+S([\d.]+)', search_text, re.IGNORECASE)
        if m109_match:
            data.hotend_temperature = float(m109_match.group(1))

    fill_match = re.search(r';\s*(?:fill_density|infill_sparse_density)\s*[:=]\s*([\d.]+)', search_text, re.IGNORECASE)
    if fill_match:
        data.fill_density = float(fill_match.group(1))

    # ── Thumbnails (Base64) — extraer TODOS (solo esto necesita el contenido completo) ──
    thumb_regex = re.compile(
        r';\s*thumbnail(?:_JPG)?\s+begin\s+(\d+)[xX](\d+)\s+(\d+)',
        re.IGNORECASE
    )

    for match in thumb_regex.finditer(content):
        w = int(match.group(1))
        h = int(match.group(2))
        fmt = 'jpg' if 'jpg' in match.group(0).lower() else 'png'

        try:
            block_start = content.index('\n', match.end()) + 1
            end_match = re.search(
                r';\s*thumbnail(?:_JPG)?\s+end',
                content[block_start:block_start + 200000],
                re.IGNORECASE
            )
            if end_match:
                raw_block = content[block_start:block_start + end_match.start()]
                base64_lines = []
                for line in raw_block.split('\n'):
                    cleaned = re.sub(r'^[\s]*;[\s]*', '', line).strip()
                    if cleaned:
                        base64_lines.append(cleaned)
                base64_data = ''.join(base64_lines)
                if len(base64_data) > 50:
                    thumb_bytes = base64.b64decode(base64_data)
                    real_w, real_h = w, h
                    try:
                        img = QImage()
                        img.loadFromData(thumb_bytes)
                        if not img.isNull():
                            real_w, real_h = img.width(), img.height()
                    except Exception:
                        pass
                    info = ThumbnailInfo(
                        data=thumb_bytes, format=fmt,
                        width=real_w, height=real_h,
                        source="gcode_base64"
                    )
                    data.all_thumbnails.append(info)
        except (ValueError, Exception):
            pass

    # Ordenar por resolución descendente y elegir el mejor
    if data.all_thumbnails:
        data.all_thumbnails.sort(key=lambda t: t.pixels, reverse=True)
        best = data.all_thumbnails[0]
        data.thumbnail = best.data
        data.thumbnail_format = best.format

    # Redondeos
    data.print_time_hours = round(data.print_time_hours, 2)
    data.filament_weight_grams = round(data.filament_weight_grams, 1)
    data.filament_length_mm = round(data.filament_length_mm, 1)
    data.surface_area_mm2 = round(data.surface_area_mm2, 2)

    return data


# ─────────────────────────────────────────────
# Parser de BGcode (.bgcode) — formato binario PrusaSlicer 2.7+
# ─────────────────────────────────────────────
# Referencia: https://github.com/prusa3d/libbgcode
# Estructura por bloque: header(8) + params(2-6) + content(uncomp_size) + CRC32(4)
# Cuando compress != None: header(12) + params + compressed_content(comp_size) + CRC32(4)

_BGCODE_MAGIC = b'GCDE'
_BGCODE_META_TYPES = {0, 2, 3, 4}   # FileMetadata, SlicerMetadata, PrinterMetadata, PrintMetadata
_BGCODE_GCODE_TYPE = 1
_BGCODE_THUMB_TYPE = 5
_BGCODE_CHECKSUM_SIZE = 4            # CRC32
_BGCODE_META_PARAMS_SIZE = 2         # EMetadataEncoding (uint16)
_BGCODE_THUMB_PARAMS_SIZE = 6        # width(2) + height(2) + format(2)


def _bgcode_decompress(data: bytes, compress_type: int) -> bytes:
    """Descomprime un bloque BGcode (deflate). Heatshrink no soportado."""
    if compress_type == 0:
        return data
    if compress_type == 1:  # deflate (raw)
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            try:
                return zlib.decompress(data)
            except zlib.error:
                return b''
    return b''  # heatshrink: skip


def parse_bgcode(file_path: str) -> GcodeData:
    """Parser para archivos BGcode de PrusaSlicer 2.7+ (formato binario)."""
    data = GcodeData()
    data.file_name = Path(file_path).name
    data.slicer = 'PrusaSlicer'

    try:
        with open(file_path, 'rb') as f:
            raw = f.read()

        if len(raw) < 10 or raw[:4] != _BGCODE_MAGIC:
            return data

        # File header: magic(4) + version(4) + checksum_type(2) = 10 bytes
        offset = 10
        meta_lines: list = []

        while offset + 8 <= len(raw):
            block_type    = struct.unpack_from('<H', raw, offset)[0]
            compress_type = struct.unpack_from('<H', raw, offset + 2)[0]
            uncomp_size   = struct.unpack_from('<I', raw, offset + 4)[0]
            offset += 8

            if compress_type != 0:
                if offset + 4 > len(raw):
                    break
                comp_size = struct.unpack_from('<I', raw, offset)[0]
                offset += 4
            else:
                comp_size = uncomp_size

            # Determinar tamaño del prefijo de params según tipo de bloque
            if block_type == _BGCODE_THUMB_TYPE:
                params_size = _BGCODE_THUMB_PARAMS_SIZE
            else:
                params_size = _BGCODE_META_PARAMS_SIZE

            # Leer params (siempre sin comprimir)
            if offset + params_size > len(raw):
                break
            params_data = raw[offset:offset + params_size]
            offset += params_size

            # Leer contenido del bloque
            if offset + comp_size > len(raw):
                break
            block_raw = raw[offset:offset + comp_size]
            offset += comp_size + _BGCODE_CHECKSUM_SIZE

            # Procesar según tipo
            if block_type in _BGCODE_META_TYPES:
                block_data = _bgcode_decompress(block_raw, compress_type)
                if block_data:
                    text = block_data.decode('utf-8', errors='replace')
                    for line in text.splitlines():
                        line = line.strip()
                        if line and '=' in line:
                            meta_lines.append(f'; {line}')

            elif block_type == _BGCODE_THUMB_TYPE:
                # params_data: width(2) + height(2) + format(2)
                if len(params_data) >= 6:
                    w      = struct.unpack_from('<H', params_data, 0)[0]
                    h      = struct.unpack_from('<H', params_data, 2)[0]
                    fmt_id = struct.unpack_from('<H', params_data, 4)[0]
                    thumb_bytes = _bgcode_decompress(block_raw, compress_type)
                    if thumb_bytes:
                        fmt = 'jpg' if fmt_id == 1 else 'png'
                        info = ThumbnailInfo(
                            data=thumb_bytes, format=fmt,
                            width=w, height=h, source='bgcode'
                        )
                        data.all_thumbnails.append(info)

        # Parsear metadata como comentarios G-code
        if meta_lines:
            meta_gcode = '; generated by PrusaSlicer\n' + '\n'.join(meta_lines)
            parsed = parse_gcode(meta_gcode)
            data.print_time_hours       = parsed.print_time_hours
            data.filament_weight_grams  = parsed.filament_weight_grams
            data.filament_length_mm     = parsed.filament_length_mm
            data.printer_model          = parsed.printer_model
            data.filament_type          = parsed.filament_type
            data.filament_colour        = parsed.filament_colour
            data.bed_temperature        = parsed.bed_temperature
            data.hotend_temperature     = parsed.hotend_temperature
            data.layer_height           = parsed.layer_height
            data.nozzle_diameter        = parsed.nozzle_diameter
            data.fill_density           = parsed.fill_density
            data.is_multicolor          = parsed.is_multicolor
            data.filament_slots         = parsed.filament_slots
            data.normalized_type        = parsed.normalized_type
            data.normalization_rule     = parsed.normalization_rule
            data.normalization_confidence = parsed.normalization_confidence

        # Seleccionar mejor thumbnail
        if data.all_thumbnails:
            data.all_thumbnails.sort(key=lambda t: t.pixels, reverse=True)
            best = data.all_thumbnails[0]
            data.thumbnail = best.data
            data.thumbnail_format = best.format

    except Exception as e:
        logger.error("GcodeParser", f"Error parseando BGcode {Path(file_path).name}: {str(e)}")

    return data


# ─────────────────────────────────────────────
# Parser de 3MF (.3mf) — ZIP con metadata
# ─────────────────────────────────────────────
def parse_3mf(file_path: str) -> GcodeData:
    data = GcodeData()
    data.file_name = Path(file_path).name

    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            names = zf.namelist()

            # Buscar .gcode dentro del ZIP
            gcode_path = None
            for name in names:
                lower = name.lower()
                if lower.startswith('metadata/') and lower.endswith('.gcode'):
                    gcode_path = name
                    break
            if not gcode_path:
                for name in names:
                    if name.lower().endswith('.gcode'):
                        gcode_path = name
                        break

            if gcode_path:
                gcode_text = zf.read(gcode_path).decode('utf-8', errors='replace')
                data = parse_gcode(gcode_text)
                data.file_name = Path(file_path).name

            # Fallback — JSON metadata (plate_*.json, project_settings.config)
            if (data.print_time_hours == 0 or data.filament_weight_grams == 0
                    or not data.printer_model or not data.filament_type):
                json_candidates = [
                    n for n in names
                    if (n.lower().endswith('.json') or n.lower().endswith('.config'))
                    and not zf.getinfo(n).is_dir()
                ]
                for name in json_candidates:
                    try:
                        json_text = zf.read(name).decode('utf-8', errors='replace')
                        json_data = json.loads(json_text)

                        if data.print_time_hours == 0:
                            for key in ('prediction', 'print_time', 'estimated_time'):
                                if key in json_data and json_data[key]:
                                    data.print_time_hours = round(float(json_data[key]) / 3600, 2)
                                    break

                        if data.filament_weight_grams == 0:
                            for key in ('weight', 'filament_used_g', 'filament_weight'):
                                if key in json_data and json_data[key]:
                                    data.filament_weight_grams = round(float(json_data[key]), 1)
                                    break

                        if not data.printer_model:
                            for key in ('printer_model', 'machine'):
                                if key in json_data and json_data[key]:
                                    val = json_data[key]
                                    data.printer_model = str(val[0] if isinstance(val, list) else val)
                                    break

                        if not data.filament_type:
                            if 'filament_type' in json_data and json_data['filament_type']:
                                val = json_data['filament_type']
                                data.filament_type = str(val[0] if isinstance(val, list) else val)

                        if not data.filament_colour:
                            if 'filament_colour' in json_data and json_data['filament_colour']:
                                val = json_data['filament_colour']
                                data.filament_colour = str(val[0] if isinstance(val, list) else val)

                        if data.nozzle_diameter == 0:
                            if 'nozzle_diameter' in json_data and json_data['nozzle_diameter']:
                                val = json_data['nozzle_diameter']
                                data.nozzle_diameter = round(float(val[0] if isinstance(val, list) else val), 2)

                    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                        pass

            # Fallback — XML/config (slice_info.config, project_settings.config, etc.)
            if data.print_time_hours == 0 or data.filament_weight_grams == 0:
                for name in names:
                    lower = name.lower()
                    if lower.endswith('.xml') or lower.endswith('.config'):
                        try:
                            xml_text = zf.read(name).decode('utf-8', errors='replace')

                            # Tiempo de impresión
                            if data.print_time_hours == 0:
                                # Formato <metadata key="prediction" value="20130"/>
                                time_m = re.search(
                                    r'<metadata\s+key="prediction"\s+value="(\d+)"',
                                    xml_text, re.IGNORECASE
                                )
                                if not time_m:
                                    time_m = re.search(
                                        r'estimated[_-]?time["\s:=>]+(\d+)',
                                        xml_text, re.IGNORECASE
                                    )
                                if time_m:
                                    data.print_time_hours = round(int(time_m.group(1)) / 3600, 2)

                            # Peso de filamento
                            if data.filament_weight_grams == 0:
                                # Formato <filament ... used_g="188.56" />
                                weight_m = re.search(
                                    r'<filament\b[^>]*\bused_g="([\d.]+)"',
                                    xml_text, re.IGNORECASE
                                )
                                if not weight_m:
                                    # Formato <metadata key="weight" value="188.56"/>
                                    weight_m = re.search(
                                        r'<metadata\s+key="weight"\s+value="([\d.]+)"',
                                        xml_text, re.IGNORECASE
                                    )
                                if not weight_m:
                                    weight_m = re.search(
                                        r'filament[_-]?weight[_-]?total["\s:=>]+([\d.]+)',
                                        xml_text, re.IGNORECASE
                                    )
                                if weight_m:
                                    data.filament_weight_grams = round(float(weight_m.group(1)), 1)

                            # Tipo de filamento
                            if not data.filament_type:
                                # Formato <filament ... type="PLA" />
                                type_m = re.search(
                                    r'<filament\b[^>]*\btype="([^"]+)"',
                                    xml_text, re.IGNORECASE
                                )
                                if not type_m:
                                    # PrusaSlicer INI config: filament_type = PLA
                                    type_m = re.search(
                                        r'^filament_type\s*=\s*([^\n;]+)', xml_text, re.IGNORECASE | re.MULTILINE
                                    )
                                if type_m:
                                    data.filament_type = type_m.group(1).strip().split(';')[0].strip()

                            # Temperaturas (PrusaSlicer INI config)
                            if data.bed_temperature == 0:
                                bed_m = re.search(
                                    r'^(?:bed_temperature|first_layer_bed_temperature)\s*=\s*([\d.]+)',
                                    xml_text, re.IGNORECASE | re.MULTILINE
                                )
                                if bed_m:
                                    data.bed_temperature = float(bed_m.group(1))

                            if data.hotend_temperature == 0:
                                hot_m = re.search(
                                    r'^(?:temperature|first_layer_temperature|nozzle_temperature)\s*=\s*([\d.]+)',
                                    xml_text, re.IGNORECASE | re.MULTILINE
                                )
                                if hot_m:
                                    data.hotend_temperature = float(hot_m.group(1))

                            # Modelo de impresora
                            if not data.printer_model:
                                # Formato <metadata key="printer_model_id" value="Creality_K1"/>
                                printer_m = re.search(
                                    r'<metadata\s+key="printer_model_id"\s+value="([^"]+)"',
                                    xml_text, re.IGNORECASE
                                )
                                if not printer_m:
                                    printer_m = re.search(
                                        r'printer[_-]?model["\s:=>]+([^"<\n]+)',
                                        xml_text, re.IGNORECASE
                                    )
                                if printer_m:
                                    data.printer_model = printer_m.group(1).strip().replace('_', ' ')
                        except Exception:
                            pass

            # Thumbnails desde 3MF
            thumb_candidates = [
                n for n in names
                if (n.lower().endswith('.png') or n.lower().endswith('.jpg') or n.lower().endswith('.jpeg'))
                and not zf.getinfo(n).is_dir()
            ]
            for tc in thumb_candidates:
                try:
                    img_data = zf.read(tc)
                    fmt = 'png' if tc.lower().endswith('.png') else 'jpg'
                    img = QImage()
                    img.loadFromData(img_data)
                    w = img.width() if not img.isNull() else 0
                    h = img.height() if not img.isNull() else 0
                    info = ThumbnailInfo(
                        data=img_data, format=fmt,
                        width=w, height=h,
                        source="3mf_file", file_name=tc
                    )
                    data.all_thumbnails.append(info)
                except Exception:
                    pass

            # Ordenar por resolución y elegir el mejor
            if data.all_thumbnails:
                data.all_thumbnails.sort(key=lambda t: t.pixels, reverse=True)
                best = data.all_thumbnails[0]
                if not data.thumbnail:
                    data.thumbnail = best.data
                    data.thumbnail_format = best.format

            # Calcular área superficial desde modelo 3D
            model_path = None
            for name in names:
                if name.lower().endswith('3dmodel.model'):
                    model_path = name
                    break
            if not model_path:
                for name in names:
                    if name.lower().endswith('.model'):
                        model_path = name
                        break

            if model_path:
                try:
                    model_content = zf.read(model_path).decode('utf-8', errors='replace')
                    data.surface_area_mm2 = _calculate_surface_area_from_3mf_model(model_content)
                except Exception:
                    pass

    except zipfile.BadZipFile:
        logger.error("GcodeParser", f"Archivo 3MF corrupto: {file_path}")

    return data


def _calculate_surface_area_from_3mf_model(xml_content: str) -> float:
    surface_area = 0.0
    try:
        clean = re.sub(r'\sxmlns[^"]*"[^"]*"', '', xml_content)
        root = ET.fromstring(clean)

        for mesh in root.iter('mesh'):
            vertices_elem = mesh.find('.//vertices')
            triangles_elem = mesh.find('.//triangles')
            if vertices_elem is None or triangles_elem is None:
                continue

            verts = []
            for v in vertices_elem.findall('vertex'):
                verts.append((
                    float(v.get('x', '0')),
                    float(v.get('y', '0')),
                    float(v.get('z', '0'))
                ))

            for tri in triangles_elem.findall('triangle'):
                i1 = int(tri.get('v1', '0'))
                i2 = int(tri.get('v2', '0'))
                i3 = int(tri.get('v3', '0'))
                if i1 < len(verts) and i2 < len(verts) and i3 < len(verts):
                    p1, p2, p3 = verts[i1], verts[i2], verts[i3]
                    ax, ay, az = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
                    bx, by, bz = p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]
                    cx = ay*bz - az*by
                    cy = az*bx - ax*bz
                    cz = ax*by - ay*bx
                    area = 0.5 * math.sqrt(cx*cx + cy*cy + cz*cz)
                    if not math.isnan(area):
                        surface_area += area
    except ET.ParseError:
        pass

    return round(surface_area, 2)


# ─────────────────────────────────────────────
# Función unificada de entrada
# ─────────────────────────────────────────────
def parse_file(file_path: str) -> GcodeData:
    """Parsea .gcode o .3mf y retorna GcodeData."""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == '.gcode':
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        data = parse_gcode(content)
        data.file_name = path.name
    elif ext == '.3mf':
        data = parse_3mf(file_path)
    elif ext == '.bgcode':
        data = parse_bgcode(file_path)
    else:
        data = GcodeData()
        data.file_name = path.name

    # Normalizar modelo de impresora: separar sistema multifilamento del modelo base
    # Ej: "COREONELMMU3" → printer_model="CORE One L", multifilament_system="MMU3"
    if data.printer_model:
        _mf_match = re.search(r'(MMU\d+S?|AMS(?:LITE)?)', data.printer_model, re.IGNORECASE)
        if _mf_match:
            data.multifilament_system = _mf_match.group(1).upper()
            data.printer_model = data.printer_model[:_mf_match.start()].strip()
        # Expandir ID comprimido de PrusaSlicer si hay coincidencia exacta
        _key = data.printer_model.upper().replace(' ', '').replace('-', '').replace('_', '')
        if _key in PRUSA_MODEL_ID_MAP:
            data.printer_model = PRUSA_MODEL_ID_MAP[_key]

    # Normalizar tipo de filamento
    if data.filament_type:
        vtype, rule, confidence = normalize_filament_type(data.filament_type)
        data.normalized_type = vtype
        data.normalization_rule = rule
        data.normalization_confidence = confidence

    logger.info("GcodeParser", f"Archivo parseado: {data.file_name} | Slicer: {data.slicer} | "
                f"Tiempo: {data.print_time_hours}h | Peso: {data.filament_weight_grams}g | "
                f"Material: {data.filament_type} → {data.normalized_type}")

    return data
