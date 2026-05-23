"""
Enumeraciones para tipos de filamento y otros dominios de la aplicación
"""
from enum import Enum


class FilamentType(Enum):
    """Tipos de filamento disponibles"""
    # ── PLA familia ──
    PLA = "PLA"
    PLA_PLUS = "PLA+"
    PLA_PRO = "PLA Pro"
    PLA_SILK = "PLA Silk"
    PLA_MARBLE = "PLA Marble"
    PLA_MATTE = "PLA Matte"
    PLA_WOOD = "PLA Wood"
    PLA_HIGH_SPEED = "PLA High Speed"
    PLA_CF = "PLA-CF"
    # ── ABS familia ──
    ABS = "ABS"
    ABS_GF = "ABS-GF"
    # ── PETG familia ──
    PETG = "PETG"
    PETG_CF = "PETG-CF"
    PETG_HF = "PETG HF"
    PETG_ESD = "PETG-ESD"
    PETG_RCF = "PETG-rCF"
    PET = "PET"
    PET_CF = "PET-CF"
    PCTG = "PCTG"
    # ── ASA familia ──
    ASA = "ASA"
    ASA_CF = "ASA-CF"
    # ── Flexibles ──
    TPU = "TPU"
    TPE = "TPE"
    FLEX = "FLEX"
    SBS = "SBS"
    EVA = "EVA"
    # ── Poliamidas (Nylon) ──
    NYLON = "Nylon"
    NYLON_CF = "Nylon CF"
    PA_GF = "PA-GF"
    PA6_GF = "PA6-GF"
    PA612_CF = "PA612-CF"
    PPA_CF = "PPA-CF"
    PPA_GF = "PPA-GF"
    # ── Policarbonato ──
    PC = "PC"
    PC_ABS = "PC-ABS"
    # ── Polipropileno ──
    PP = "PP"
    PP_CF = "PP-CF"
    PP_GF = "PP-GF"
    # ── Soporte ──
    PVA = "PVA"
    BVOH = "BVOH"
    HIPS = "HIPS"
    # ── Ingeniería ──
    PPS = "PPS"
    PPS_CF = "PPS-CF"
    PE = "PE"
    PE_CF = "PE-CF"
    PHA = "PHA"
    PMMA = "PMMA"
    POM = "POM"
    PEEK = "PEEK"
    PEI = "PEI"
    PEI_CF = "PEI-CF"
    # ── Otros ──
    OTHER = "OTHER"


class FilamentColor(Enum):
    """Gama de colores estandarizada para filamentos 3D"""    
    # === Básicos ===
    WHITE = "Blanco"
    BLACK = "Negro"
    RED = "Rojo"
    BLUE = "Azul"
    GREEN = "Verde"
    YELLOW = "Amarillo"
    ORANGE = "Naranja"
    PURPLE = "Morado"
    PINK = "Rosa"
    BROWN = "Marrón"
    GRAY = "Gris"
    TRANSPARENT = "Transparente"
    NATURAL = "Natural"

    # === Azules ===
    LIGHT_BLUE = "Azul Claro"
    DARK_BLUE = "Azul Oscuro"
    NAVY_BLUE = "Azul Marino"
    SKY_BLUE = "Azul Cielo"
    PRUSSIAN_BLUE = "Azul Prusia"
    COBALT = "Cobalto"
    CELESTE = "Celeste"
    AQUA = "Aqua"

    # === Verdes ===
    LIGHT_GREEN = "Verde Claro"
    DARK_GREEN = "Verde Oscuro"
    LIME = "Verde Lima"
    OLIVE = "Verde Oliva"
    SAGE = "Verde Salvia"
    MINT = "Menta"
    TEAL = "Verde Azulado"

    # === Grises y Neutros ===
    LIGHT_GRAY = "Gris Claro"
    DARK_GRAY = "Gris Oscuro"
    SILVER_GRAY = "Gris Plata"
    BEIGE = "Beige"
    CREAM = "Crema"
    IVORY = "Marfil"
    KHAKI = "Caqui"
    TAN = "Canela"
    DARK_BROWN = "Marrón Oscuro"
    LIGHT_BROWN = "Marrón Claro"
    CHOCOLATE = "Chocolate"

    # === Metálicos ===
    SILVER = "Plateado"
    GOLD = "Dorado"
    BRONZE = "Bronce"
    COPPER = "Cobre"

    # === Rojos, Rosados y Violetas ===
    BURGUNDY = "Bordó"
    MAROON = "Granate"
    CORAL = "Coral"
    SALMON = "Salmón"
    PEACH = "Durazno"
    FUCHSIA = "Fucsia"
    MAGENTA = "Magenta"
    VIOLET = "Violeta"
    LAVENDER = "Lavanda"
    INDIGO = "Índigo"
    SKIN_TONE = "Tono Piel"

    # === Otros Sólidos ===
    TURQUOISE = "Turquesa"
    CYAN = "Cian"
    RUBY = "Rubí"
    EMERALD = "Esmeralda"

    # === Fluorescentes / Neón ===
    YELLOW_FLUO = "Amarillo Fluo"
    GREEN_FLUO = "Verde Fluo"
    ORANGE_FLUO = "Naranja Fluo"
    HEX_FLUO = "Rosa Fluo"
    FUCHSIA_FLUO = "Fucsia Fluo"

    # === Translúcidos ===
    TRANS_RED = "Rojo Translúcido"
    TRANS_BLUE = "Azul Translúcido"
    TRANS_GREEN = "Verde Translúcido"
    TRANS_YELLOW = "Amarillo Translúcido"
    TRANS_ORANGE = "Naranja Translúcido"
    TRANS_PURPLE = "Morado Translúcido"
    TRANS_PINK = "Rosa Translúcido"

    # === Co-extrusión y Efectos (Bicolor / Multicolor / Co-extrusion) ===
    RAINBOW = "Arcoíris"
    WHITE_GREEN = "Blanco-Verde"
    GREEN_BLUE = "Verde-Azul"
    PINK_BLUE = "Rosa-Azul"
    DUAL_COLOR = "Bicolor"         # Genérico para bobinas de doble color (ej. Verde-Azul)
    TRI_COLOR = "Tricolor"         # Genérico para bobinas de triple color
    GLOW_IN_THE_DARK = "Fotoluminiscente" # Clave técnica para filamentos que brillan en la oscuridad

    # === Comodín ===
    OTHER = "Otro"


class QuoteStatus(Enum):
    """Estados de presupuesto"""
    DRAFT = "Borrador"
    PENDING = "Pendiente"
    APPROVED = "Aprobado"
    REJECTED = "Rechazado"
    COMPLETED = "Completado"
    CANCELLED = "Cancelado"


class AdvanceMode(Enum):
    """Modos de anticipo disponibles"""
    NONE = 0  # Sin anticipo automático
    AUTO_START = 1  # Activar por defecto al iniciar
    MIN_AMOUNT = 2  # Activar al monto mínimo
    MAX_AMOUNT = 3  # Activar al monto máximo
    MIN_MAX_AMOUNT = 4  # Activar en montos mínimos y máximos
    
    @classmethod
    def get_display_names(cls):
        """Obtiene los nombres para mostrar en la interfaz"""
        return [
            "Manual - Aplicar ajuste por defecto",
            "Inicial - Aplicar ajuste por defecto al abrir la aplicación",
            "Automático - Aplicar al monto mínimo", 
            "Automático - Aplicar al monto máximo",
            "Automático - Aplicar al monto mínimo y máximo"
        ]
    
    @classmethod
    def get_display_name(cls, mode_value: int) -> str:
        """Obtiene el nombre para mostrar de un modo específico"""
        names = cls.get_display_names()
        if 0 <= mode_value < len(names):
            return names[mode_value]
        return names[0]  # Default a "Manual - Aplicar ajuste por defecto"
    
    @classmethod
    def from_display_name(cls, display_name: str) -> int:
        """Obtiene el valor numérico a partir del nombre de display"""
        names = cls.get_display_names()
        try:
            return names.index(display_name)
        except ValueError:
            return 0  # Default a NONE


# ─────────────────────────────────────────────
# Catálogo de impresoras 3D (extraído de OrcaSlicer profiles)
# 61 marcas, 351+ modelos
# ─────────────────────────────────────────────
PRINTER_CATALOG = {
    "Afinia": [
        "H+1(HS)",
    ],
    "Anker": [
        "M5",
        "M5 All-Metal Hot End",
        "M5C",
    ],
    "Anycubic": [
        "4Max Pro",
        "4Max Pro 2",
        "Chiron",
        "Kobra",
        "Kobra 2",
        "Kobra 2 Max",
        "Kobra 2 Neo",
        "Kobra 2 Plus",
        "Kobra 2 Pro",
        "Kobra 3",
        "Kobra Max",
        "Kobra Plus",
        "Kobra S1",
        "Predator",
        "Vyper",
        "i3 Mega S",
    ],
    "Artillery": [
        "Genius",
        "Genius Pro",
        "Hornet",
        "M1 Pro",
        "Sidewinder X1",
        "Sidewinder X2",
        "Sidewinder X3 Plus",
        "Sidewinder X3 Pro",
        "Sidewinder X4 Plus",
        "Sidewinder X4 Pro",
    ],
    "Bambu Lab": [
        "A1",
        "A1 mini",
        "H2D",
        "H2D Pro",
        "H2S",
        "P1P",
        "P1S",
        "P2S",
        "X1",
        "X1 Carbon",
        "X1E",
    ],
    "BIQU (BigTreeTech)": [
        "B1",
        "BX",
        "Hurakan",
    ],
    "Blocks": [
        "Pro S100",
        "RD50 V2",
        "RF50",
    ],
    "Chuanying": [
        "X1",
    ],
    "CoLiDo": [
        "160 V2",
        "DIY 4.0",
        "DIY 4.0 V2",
        "SR1",
        "X16",
    ],
    "CoPrint": [
        "ChromaSet",
    ],
    "Comgrow": [
        "T300",
        "T500",
    ],
    "Construct3D": [
        "1",
        "1 XL",
    ],
    "Creality": [
        "CR-10 Max",
        "CR-10 SE",
        "CR-10 V2",
        "CR-10 V3",
        "CR-6 Max",
        "CR-6 SE",
        "CR-M4",
        "Ender-3",
        "Ender-3 Pro",
        "Ender-3 S1",
        "Ender-3 S1 Plus",
        "Ender-3 S1 Pro",
        "Ender-3 V2",
        "Ender-3 V2 Neo",
        "Ender-3 V3",
        "Ender-3 V3 KE",
        "Ender-3 V3 Plus",
        "Ender-3 V3 SE",
        "Ender-5",
        "Ender-5 Max",
        "Ender-5 Plus",
        "Ender-5 Pro (2019)",
        "Ender-5 S1",
        "Ender-5S",
        "Ender-6",
        "Hi",
        "K1",
        "K1 Max",
        "K1 SE",
        "K1C",
        "K2",
        "K2 Plus",
        "K2 Pro",
        "Sermoon V1",
    ],
    "Cubicon": [
        "xCeler-I",
        "xCeler-Plus",
    ],
    "DeltaMaker": [
        "2",
        "2T",
        "2XT",
    ],
    "Dremel": [
        "3D20",
        "3D40",
        "3D45",
    ],
    "Elegoo": [
        "Centauri",
        "Centauri Carbon",
        "Centauri Carbon 2",
        "Neptune",
        "Neptune 2",
        "Neptune 2D",
        "Neptune 2S",
        "Neptune 3",
        "Neptune 3 Max",
        "Neptune 3 Plus",
        "Neptune 3 Pro",
        "Neptune 4",
        "Neptune 4 Max",
        "Neptune 4 Plus",
        "Neptune 4 Pro",
        "Neptune X",
        "OrangeStorm Giga",
    ],
    "Eryone": [
        "ER20",
        "ER20 Klipper",
        "Thinker X400",
    ],
    "FLSun": [
        "Q5",
        "QQ-S Pro",
        "S1",
        "Super Racer (SR)",
        "T1",
        "V400",
    ],
    "Flashforge": [
        "AD5X",
        "Adventurer 3 Series",
        "Adventurer 4 Series",
        "Adventurer 5M",
        "Adventurer 5M Pro",
        "Guider 2s",
        "Guider 3 Ultra",
        "Guider4",
        "Guider4 Pro",
    ],
    "FlyingBear": [
        "Ghost 6",
        "Ghost7",
        "Reborn3",
        "S1",
    ],
    "Folgertech": [
        "FT-5",
        "FT-6",
        "i3",
    ],
    "Geeetech": [
        "A10 M",
        "A10 Pro",
        "A10 T",
        "A20",
        "A20 M",
        "A20 T",
        "A30 M",
        "A30 Pro",
        "A30 T",
        "M1",
        "Mizar",
        "Mizar M",
        "Mizar Max",
        "Mizar Pro",
        "Mizar S",
        "Thunder",
    ],
    "Ginger Additive": [
        "G1",
    ],
    "InfiMech": [
        "EX",
        "EX+APS",
        "TX",
        "TX Hardened Steel Nozzle",
    ],
    "Kingroon": [
        "KLP1",
        "KP3S 3.0",
        "KP3S PRO S1",
        "KP3S PRO V2",
        "KP3S V1",
    ],
    "LONGER": [
        "LK10",
        "LK10 Plus",
    ],
    "Lulzbot": [
        "Taz 4 or 5",
        "Taz 6",
        "Taz Pro Dual",
        "Taz Pro S",
    ],
    "M3D": [
        "Enabler D8500 MM Model",
    ],
    "MagicMaker": [
        "MM BoneKing",
        "MM hj SK",
        "MM hqs SF",
        "MM hqs hj",
        "MM slb",
    ],
    "Mellow": [
        "M1",
    ],
    "OpenEYE": [
        "Peacock V2",
    ],
    "Peopoly": [
        "Magneto X",
    ],
    "Phrozen": [
        "Arco",
    ],
    "Positron3D": [
        "The Positron",
    ],
    "Prusa": [
        "CORE One",
        "CORE One HF",
        "CORE One L",
        "CORE One L HF",
        "MINI",
        "MINI IS",
        "MK3.5",
        "MK3S",
        "MK4",
        "MK4S",
        "MK4S HF",
        "XL",
        "XL 5T",
    ],
    "Qidi": [
        "Q1 Pro",
        "Q2",
        "Q2C",
        "X-CF Pro",
        "X-Max",
        "X-Max 3",
        "X-Max 4",
        "X-Plus",
        "X-Plus 3",
        "X-Plus 4",
        "X-Smart 3",
    ],
    "RH3D": [
        "E3NG v1.2S",
    ],
    "Raise3D": [
        "Pro3",
        "Pro3 Plus",
    ],
    "Ratrig": [
        "V-Cast",
        "V-Core 3 200",
        "V-Core 3 300",
        "V-Core 3 400",
        "V-Core 3 500",
        "V-Core 4 300",
        "V-Core 4 400",
        "V-Core 4 500",
        "V-Core 4 HYBRID 300",
        "V-Core 4 HYBRID 400",
        "V-Core 4 HYBRID 500",
        "V-Core 4 IDEX 300",
        "V-Core 4 IDEX 300 COPY MODE",
        "V-Core 4 IDEX 300 MIRROR MODE",
        "V-Core 4 IDEX 400",
        "V-Core 4 IDEX 400 COPY MODE",
        "V-Core 4 IDEX 400 MIRROR MODE",
        "V-Core 4 IDEX 500",
        "V-Core 4 IDEX 500 COPY MODE",
        "V-Core 4 IDEX 500 MIRROR MODE",
        "V-Minion",
    ],
    "RolohaunDesign": [
        "Delta Flyer Refit",
        "Rook MK1 LDO",
    ],
    "SecKit": [
        "SK-Tank",
        "Go3",
    ],
    "Snapmaker": [
        "A250",
        "A250 BKit",
        "A250 Dual",
        "A250 Dual BKit",
        "A250 Dual QS+B Kit",
        "A250 Dual QSKit",
        "A250 QS+B Kit",
        "A250 QSKit",
        "A350",
        "A350 BKit",
        "A350 Dual",
        "A350 Dual BKit",
        "A350 Dual QS+B Kit",
        "A350 Dual QSKit",
        "A350 QS+B Kit",
        "A350 QSKit",
        "Artisan",
        "J1",
        "U1",
    ],
    "Sovol": [
        "SV01",
        "SV01 Pro",
        "SV02",
        "SV05",
        "SV06",
        "SV06 ACE",
        "SV06 Plus",
        "SV06 Plus ACE",
        "SV07",
        "SV07 Plus",
        "SV08",
        "SV08 MAX",
        "Zero",
    ],
    "Tiertime": [
        "UP300 HS",
        "UP310 Pro",
        "UP400 Pro",
        "UP600 HS",
    ],
    "Tronxy": [
        "X5SA 400 Marlin Firmware",
    ],
    "TwoTrees": [
        "SK1",
        "SP-5 Klipper",
    ],
    "UltiMaker": [
        "2",
    ],
    "Vivedino": [
        "Troodon 2.0 - Klipper",
        "Troodon 2.0 - RRF",
    ],
    "Volumic": [
        "EXO42",
        "EXO42 IDRE",
        "EXO42 Performance",
        "EXO42 Stage 2",
        "EXO65",
        "EXO65 IDRE",
        "EXO65 Performance",
        "EXO65 Stage 2",
        "SH65",
        "SH65 IDRE",
        "SH65 Performance",
        "SH65 Stage 2",
        "VS20MK2",
        "VS30MK2",
        "VS30MK3",
        "VS30MK3 Stage 2",
        "VS30SC",
        "VS30SC2",
        "VS30SC2 Performance",
        "VS30SC2 Stage 2",
        "VS30ULTRA",
    ],
    "Voron": [
        "0.1",
        "2.4 250",
        "2.4 300",
        "2.4 350",
        "Switchwire 250",
        "Trident 250",
        "Trident 300",
        "Trident 350",
    ],
    "Voxelab": [
        "Aquila X2",
    ],
    "Vzbot": [
        "235 AWD",
        "330 AWD",
    ],
    "WEMAKE3D": [
        "PhoenixProV1",
        "TinyBotV1",
    ],
    "Wanhao": [
        "D12-300",
    ],
    "Wanhao France": [
        "D12 230 PRO M2 DIRECT",
        "D12 230 PRO M2 MONO DUAL",
        "D12 230 PRO M2 MONO DUAL PoopTool",
        "D12 230 PRO SMARTPAD DIRECT",
        "D12 230 PRO SMARTPAD MONO DUAL",
        "D12 230 PRO SMARTPAD MONO DUAL PoopTool",
        "D12 300 PRO M2 DIRECT",
        "D12 300 PRO M2 MONO DUAL",
        "D12 300 PRO M2 MONO DUAL PoopTool",
        "D12 300 PRO SMARTPAD DIRECT",
        "D12 300 PRO SMARTPAD MONO DUAL",
        "D12 300 PRO SMARTPAD MONO DUAL PoopTool",
        "D12 500 PRO M2 DIRECT",
        "D12 500 PRO M2 MONO DUAL",
        "D12 500 PRO M2 MONO DUAL PoopTool",
        "D12 500 PRO SMARTPAD DIRECT",
        "D12 500 PRO SMARTPAD MONO DUAL",
        "D12 500 PRO SMARTPAD MONO DUAL PoopTool",
    ],
    "WonderMaker": [
        "ZR",
        "ZR Ultra",
        "ZR Ultra S",
    ],
    "Z-Bolt": [
        "S1000",
        "S1000 Dual",
        "S300",
        "S300 Dual",
        "S400",
        "S400 Dual",
        "S600",
        "S600 Dual",
        "S800 Dual",
    ],
    "iQ": [
        "TiQ2",
        "TiQ8",
    ],
    "Otra": [],
}

