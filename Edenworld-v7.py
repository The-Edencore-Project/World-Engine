# ============ EDEN WORLD-V7 (CHUNK 1/3) ============
# Geometry shift, Leviathan Ambience, and the Woven Layer.
# =======================================================

import tkinter as tk, math, time, os, json, random
import wave, array, subprocess, shutil, threading

root = tk.Tk()
root.title("Edenshore")
try: 
    root.attributes("-fullscreen", True)
except tk.TclError: 
    pass

root.update_idletasks()
W, H = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (W, H))
root.configure(bg="#0a0208")

canvas = tk.Canvas(root, bg="#020108", width=W, height=H, highlightthickness=0)
canvas.pack(fill="both", expand=True)

def font_full(px, bold=True): 
    return ("Helvetica", -max(8, int(px)), "bold" if bold else "normal")

DEVICE_CLASS = "phone" if W < 600 else "tablet" if W < 1200 else "desktop"

# ============ DIRECTORIES ============
STATE_DIR = os.path.join(os.path.expanduser("~"), ".edenworld")
STATE_PATH = os.path.join(STATE_DIR, "world_state.json")
WEIGHTS_PATH = os.path.join(STATE_DIR, "council_weights.json")
MUSIC_PATH = os.path.join(STATE_DIR, "music.wav")
DRONE_PATH = os.path.join(STATE_DIR, "drone.wav")

def _ensure_state_dir():
    try: os.makedirs(STATE_DIR, exist_ok=True)
    except Exception: pass

# ============ AUDIO ENGINE ============
AUDIO_MODE = None
AUDIO_PROC = [None]

def _detect_audio():
    global AUDIO_MODE
    try:
        from playsound import playsound
        AUDIO_MODE = "playsound"; return
    except Exception: pass
    try:
        import pygame
        pygame.mixer.init()
        AUDIO_MODE = "pygame"; return
    except Exception: pass
    if shutil.which("am"):
        AUDIO_MODE = "android"; return
    AUDIO_MODE = None

_detect_audio()

def _generate_drone(path, base_freq=110.0, duration=20.0, sr=22050):
    n = int(duration * sr); buf = array.array('h')
    for i in range(n):
        t = i / sr
        s = (math.sin(2*math.pi*base_freq*t) * 0.40 + math.sin(2*math.pi*base_freq*1.5*t) * 0.20 + math.sin(2*math.pi*base_freq*2.01*t) * 0.14)
        env = 0.65 + 0.35 * math.sin(2*math.pi*t / 8.0)
        v = int(s * env * 11000)
        buf.append(max(-32767, min(32767, v)))
    with wave.open(str(path), 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(buf.tobytes())

def ensure_music():
    _ensure_state_dir()
    if os.path.exists(MUSIC_PATH): return MUSIC_PATH
    if not os.path.exists(DRONE_PATH):
        try: _generate_drone(DRONE_PATH)
        except Exception: return None
    return DRONE_PATH

def play_music(path, loop=True, volume=0.25):
    if AUDIO_MODE is None or path is None: return
    try:
        if AUDIO_MODE == "playsound":
            from playsound import playsound
            playsound(str(path), block=False)
        elif AUDIO_MODE == "pygame":
            import pygame
            pygame.mixer.music.load(str(path)); pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(-1 if loop else 0)
        elif AUDIO_MODE == "android":
            AUDIO_PROC[0] = subprocess.Popen(["am","start","-a","android.intent.action.VIEW","-d","file://"+str(path),"-t","audio/wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception: pass

def _boot_audio():
    path = ensure_music()
    if path: play_music(path, loop=True, volume=0.25)

# ============ PALETTES ============
WATER_TOP = "#2a0450"; WATER_HIGH = "#5a1080"; WATER_MID = "#a82870"
WATER_LOW = "#e06030"; WATER_DEEP = "#a03018"; WATER_BOT = "#1a0410"
SAND_LIT = "#8a4828"; SAND = "#3a1810"; SAND_DARK = "#1a0808"; SAND_DEEP = "#080202"

FOREST_TOP = "#60ffd0"; FOREST_HIGH = "#208060"; FOREST_MID = "#104030"
FOREST_LOW = "#0a2018"; FOREST_BOT = "#050a08"
DIRT_LIT = "#5a3a20"; DIRT = "#2a1810"; DIRT_DARK = "#140a05"; DIRT_DEEP = "#050201"

BEACH_TOP = "#2a1a40"; BEACH_HIGH = "#a04060"; BEACH_MID = "#e07050"
BEACH_LOW = "#f0a060"; BEACH_DEEP = "#f0d090"; BEACH_BOT = "#f0e0b0"
COAST_LIT = "#f0d8a0"; COAST = "#c0a070"; COAST_DARK = "#806040"; COAST_DEEP = "#402010"

CASTLE_TOP = "#0a0510"; CASTLE_HIGH = "#1a1028"; CASTLE_MID = "#2a1838"
CASTLE_LOW = "#3a2048"; CASTLE_DEEP = "#1a0820"; CASTLE_BOT = "#050205"
STONE_LIT = "#4a4050"; STONE = "#2a2028"; STONE_DARK = "#181018"; STONE_DEEP = "#0a0508"

GLOW_WARM = "#ffe8a0"; GLOW_COOL = "#80ffe0"; GLOW_GREEN = "#60ffd0"; GLOW_PINK = "#ff80b8"
BUBBLE_TEXT = "#fff8e8"; NESSY_BODY = "#0a0418"; NESSY_RIM_BASE = "#ffb060"; HAZE = "#4a1030"
UI_COL = "#a0a0a0"

# ============ SEATS & GEOMETRY ============
SEATS = ["Solon","Lumen","Vertex","Prism","Ripple"]
SEAT_BODY = {"Solon":"#1a2848","Lumen":"#3a1858","Vertex":"#1a3a28","Prism":"#5a3810","Ripple":"#48182a"}
SEAT_RIM  = {"Solon":"#ffb060","Lumen":"#ffc080","Vertex":"#ffa050","Prism":"#ffd080","Ripple":"#ffb8a0"}
SEAT_COLOUR = dict(SEAT_RIM)
SEAT_BREATH = {"Solon":5.0,"Lumen":2.0,"Vertex":1.5,"Prism":4.0,"Ripple":3.0}

# V7 GEOMETRY SHIFT: Moved down by 0.08 to give bubbles more runway
SEAT_HOME_X = {"Solon":0.35, "Lumen":0.22, "Vertex":0.50, "Ripple":0.78, "Prism":0.65}
SEAT_HOME_Y = {"Solon":0.40, "Lumen":0.56, "Vertex":0.80, "Ripple":0.56, "Prism":0.40}

# ============ MATH & PERSPECTIVE ============
def lerp(c1, c2, t):
    h1=c1.lstrip("#"); h2=c2.lstrip("#")
    r1=int(h1[0:2],16); g1=int(h1[2:4],16); b1=int(h1[4:6],16)
    r2=int(h2[0:2],16); g2=int(h2[2:4],16); b2=int(h2[4:6],16)
    t=max(0.0,min(1.0,t))
    return "#%02x%02x%02x"%(int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t))

def clamp(v,lo,hi): return max(lo,min(hi,v))

HUE_PERIOD = 240.0
def _hue_shift_hex(hex_col, shift):
    h = hex_col.lstrip("#")
    r=int(h[0:2],16)/255.0; g=int(h[2:4],16)/255.0; b=int(h[4:6],16)/255.0
    mx=max(r,g,b); mn=min(r,g,b); d=mx-mn
    if d == 0: hh = 0.0
    elif mx == r: hh = ((g-b)/d) % 6
    elif mx == g: hh = (b-r)/d + 2
    else:         hh = (r-g)/d + 4
    hh = (hh / 6.0 + shift) % 1.0
    s = 0 if mx == 0 else d/mx
    v = mx
    i = int(hh * 6.0); f = hh * 6.0 - i
    p = v*(1-s); q = v*(1-f*s); t = v*(1-(1-f)*s)
    i = i % 6
    if   i == 0: rr,gg,bb = v,t,p
    elif i == 1: rr,gg,bb = q,v,p
    elif i == 2: rr,gg,bb = p,v,t
    elif i == 3: rr,gg,bb = p,q,v
    elif i == 4: rr,gg,bb = t,p,v
    else:        rr,gg,bb = v,p,q
    return "#%02x%02x%02x"%(int(rr*255),int(gg*255),int(bb*255))

def hue_shift_amount(): return math.sin(time.time() * (2*math.pi / HUE_PERIOD)) * 0.12
def hue(col):
    s = hue_shift_amount()
    return _hue_shift_hex(col, s) if abs(s) >= 0.002 else col

def get_perspective_scale(y_pos):
    far_y = H * 0.25; near_y = H * 0.75
    depth = clamp((y_pos - far_y) / (near_y - far_y), 0.0, 1.0)
    return 0.4 + (depth * 0.6)

# ============ CAMERA ============
ZOOM_FIXED = 0.85
CAM_FX = W * 0.5; CAM_FY = H * 0.50
def cam(x, y): return (CAM_FX + (x - CAM_FX) * ZOOM_FIXED, CAM_FY + (y - CAM_FY) * ZOOM_FIXED)

# ============ CONSTANTS & GLOBALS ============
SURFACE_Y = int(H*0.06); FLOOR_Y = int(H*0.80)
LIGHT_X = int(W*0.50); START_TIME = time.time()

CURRENT_BIOME = "water"
INTERO = {"session_mins":0.0,"utterances":0,"chamber_strain":0.0,"session_warmth":0.0,"utterances_this_hour":0,"last_hour_seen":time.localtime().tm_hour,"been_touched":False,"last_touch_kind":None}
EXTERO = {"hour":0,"rhythm":"afternoon","time_bucket":"afternoon","battery":None,"charging":False,"touch_x":-1,"touch_y":-1,"touch_at":0.0,"touch_count_session":0,"drag_distance":0.0,"focused":True,"focus_lost_at":0.0,"device_class":DEVICE_CLASS}
MOOD = {"target":0.55,"current":0.55,"last_utterance_at":time.time(),"drift_phase":random.uniform(0,6.28)}
STRAIN = {s: 0.2 for s in SEATS}; BREATH = {s: random.uniform(0,6.28) for s in SEATS}
BELL = {"phase": 0.0}; QUIET = {"level": 0.0, "silent_since": time.time()}
VALENCE = {"level": 0.5, "target": 0.5}; SURPRISE = {"current": 0.0, "smooth": 0.0}
HARMONY = {"level": 1.0, "target": 1.0}; NESSY = {"x": W * 0.4, "speed": 0.35 * (W / 800.0), "phase": 0.0, "dip": 0.0, "bright": 0.0}
SCENE = {"t":0.0,"last_save":time.time(),"scroll_x":0.0,"scroll_speed":0.5, "last_biome": CURRENT_BIOME}
PULSE = {"phase":0.0}; CREATURES = []; GUESTS = []; STREAMS = []; PARTICLES = []
LEVIATHANS = [] # The massive background elements
DIALOGUE_QUEUE = {"active": False, "lines": [], "index": 0, "gap": 0.5, "t": 0.0, "current_seat": None}
PLAYED_STORIES = set(); RHYTHM = {"last_seat": None, "time_since_last_story": 0.0}
STATUS_TEXT = {"text": "Edenshore", "timer": 0.0}

BIOME_REACTOR = {"weather": "calm", "timer": 0.0}
ONBOARDING = {"active": False, "step": 0}
INQUIRY = {"active": False, "step": 0, "timer": 0.0, "last_run": time.time()}
ENTRY_BOX = None

UI_BUTTONS = {
    "pond":   {"x": W*0.15, "y": H*0.94, "text": "POND", "active": True},
    "forest": {"x": W*0.38, "y": H*0.94, "text": "FOREST", "active": False},
    "beach":  {"x": W*0.62, "y": H*0.94, "text": "BEACH", "active": False},
    "castle": {"x": W*0.85, "y": H*0.94, "text": "CASTLE", "active": False}
}

# ============ NEURAL NETWORK ============
def sigmoid(x):
    if x < -60: return 0.0
    if x > 60: return 1.0
    return 1.0 / (1.0 + math.exp(-x))

WEIGHT_CLAMP = 10.0; LR_DEFAULT = 0.02; LR_LUMEN = 0.005
class SeatNet:
    def __init__(self, seed, lr=LR_DEFAULT):
        rng = random.Random(seed)
        self.n_in = 20; self.n_hid = 16
        self.W1 = [[rng.uniform(-0.5, 0.5) for _ in range(self.n_hid)] for _ in range(self.n_in)]
        self.B1 = [0.0] * self.n_hid; self.W2 = [rng.uniform(-0.5, 0.5) for _ in range(self.n_hid)]; self.B2 = 0.0
        self.lr = lr; self.loss = 1.0; self.last_out = 0.5; self.last_target = 0.0; self.attention = 1.0 
    def forward(self, x):
        h = [sigmoid(self.B1[j] + sum(x[i] * self.W1[i][j] for i in range(self.n_in))) for j in range(self.n_hid)]
        zo = self.B2 + sum(h[j] * self.W2[j] for j in range(self.n_hid))
        return h, sigmoid(zo)
    def _clamp_weights(self):
        for i in range(self.n_in):
            for j in range(self.n_hid): self.W1[i][j] = clamp(self.W1[i][j], -WEIGHT_CLAMP, WEIGHT_CLAMP)
        for j in range(self.n_hid): self.W2[j] = clamp(self.W2[j], -WEIGHT_CLAMP, WEIGHT_CLAMP)
    def step(self, x, target):
        h, o = self.forward(x)
        d_out = (o - target) * o * (1 - o)
        d_hid = [d_out * self.W2[j] * h[j] * (1 - h[j]) for j in range(self.n_hid)]
        step_lr = self.lr * self.attention
        for j in range(self.n_hid): self.W2[j] -= step_lr * d_out * h[j]
        self.B2 -= step_lr * d_out
        for i in range(self.n_in):
            for j in range(self.n_hid): self.W1[i][j] -= step_lr * d_hid[j] * x[i]
        for j in range(self.n_hid): self.B1[j] -= step_lr * d_hid[j]
        self._clamp_weights(); self.last_out = o; self.last_target = target; self.loss = (o - target) ** 2
    def confidence(self): return abs(self.last_out - 0.5) * 2.0
    def to_dict(self): return {"W1": self.W1, "B1": self.B1, "W2": self.W2, "B2": self.B2}
    def load_dict(self, d):
        try:
            W1 = d.get("W1"); B1 = d.get("B1"); W2 = d.get("W2"); B2 = d.get("B2")
            if (isinstance(W1, list) and len(W1) == self.n_in and isinstance(B1, list) and len(B1) == self.n_hid and isinstance(W2, list) and len(W2) == self.n_hid):
                self.W1 = W1; self.B1 = B1; self.W2 = W2; self.B2 = float(B2); self._clamp_weights()
        except Exception: pass

SEAT_NETS = {s: SeatNet(seed=hash(s) & 0xffff, lr=(LR_LUMEN if s=="Lumen" else LR_DEFAULT)) for s in SEATS}

# ============ STATE & ONBOARDING ============
def load_state():
    try:
        with open(STATE_PATH) as f: d=json.load(f)
        return {
            "mood":float(d.get("mood",0.55)), "strain":float(d.get("strain",0.20)), 
            "valence":float(d.get("valence",0.5)), "last_seen":float(d.get("last_seen",0.0)), 
            "last_hour":int(d.get("last_hour",-1)), "visits":int(d.get("visits",0)), 
            "biome":str(d.get("biome","water")), "name":str(d.get("name","")),
            "age":str(d.get("age","")), "location":str(d.get("location","")),
            "fav_food":str(d.get("fav_food","")), "fav_game":str(d.get("fav_game","")), "fav_biome":str(d.get("fav_biome",""))
        }
    except Exception: 
        return {"mood":0.55,"strain":0.20,"valence":0.5,"last_seen":0.0,"last_hour":-1,"visits":0,"biome":"water","name":"","age":"","location":"","fav_food":"","fav_game":"","fav_biome":""}

def save_state(mood, strain):
    _ensure_state_dir()
    try:
        with open(STATE_PATH, "w") as f: 
            json.dump({
                "mood":round(mood,4),"strain":round(strain,4),"valence":round(VALENCE["level"],4),
                "last_seen":time.time(),"last_hour":time.localtime().tm_hour,"visits":PRIOR.get("visits",0)+1,
                "biome":CURRENT_BIOME,"name":PRIOR.get("name",""), "age":PRIOR.get("age",""), "location":PRIOR.get("location",""),
                "fav_food":PRIOR.get("fav_food",""), "fav_game":PRIOR.get("fav_game",""), "fav_biome":PRIOR.get("fav_biome","")
            }, f)
        with open(WEIGHTS_PATH, "w") as f: json.dump({s: SEAT_NETS[s].to_dict() for s in SEATS}, f)
    except Exception: pass

PRIOR = load_state()

def start_onboarding():
    global ENTRY_BOX
    ONBOARDING["active"] = True
    ONBOARDING["step"] = 1
    
    ENTRY_BOX = tk.Entry(root, font=("Helvetica", 20), bg="#05020a", fg="#ffe8a0", insertbackground="#ffe8a0", justify="center", relief="flat", highlightthickness=1, highlightbackground="#ffe8a0")
    ENTRY_BOX.place(relx=0.5, rely=0.5, anchor="center", width=W*0.6, height=H*0.06)
    ENTRY_BOX.focus_set()
    ENTRY_BOX.bind("<Return>", process_onboarding_input)

def process_onboarding_input(event):
    global ENTRY_BOX
    text = ENTRY_BOX.get().strip()
    
    if ONBOARDING["step"] == 1:
        PRIOR["name"] = text if text else "Friend"
        ONBOARDING["step"] = 2
        ENTRY_BOX.delete(0, tk.END)
    elif ONBOARDING["step"] == 2:
        PRIOR["age"] = text
        ONBOARDING["step"] = 3
        ENTRY_BOX.delete(0, tk.END)
    elif ONBOARDING["step"] == 3:
        PRIOR["location"] = text
        ONBOARDING["step"] = 4
        ENTRY_BOX.destroy()
        ENTRY_BOX = None
        
        ONBOARDING["active"] = False
        save_state(MOOD["current"], INTERO["chamber_strain"])
        
        n = PRIOR.get("name", "Friend")
        DIALOGUE_QUEUE["lines"] = [
            ("Vertex", f"Hello {n}. I am Vertex."),
            ("Solon", f"I am Solon. Welcome."),
            ("Lumen", f"I am Lumen. It is good to meet you, {n}."),
            ("Prism", f"Hello. I am Prism."),
            ("Ripple", f"Ripple here. The chamber feels warmer now that you are here.")
        ]
        DIALOGUE_QUEUE["index"] = 0; DIALOGUE_QUEUE["t"] = 0.0; DIALOGUE_QUEUE["active"] = True; DIALOGUE_QUEUE["current_seat"] = None
        STATUS_TEXT["text"] = f"The chamber is ready, {n}."
        canvas.focus_set()

if PRIOR["visits"] == 0 or PRIOR["name"] == "":
    root.after(1000, start_onboarding)

_hrs_since = (time.time() - PRIOR["last_seen"]) / 3600.0 if PRIOR["last_seen"] > 0 else 0
if _hrs_since > 12.0 and random.random() < 0.3:
    CURRENT_BIOME = "forest" if PRIOR["biome"] == "water" else "water"
else:
    CURRENT_BIOME = PRIOR["biome"]

if CURRENT_BIOME not in ["water", "forest", "beach", "castle"]: CURRENT_BIOME = "water"

if os.path.exists(WEIGHTS_PATH):
    try:
        with open(WEIGHTS_PATH) as f:
            d = json.load(f)
            for s in SEATS:
                if s in d: SEAT_NETS[s].load_dict(d[s])
    except Exception: pass

_carry = clamp(1.0 - (time.time() - PRIOR["last_seen"]) / 172800.0, 0.0, 1.0) if PRIOR["last_seen"] > 0 else 0.0
MOOD["current"] = clamp(PRIOR["mood"]*_carry + 0.55*(1.0-_carry), 0.10, 0.98)
VALENCE["level"] = clamp(PRIOR["valence"]*_carry + 0.5*(1.0-_carry), 0.0, 1.0)
STRAIN = {s: PRIOR["strain"] for s in SEATS}

for k, b in UI_BUTTONS.items():
    b["active"] = (k == CURRENT_BIOME)

# ============ SENSORS ============
def read_extero():
    now = time.localtime(); h = now.tm_hour
    if   5 <= h < 11: rhythm = "morning"
    elif 11 <= h < 16: rhythm = "midday"
    elif 16 <= h < 21: rhythm = "evening"
    else:             rhythm = "night"
    EXTERO["hour"]=h; EXTERO["rhythm"]=rhythm
    try:
        for d in os.listdir("/sys/class/power_supply"):
            p = "/sys/class/power_supply/" + d
            if os.path.exists(p + "/capacity"):
                with open(p + "/capacity") as f: EXTERO["battery"]=int(f.read().strip())
                if os.path.exists(p + "/status"):
                    with open(p + "/status") as f: EXTERO["charging"] = f.read().strip().lower() in ("charging","full")
                break
    except Exception: pass

def update_intero():
    INTERO["session_mins"] = (time.time() - START_TIME) / 60.0
    INTERO["session_warmth"] = clamp(INTERO["session_mins"] / 30.0, 0.0, 1.0)

def touch_energy():
    if EXTERO["touch_at"] <= 0: return 0.0
    return clamp(1.0 - (time.time() - EXTERO["touch_at"]) / 15.0, 0.0, 1.0)

def compute_mood_target():
    b = EXTERO["battery"]; b_score = 0.5 if b is None else 0.75 if EXTERO["charging"] else 0.70 if b >= 70 else 0.55 if b >= 40 else 0.35 if b >= 15 else 0.20
    m = INTERO["session_mins"]; s_score = 0.75 if m < 5 else 0.60 if m < 20 else 0.45 if m < 45 else 0.35
    t = (0.72*0.45 if EXTERO["rhythm"]=="morning" else 0.52*0.45 if EXTERO["rhythm"]=="evening" else 0.68*0.45) + b_score*0.20 + s_score*0.20 + 0.15 + (INTERO["session_warmth"]*0.05)
    if not EXTERO["focused"]: t *= 0.55
    t += (VALENCE["level"] - 0.5) * 0.10
    MOOD["target"] = clamp(t, 0.15, 0.95)

def update_mood(dt):
    MOOD["drift_phase"] += dt * 0.3; drift = math.sin(MOOD["drift_phase"]) * 0.02
    MOOD["current"] += (MOOD["target"] + drift - MOOD["current"]) * 0.018
    MOOD["current"] = clamp(MOOD["current"], 0.08, 0.98)

def update_strain(dt):
    base = clamp(INTERO["utterances_this_hour"] / 30.0, 0.0, 1.0) + (0.0 if not EXTERO["battery"] or EXTERO["battery"]>=25 else (25-EXTERO["battery"])/25.0*0.3)
    for seat in SEATS:
        STRAIN[seat] += (base * (0.6 + random.uniform(0,0.4)) - STRAIN[seat]) * 0.006
        STRAIN[seat] = clamp(STRAIN[seat], 0.0, 1.0)

def update_breath(dt):
    rate = (0.7 + MOOD["current"] * 0.7) * (1.0 - QUIET["level"] * 0.55)
    for seat in SEATS: BREATH[seat] += dt * (1.0 / SEAT_BREATH[seat]) * rate

def breath_offset(seat, amp=1.0): return math.sin(BREATH[seat] * 6.28) * amp
def update_bell(dt): BELL["phase"] += dt * (0.35 + MOOD["current"] * 0.35)
def bell_value(): return 0.5 + 0.5 * math.sin(BELL["phase"] * 6.28)
def night_amount(): return 0.55 if EXTERO["rhythm"] == "night" else 0.20 if EXTERO["rhythm"] == "evening" else 0.0

def update_quiet(dt):
    if any_stream_active(): QUIET["silent_since"] = time.time(); target = 0.0
    else: silent_for = time.time() - QUIET["silent_since"]; target = 1.0 if silent_for > 20.0 else 0.0
    QUIET["level"] += (target - QUIET["level"]) * 0.008
    QUIET["level"] = clamp(QUIET["level"], 0.0, 1.0)

def update_nessy(dt):
    NESSY["phase"] += dt * 0.6; NESSY["x"] += NESSY["speed"] * dt * 60
    if NESSY["x"] > W * 0.85: NESSY["x"] = -W * 0.1
    NESSY["dip"] = SURPRISE["smooth"] * 0.8
    NESSY["bright"] = sum(SEAT_NETS[s].confidence() for s in SEATS) / len(SEATS)

# ============ PARTICLES & LEVIATHANS ============
def spawn_particles(dt):
    global PARTICLES
    if random.random() < 0.8 * (1.0 - QUIET["level"]*0.5):
        if CURRENT_BIOME == "water":
            PARTICLES.append({"x": random.uniform(0, W), "y": H*1.05, "speed": random.uniform(1.0, 3.0), "r": random.uniform(1, 3), "col": hue(GLOW_COOL), "type": "bubble"})
        elif CURRENT_BIOME == "forest":
            PARTICLES.append({"x": random.uniform(-W*0.2, W*1.2), "y": -H*0.1, "speed": random.uniform(0.5, 1.5), "r": random.uniform(2, 4), "col": hue(GLOW_GREEN), "type": "leaf", "phase": random.uniform(0,6.28)})
        elif CURRENT_BIOME == "beach":
            PARTICLES.append({"x": -W*0.1, "y": random.uniform(H*0.2, H*0.9), "speed": random.uniform(2.0, 4.0), "r": random.uniform(1, 2), "col": hue(COAST_LIT), "type": "sand"})
        elif CURRENT_BIOME == "castle":
            PARTICLES.append({"x": random.uniform(0, W), "y": random.uniform(-H*0.1, H*0.2), "speed": random.uniform(0.2, 0.8), "r": random.uniform(1, 2), "col": hue(UI_COL), "type": "dust"})

    alive = []
    for p in PARTICLES:
        if p["type"] == "bubble":
            p["y"] -= p["speed"]
            if p["y"] > -20: alive.append(p)
        elif p["type"] == "leaf":
            p["y"] += p["speed"]
            p["x"] += math.sin(SCENE["t"]*2.0 + p["phase"]) * 2
            if p["y"] < H*1.1: alive.append(p)
        elif p["type"] == "sand":
            p["x"] += p["speed"]
            p["y"] -= 0.5
            if p["x"] < W*1.1: alive.append(p)
        elif p["type"] == "dust":
            p["y"] += p["speed"]
            p["x"] += math.sin(SCENE["t"] + p["r"]) * 0.5
            if p["y"] < H*1.1: alive.append(p)
    PARTICLES = alive

def update_leviathans(dt):
    global LEVIATHANS
    for lv in LEVIATHANS:
        lv["phase"] += dt * 0.1
        lv["x"] += lv["speed"] * dt * 60
        # Loop around
        if lv["x"] > W + lv["w"]: lv["x"] = -lv["w"]
        
        # Breathing scale
        lv["scale"] = 1.0 + math.sin(lv["phase"]) * 0.02
        
    # Spawn leviathans if none are active
    if len(LEVIATHANS) < 1 and random.random() < 0.005:
        kind = ""
        if CURRENT_BIOME == "water": kind = "whale"
        elif CURRENT_BIOME == "forest": kind = "eye"
        elif CURRENT_BIOME == "beach": kind = "sun"
        elif CURRENT_BIOME == "castle": kind = "gear"
        
        LEVIATHANS.append({
            "kind": kind,
            "x": -W*0.5,
            "y": random.uniform(H*0.1, H*0.3),
            "w": W * random.uniform(0.6, 1.0),
            "h": H * random.uniform(0.3, 0.6),
            "speed": random.uniform(0.1, 0.3), # Very slow
            "phase": random.uniform(0, 6.28),
            "scale": 1.0,
            "col": hue("#0a0418")
        })

def draw_leviathans():
    for lv in LEVIATHANS:
        # Draw massive background silhouettes
        x, y = cam(lv["x"], lv["y"])
        w, h = lv["w"] * lv["scale"], lv["h"] * lv["scale"]
        
        if lv["kind"] == "whale":
            # Massive shadow blob
            canvas.create_oval(x-w*0.5, y-h*0.5, x+w*0.5, y+h*0.5, fill=lv["col"], outline="", stipple="gray25", tags="leviathan")
            canvas.create_polygon(x-w*0.3, y-h*0.4, x-w*0.6, y-h*0.6, x-w*0.5, y-h*0.2, fill=lv["col"], outline="", stipple="gray25", tags="leviathan")
        elif lv["kind"] == "eye":
            # Massive floating eye
            canvas.create_oval(x-w*0.5, y-h*0.5, x+w*0.5, y+h*0.5, fill=lv["col"], outline="", stipple="gray25", tags="leviathan")
            canvas.create_oval(x-w*0.1, y-h*0.1, x+w*0.1, y+h*0.1, fill=hue(GLOW_WARM), outline="", stipple="gray50", tags="leviathan")
        elif lv["kind"] == "sun":
            # Massive glowing sun
            canvas.create_oval(x-w*0.5, y-h*0.5, x+w*0.5, y+h*0.5, fill=lv["col"], outline="", stipple="gray12", tags="leviathan")
            canvas.create_oval(x-w*0.4, y-h*0.4, x+w*0.4, y+h*0.4, fill=hue(GLOW_WARM), outline="", stipple="gray25", tags="leviathan")
        elif lv["kind"] == "gear":
            # Massive gear (simplified as a circle with blocky teeth)
            canvas.create_oval(x-w*0.5, y-h*0.5, x+w*0.5, y+h*0.5, fill=lv["col"], outline="", stipple="gray25", tags="leviathan")
            canvas.create_oval(x-w*0.2, y-h*0.2, x+w*0.2, y+h*0.2, fill=hue(WATER_BOT), outline="", tags="leviathan")

def draw_particles():
    for p in PARTICLES:
        cx, cy = cam(p["x"], p["y"])
        canvas.create_oval(cx-p["r"], cy-p["r"], cx+p["r"], cy+p["r"], fill=p["col"], outline="", stipple="gray50", tags="dyn")

# ============ BIOME ENGINE ============
WORLD_SPAN = W*3.0; NEAR_SPAN = W*4.0; FOREGROUND_SPAN = W*4.5
STAR_DATA = []; FAR_DATA = []; MID_DATA = []; NEAR_DATA = []; FOREGROUND_DATA = []

def generate_biome_data(biome_name):
    global STAR_DATA, FAR_DATA, MID_DATA, NEAR_DATA, FOREGROUND_DATA, LEVIATHANS
    STAR_DATA = []; FAR_DATA = []; MID_DATA = []; NEAR_DATA = []; FOREGROUND_DATA = []
    PARTICLES.clear()
    LEVIATHANS.clear() # Clear old leviathans on biome shift
    
    if biome_name == "water":
        rng = random.Random(606)
        for _ in range(46): STAR_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),"y":rng.uniform(0.02,0.45)*H,"r":rng.uniform(0.5,1.3),"phase":rng.uniform(0,6.28),"speed":rng.uniform(0.3,0.8)})
        rng = random.Random(101)
        for i in range(14): FAR_DATA.append({"kind":rng.choice(["hump","peak","slab"]),"wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.10,0.40),"h":H*rng.uniform(0.03,0.14),"colour":rng.choice(["#3a0a18","#4a1030","#5a1a3a"]),"seed":rng.randint(0,9999)})
        rng = random.Random(201)
        for i in range(10): MID_DATA.append({"kind":rng.choice(["rock","spire"]),"wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.05,0.22),"h":H*rng.uniform(0.07,0.18),"colour":rng.choice(["#1a0408","#280810","#380c18"]),"seed":rng.randint(0,9999)})
        rng = random.Random(808)
        for _ in range(14): NEAR_DATA.append({"kind":rng.choice(["kelp","grass","frond"]),"wx":rng.uniform(0,NEAR_SPAN),"h":H*rng.uniform(0.18,0.55),"w":W*rng.uniform(0.018,0.055),"blades":rng.randint(3,6),"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
        rng = random.Random(909)
        for _ in range(8): FOREGROUND_DATA.append({"kind":rng.choice(["kelp","grass","spire"]),"wx":rng.uniform(0,FOREGROUND_SPAN),"h":H*rng.uniform(0.25,0.50),"w":W*rng.uniform(0.025,0.045),"blades":rng.randint(4,7),"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
    elif biome_name == "forest":
        rng = random.Random(303)
        for _ in range(20): STAR_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),"y":rng.uniform(0.05,0.30)*H,"r":rng.uniform(0.5,1.0),"phase":rng.uniform(0,6.28),"speed":rng.uniform(0.1,0.4)})
        rng = random.Random(404)
        for i in range(14): FAR_DATA.append({"kind":rng.choice(["hump","peak"]),"wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.20,0.50),"h":H*rng.uniform(0.05,0.15),"colour":rng.choice(["#0a2018","#103020","#184028"]),"seed":rng.randint(0,9999)})
        rng = random.Random(505)
        for i in range(10): MID_DATA.append({"kind":"trunk","wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.03,0.05),"h":H*rng.uniform(0.40,0.70),"colour":rng.choice(["#0a0505","#140a08"]),"seed":rng.randint(0,9999)})
        rng = random.Random(606)
        for _ in range(14): NEAR_DATA.append({"kind":rng.choice(["fern","bush"]),"wx":rng.uniform(0,NEAR_SPAN),"h":H*rng.uniform(0.15,0.40),"w":W*rng.uniform(0.04,0.08),"blades":rng.randint(5,10),"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
        rng = random.Random(707)
        for _ in range(8): FOREGROUND_DATA.append({"kind":rng.choice(["root","trunk"]),"wx":rng.uniform(0,FOREGROUND_SPAN),"h":H*rng.uniform(0.4,0.8),"w":W*rng.uniform(0.04,0.08),"blades":rng.randint(2,4),"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
    elif biome_name == "beach":
        rng = random.Random(111)
        for _ in range(30): STAR_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),"y":rng.uniform(0.05,0.35)*H,"r":rng.uniform(0.5,1.0),"phase":rng.uniform(0,6.28),"speed":rng.uniform(0.2,0.5)})
        rng = random.Random(222)
        for i in range(8): FAR_DATA.append({"kind":"dune","wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.30,0.60),"h":H*rng.uniform(0.05,0.15),"colour":rng.choice(["#e07050","#d06040","#c05030"]),"seed":rng.randint(0,9999)})
        rng = random.Random(333)
        for i in range(6): MID_DATA.append({"kind":"palm","wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.02,0.04),"h":H*rng.uniform(0.30,0.50),"colour":rng.choice(["#3a2010","#4a2818"]),"seed":rng.randint(0,9999)})
        rng = random.Random(444)
        for _ in range(12): NEAR_DATA.append({"kind":"beachgrass","wx":rng.uniform(0,NEAR_SPAN),"h":H*rng.uniform(0.10,0.25),"w":W*rng.uniform(0.02,0.05),"blades":rng.randint(3,5),"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
        rng = random.Random(555)
        for _ in range(6): FOREGROUND_DATA.append({"kind":"driftwood","wx":rng.uniform(0,FOREGROUND_SPAN),"h":H*rng.uniform(0.05,0.15),"w":W*rng.uniform(0.06,0.10),"blades":2,"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
    elif biome_name == "castle":
        rng = random.Random(777)
        for _ in range(15): STAR_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),"y":rng.uniform(0.05,0.30)*H,"r":rng.uniform(0.4,0.8),"phase":rng.uniform(0,6.28),"speed":rng.uniform(0.1,0.3)})
        rng = random.Random(888)
        for i in range(10): FAR_DATA.append({"kind":"spire","wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.10,0.20),"h":H*rng.uniform(0.15,0.30),"colour":rng.choice(["#1a1028","#2a1838","#3a2048"]),"seed":rng.randint(0,9999)})
        rng = random.Random(999)
        for i in range(8): MID_DATA.append({"kind":"tower","wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.05,0.08),"h":H*rng.uniform(0.40,0.60),"colour":rng.choice(["#2a2028","#3a3038"]),"seed":rng.randint(0,9999)})
        rng = random.Random(1010)
        for i in range(6): MID_DATA.append({"kind":"wall","wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.10,0.20),"h":H*rng.uniform(0.20,0.30),"colour":rng.choice(["#181018","#2a2028"]),"seed":rng.randint(0,9999)})
        rng = random.Random(1212)
        for _ in range(10): NEAR_DATA.append({"kind":"pillar","wx":rng.uniform(0,NEAR_SPAN),"h":H*rng.uniform(0.20,0.50),"w":W*rng.uniform(0.02,0.04),"blades":1,"phase":0,"seed":rng.randint(0,9999)})
        rng = random.Random(1313)
        for _ in range(6): FOREGROUND_DATA.append({"kind":"pillar","wx":rng.uniform(0,FOREGROUND_SPAN),"h":H*rng.uniform(0.40,0.70),"w":W*rng.uniform(0.04,0.07),"blades":1,"phase":0,"seed":rng.randint(0,9999)})

generate_biome_data(CURRENT_BIOME)

def floor_top_y(wx): 
    return FLOOR_Y + math.sin(wx*0.0075)*H*0.010 + math.sin(wx*0.019+1.3)*H*0.005 + math.sin(wx*0.041+2.7)*H*0.002

def _haze(col, t): return lerp(col, hue(HAZE), t)
def _darken_by_quiet(col, amount=0.35): return lerp(col, "#000000", QUIET["level"] * amount)
def _valence_tint(col):
    v = VALENCE["level"]
    if v > 0.55: return lerp(col, hue(GLOW_WARM), (v - 0.55) * 0.75)
    if v < 0.45: return lerp(col, hue(GLOW_COOL), (0.45 - v) * 0.60)
    return col

def draw_gradient(top_color, high_color, mid_color, low_color, deep_color, bot_color):
    stops = [(0.00,hue(top_color)),(0.14,hue(high_color)),(0.40,hue(mid_color)),(0.68,hue(low_color)),(0.88,hue(deep_color)),(1.00,hue(bot_color))]
    pulse = 0.97 + 0.03 * math.sin(PULSE["phase"]); te = touch_energy()
    for i in range(60):
        t = i/60; col = stops[-1][1]
        for j in range(len(stops)-1):
            if stops[j][0] <= t <= stops[j+1][0]:
                col = lerp(stops[j][1], stops[j+1][1], (t-stops[j][0])/(stops[j+1][0]-stops[j][0])); break
        col = lerp("#000000", col, pulse)
        if te > 0.01: col = lerp(col, hue(GLOW_WARM), te*0.06)
        col = _darken_by_quiet(col, 0.40); col = _valence_tint(col)
        canvas.create_rectangle(0, int(H*t), W, int(H*(i+1)/60)+2, fill=col, outline="", tags="bg")

def draw_god_rays(ray_color):
    intensity = (0.14 + MOOD["current"] * 0.20) * 0.5
    intensity *= (1.0 - night_amount()*0.60) * (1.0 - QUIET["level"] * 0.85)
    if intensity < 0.02: return
    src_x = LIGHT_X + math.sin(SCENE["t"]*0.05)*W*0.15
    for i in range(4):
        rx = src_x + (i-1.5)*W*0.10 + math.sin(SCENE["t"]*0.3 + i*1.7)*W*0.008
        col = lerp(hue(WATER_BOT), hue(ray_color), intensity*0.70)
        canvas.create_polygon(rx-W*0.025, SURFACE_Y, rx+W*0.025, SURFACE_Y, rx+W*0.14, SURFACE_Y+H*0.72, rx-W*0.14, SURFACE_Y+H*0.72, fill=col, outline="", stipple="gray50", tags="bg")

def draw_far(layer_color_haze):
    sx_off = SCENE["scroll_x"]*0.25
    for it in FAR_DATA:
        sx = (it["wx"] - sx_off) % WORLD_SPAN
        if sx > W+it["w"]: sx -= WORLD_SPAN
        if sx < -it["w"] or sx > W+it["w"]: continue
        rng = random.Random(it["seed"]); k = it["kind"]; base_y = floor_top_y(it["wx"]) - H*0.004
        col = _darken_by_quiet(_haze(it["colour"], layer_color_haze), 0.5)
        
        if k == "slab": 
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=col, outline="", tags="bg"); continue
        elif k == "dune":
            pts = []
            for i in range(9):
                f = i/8; shape = math.sin(f*math.pi)**1.5
                pts.extend([sx - it["w"]*0.5 + it["w"]*f, base_y - it["h"]*shape])
            pts.extend([sx+it["w"]*0.5, base_y]); pts.extend([sx-it["w"]*0.5, base_y])
            canvas.create_polygon(*pts, fill=col, outline="", smooth=True, tags="bg")
            continue
        elif k == "spire":
            pts = [(sx-it["w"]*0.5, base_y), (sx-it["w"]*0.1, base_y-it["h"]), (sx, base_y-it["h"]*1.2), (sx+it["w"]*0.1, base_y-it["h"]), (sx+it["w"]*0.5, base_y)]
            canvas.create_polygon(*[c for p in pts for c in p], fill=col, outline="", tags="bg")
            continue
            
        pts = []
        for i in range(9):
            f = i/8; shape = math.sin(f*math.pi)**(0.6 if k=="peak" else 1.0) + rng.uniform(-0.06,0.06)
            pts.extend([sx - it["w"]*0.5 + it["w"]*f, base_y - it["h"]*shape])
        pts.extend([sx+it["w"]*0.5, base_y]); pts.extend([sx-it["w"]*0.5, base_y])
        canvas.create_polygon(*pts, fill=col, outline="", smooth=True, tags="bg")

def draw_floor(floor_color, lip_color, dark_color, deep_color):
    steps = 60; top = [(W*i/steps, floor_top_y(W*i/steps + SCENE["scroll_x"])) for i in range(steps+1)]
    poly = []
    for (x,y) in top: poly.extend([x,y])
    poly.extend([W,H]); poly.extend([0,H])
    canvas.create_polygon(*poly, fill=_darken_by_quiet(hue(floor_color),0.35), outline="", tags="bg")
    lip = []
    for (x,y) in top: lip.extend([x,y])
    for (x,y) in reversed(top): lip.extend([x, y+H*0.006])
    canvas.create_polygon(*lip, fill=_darken_by_quiet(hue(lip_color),0.35), outline="", tags="bg")
    for off, col in [(0.055,_darken_by_quiet(hue(dark_color),0.35)), (0.12,_darken_by_quiet(hue(deep_color),0.35))]:
        band = []
        for i in range(steps+1): band.extend([W*i/steps, floor_top_y(W*i/steps + SCENE["scroll_x"]) + H*off])
        band.extend([W,H]); band.extend([0,H])
        canvas.create_polygon(*band, fill=col, outline="", tags="bg")

def draw_mid(layer_color_haze):
    sx_off = SCENE["scroll_x"]*0.55
    for it in MID_DATA:
        sx = (it["wx"] - sx_off) % WORLD_SPAN
        if sx > W+it["w"]: sx -= WORLD_SPAN
        if sx < -it["w"] or sx > W+it["w"]: continue
        rng = random.Random(it["seed"]); k = it["kind"]; base_y = floor_top_y(it["wx"]) - H*0.002
        col = _darken_by_quiet(_haze(it["colour"], layer_color_haze), 0.5)
        
        if k == "trunk": 
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=col, outline="", tags="bg"); continue
        elif k == "palm":
            canvas.create_line(sx, base_y, sx - it["w"]*0.2, base_y-it["h"], fill=col, width=max(2,int(it["w"])), tags="bg")
            for a in [-0.6, -0.2, 0.2, 0.6]:
                fx = sx - it["w"]*0.2 + math.sin(a)*it["w"]*1.5
                fy = base_y - it["h"] + math.cos(a)*it["h"]*0.1
                canvas.create_polygon(sx-it["w"]*0.2, base_y-it["h"], fx, fy, fx-it["w"]*0.5, fy+it["h"]*0.1, fill=col, outline="", tags="bg")
            continue
        elif k == "tower":
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=col, outline="", tags="bg")
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"]-it["w"]*0.2, sx-it["w"]*0.2, base_y-it["h"], fill=col, outline="", tags="bg")
            canvas.create_rectangle(sx+it["w"]*0.2, base_y-it["h"]-it["w"]*0.2, sx+it["w"]*0.5, base_y-it["h"], fill=col, outline="", tags="bg")
            continue
        elif k == "wall":
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=col, outline="", tags="bg")
            for i in range(4):
                bx = sx - it["w"]*0.5 + (it["w"]/4)*i
                canvas.create_rectangle(bx, base_y-it["h"]-it["w"]*0.1, bx+it["w"]*0.1, base_y-it["h"], fill=col, outline="", tags="bg")
            continue
            
        pts = []
        for i in range(9):
            f = i/8; shape = math.sin(f*math.pi)**(0.4 if k=="spire" else 0.75) + rng.uniform(-0.08,0.08)
            pts.extend([sx - it["w"]*0.5 + it["w"]*f, base_y - it["h"]*shape])
        pts.extend([sx+it["w"]*0.5, base_y]); pts.extend([sx-it["w"]*0.5, base_y])
        canvas.create_polygon(*pts, fill=col, outline="", smooth=True, tags="bg")

def draw_near(base_color):
    sx_off = SCENE["scroll_x"]*1.15; base_y = H*1.02
    for it in NEAR_DATA:
        sx = (it["wx"] - sx_off) % NEAR_SPAN
        if sx > W+it["w"]*3: sx -= NEAR_SPAN
        if sx < -it["w"]*3 or sx > W+it["w"]*3: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        
        if k == "pillar":
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=base_color, outline="", tags="near")
            canvas.create_rectangle(sx-it["w"]*0.6, base_y-it["h"]-it["w"]*0.1, sx+it["w"]*0.6, base_y-it["h"], fill=base_color, outline="", tags="near")
            continue
        elif k in ("kelp","grass","fern","beachgrass"):
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2) * it["w"] * 0.4
                sway = math.sin(SCENE["t"]*0.8*(1.0 - QUIET["level"]*0.6) + it["phase"] + j)*W*0.022
                pts = [(sx+off+sway*(k2/7)**2, base_y - it["h"]*(k2/7)) for k2 in range(8)]
                canvas.create_line(*[c for p in pts for c in p], fill=base_color, width=max(2,int(W*0.016)), smooth=True, capstyle="round", tags="near")
        else:
            for j in range(it["blades"]):
                a = -math.pi/2 + (j - (it["blades"]-1)/2)*0.28; length = it["h"] * rng.uniform(0.7,1.0)
                canvas.create_line(sx, base_y, sx + math.cos(a)*length, base_y + math.sin(a)*length, fill=base_color, width=max(2,int(W*0.018)), smooth=True, capstyle="round", tags="near")

def draw_foreground(base_color):
    sx_off = SCENE["scroll_x"]*1.5; base_y = H*1.05
    for it in FOREGROUND_DATA:
        sx = (it["wx"] - sx_off) % FOREGROUND_SPAN
        if sx > W+it["w"]*3: sx -= FOREGROUND_SPAN
        if sx < -it["w"]*3 or sx > W+it["w"]*3: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        
        if k == "pillar":
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=base_color, outline="", tags="fg")
            continue
        elif k == "driftwood":
            canvas.create_polygon(sx-it["w"]*0.5, base_y, sx-it["w"]*0.2, base_y-it["h"], sx+it["w"]*0.2, base_y-it["h"]*0.8, sx+it["w"]*0.5, base_y, fill=base_color, outline="", smooth=True, tags="fg")
            continue
        elif k in ("kelp", "root"):
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2)*it["w"]*0.4
                sway = math.sin(SCENE["t"]*0.7*(1.0 - QUIET["level"]*0.6) + it["phase"] + j)*W*0.025
                pts = [(sx+off+sway*(k2/7)**2, base_y - it["h"]*(k2/7)) for k2 in range(8)]
                canvas.create_line(*[c for p in pts for c in p], fill=base_color, width=max(3,int(W*0.020)), smooth=True, capstyle="round", tags="fg")
        elif k == "grass":
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2)*it["w"]*0.35
                sway = math.sin(SCENE["t"]*1.2 + it["phase"] + j)*W*0.03
                pts = [(sx+off+sway*(k2/5), base_y - it["h"]*(k2/5)) for k2 in range(6)]
                canvas.create_line(*[c for p in pts for c in p], fill=base_color, width=max(3,int(W*0.022)), smooth=True, capstyle="round", tags="fg")
        elif k == "trunk":
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=base_color, outline="", tags="fg")
        else:
            pts = [(sx-it["w"]*0.5, base_y),(sx-it["w"]*0.3, base_y-it["h"]*0.5),(sx, base_y-it["h"]),(sx+it["w"]*0.3, base_y-it["h"]*0.5),(sx+it["w"]*0.5, base_y)]
            canvas.create_polygon(*[c for p in pts for c in p], fill=base_color, outline="", smooth=True, tags="fg")

def render_biome_background():
    canvas.delete("bg")
    canvas.delete("leviathan") # Clear massive layer
    
    if CURRENT_BIOME == "water":
        draw_gradient(WATER_TOP, WATER_HIGH, WATER_MID, WATER_LOW, WATER_DEEP, WATER_BOT)
        draw_leviathans() # Draw massive whale behind the rays
        draw_god_rays(GLOW_WARM); draw_far(0.30); draw_floor(SAND, SAND_LIT, SAND_DARK, SAND_DEEP); draw_mid(0.15)
    elif CURRENT_BIOME == "forest":
        draw_gradient(FOREST_TOP, FOREST_HIGH, FOREST_MID, FOREST_LOW, "#0a2018", FOREST_BOT)
        draw_leviathans() # Draw massive eye behind the rays
        draw_god_rays(GLOW_GREEN); draw_far(0.40); draw_floor(DIRT, DIRT_LIT, DIRT_DARK, DIRT_DEEP); draw_mid(0.25)
    elif CURRENT_BIOME == "beach":
        draw_gradient(BEACH_TOP, BEACH_HIGH, BEACH_MID, BEACH_LOW, BEACH_DEEP, BEACH_BOT)
        draw_leviathans() # Draw massive sun behind the rays
        draw_god_rays(GLOW_WARM); draw_far(0.20); draw_floor(COAST, COAST_LIT, COAST_DARK, COAST_DEEP); draw_mid(0.10)
    elif CURRENT_BIOME == "castle":
        draw_gradient(CASTLE_TOP, CASTLE_HIGH, CASTLE_MID, CASTLE_LOW, CASTLE_DEEP, CASTLE_BOT)
        draw_leviathans() # Draw massive gear behind the rays
        draw_god_rays(GLOW_COOL); draw_far(0.15); draw_floor(STONE, STONE_LIT, STONE_DARK, STONE_DEEP); draw_mid(0.05)

def render_biome_near():
    canvas.delete("near")
    draw_near("#080202" if CURRENT_BIOME == "water" else "#050201")

def render_biome_foreground():
    canvas.delete("fg")
    draw_foreground("#000000")

def update_scroll(dt):
    mood_speed = (0.5 + MOOD["current"]*0.9) * (1.0 - QUIET["level"]*0.7)
    SCENE["scroll_speed"] = mood_speed * (1.0 - INTERO["chamber_strain"]*0.4)
    SCENE["scroll_x"] += SCENE["scroll_speed"]*dt*60.0

# --- END OF CHUNK 1/3 ---

# ============ V7 CHUNK 2/3: AVATARS, GUESTS, & NEURAL COUNCIL ============
# Layers 6-11, 15, 19, 23-24. The bodies, the minds, and the 20-input logic.
# =======================================================================

def breath_offset(seat, amp=1.0):
    local_breath = math.sin(BREATH[seat] * 6.28)
    global_breath = math.sin(SCENE["t"] * 1.5)
    blended = local_breath * (1.0 - HARMONY["level"] * 0.8) + global_breath * (HARMONY["level"] * 0.8)
    return blended * amp

def make_creatures():
    specs = [
        {"seat":"Solon","scale":0.065,"name":"turtle"},
        {"seat":"Lumen","scale":0.055,"name":"jelly"},
        {"seat":"Vertex","scale":0.050,"name":"crab"},
        {"seat":"Prism","scale":0.055,"name":"angel"},
        {"seat":"Ripple","scale":0.055,"name":"seahorse"}
    ]
    for sp in specs:
        # This now uses the shifted Y coordinates from Chunk 1
        hx = W * SEAT_HOME_X[sp["seat"]]; hy = H * SEAT_HOME_Y[sp["seat"]]
        sp.update({
            "home_x":hx, "home_y":hy, "x":hx, "y":hy, "base_y":hy, 
            "dir":1, "phase":random.uniform(0,6.28), "wander_t":random.uniform(0,6.28), "lean":0.0,
            "zoom": 1.0, "zoom_target": 1.0
        })
        CREATURES.append(sp)

def update_creatures(dt):
    mood_speed = (0.7 + MOOD["current"] * 0.8) * (1.0 - QUIET["level"] * 0.75)
    spread = 0.8 + (1.0 - HARMONY["level"]) * 0.4
    
    for c in CREATURES:
        st = STRAIN[c["seat"]]
        smoothness = clamp(1.0 - st * 0.75, 0.20, 1.0)
        
        effective_home_x = 0.5 + (c["home_x"] - 0.5) * spread
        effective_home_y = 0.5 + (c["home_y"] - 0.5) * spread
        
        c["wander_t"] += dt * 0.20 * mood_speed * smoothness
        target_x = effective_home_x + math.sin(c["wander_t"]) * W * (0.030 + st * 0.020)
        
        if abs(target_x - c["x"]) > W * 0.02:
            new_dir = 1 if target_x > c["x"] else -1
            if new_dir != c["dir"]: c["dir"] = new_dir
                
        c["lean"] += (c["dir"] * min(1.0, abs(target_x - c["x"])/(W*0.03)) - c["lean"]) * (0.05 * smoothness)
        c["x"] += (target_x - c["x"]) * (0.008 * smoothness)
        
        c["phase"] += dt * 3.0 * mood_speed
        depth = (0.012 + MOOD["current"] * 0.010) * (1.0 - st * 0.40)
        c["y"] = effective_home_y + breath_offset(c["seat"], amp=1.0) * H * depth + st * H * 0.03
        
        c["x"] = clamp(c["x"], W*0.08, W*0.92)
        c["y"] = clamp(c["y"], H*0.15, H*0.85)

        # Dynamic Zoom Logic
        if DIALOGUE_QUEUE["current_seat"] == c["seat"] or any(st["seat"] == c["seat"] for st in STREAMS):
            c["zoom_target"] = 1.15
        else:
            c["zoom_target"] = 1.0
        c["zoom"] += (c["zoom_target"] - c["zoom"]) * 0.08

def _rim_offset(pts, dx, dy, amt): return [(px + dx*amt, py + dy*amt) for (px, py) in pts]
def _seat_rim(seat): return lerp(hue(SEAT_RIM[seat]), hue(GLOW_WARM), clamp(bell_value()*0.10 + VALENCE["level"]*0.15 + SEAT_NETS[seat].confidence()*0.10, 0.0, 0.45))
def _seat_pupil_radius(seat, base_r): return base_r * clamp(0.40 + 0.35 * (1.0 - SEAT_NETS[seat].confidence()) + 0.30 * SEAT_NETS[seat].last_out, 0.30, 1.05)

def draw_pulse_dot(cx, cy, r, seat):
    a = clamp(SEAT_NETS[seat].confidence() * 0.7 + SEAT_NETS[seat].last_out * 0.3, 0.0, 1.0)
    if a < 0.05: return
    col = hue(SEAT_RIM[seat]); body = hue(SEAT_BODY[seat])
    canvas.create_oval(cx-r*2.5, cy-r*2.5, cx+r*2.5, cy+r*2.5, fill=lerp(body, col, 0.15 * a), outline="", tags="dyn")
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=lerp(body, col, 0.90 * a), outline="", tags="dyn")

def draw_shadow(c):
    base_y = floor_top_y(c["x"] + SCENE["scroll_x"]) + H*0.02
    persp = get_perspective_scale(c["y"])
    rx = H * c["scale"] * 0.85 * ZOOM_FIXED * persp * c["zoom"]
    ry = H * c["scale"] * 0.14 * ZOOM_FIXED * persp * c["zoom"]
    col = "#050505" if CURRENT_BIOME in ("forest", "castle") else "#0a0208"
    canvas.create_oval(c["x"] - rx, base_y - ry, c["x"] + rx, base_y + ry, fill=col, outline="", tags="dyn")

def draw_solon(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H * ZOOM_FIXED * get_perspective_scale(y) * c["zoom"]
    breath = breath_offset("Solon", amp=0.06); lean = c["lean"]; y += breath * s * 0.12
    d = 1 
    body_h = hue(SEAT_BODY["Solon"]); rim = _seat_rim("Solon")
    shell = [(x-1.00*s,y+0.05*s),(x-0.85*s,y-0.30*s),(x-0.50*s,y-0.48*s),(x-0.10*s,y-0.55*s),(x+0.30*s,y-0.50*s),(x+0.60*s,y-0.35*s),(x+0.85*s,y-0.15*s),(x+0.95*s,y+0.05*s),(x+0.75*s,y+0.28*s),(x-0.70*s,y+0.30*s)]
    hx = x + d*1.18*s + lean*s*0.10; hy = y - 0.28*s
    head = [(x+d*0.85*s,y-0.42*s),(hx-d*0.18*s,hy-0.22*s),(hx+d*0.08*s,hy-0.16*s),(hx+d*0.16*s,hy+0.02*s),(hx+d*0.04*s,hy+0.18*s),(hx-d*0.16*s,hy+0.14*s),(x+d*0.85*s,y-0.12*s)]
    ldx, ldy = -0.4, -0.9
    canvas.create_polygon(*[p for pt in _rim_offset(shell,ldx,ldy,s*0.20) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in _rim_offset(head,ldx,ldy,s*0.20) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    belly = [(x-0.70*s,y+0.30*s),(x+0.75*s,y+0.28*s),(x+0.65*s,y+0.42*s),(x-0.60*s,y+0.44*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(belly,ldx,ldy,s*0.15) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in shell for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in belly for p in pt], fill=lerp(body_h,"#000000",0.25), outline="", smooth=True, tags="dyn")
    sc_col = lerp(body_h, rim, 0.18); scute_centers = []
    for sd in [(-0.55,-0.38,-0.20,-0.50,-0.10,-0.22,-0.48,-0.14),(-0.15,-0.53,0.18,-0.50,0.22,-0.22,-0.08,-0.16),(0.24,-0.48,0.55,-0.34,0.58,-0.14,0.28,-0.08)]:
        pts = [(x+sd[i]*s, y+sd[i+1]*s) for i in range(0,8,2)]
        canvas.create_polygon(*[p for pt in pts for p in pt], fill=sc_col, outline="", tags="dyn")
        scute_centers.append((sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts)))
    canvas.create_polygon(*[p for pt in head for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    er = s * 0.075; ex = hx - d*0.02*s; ey = hy - 0.05*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.85), outline="", tags="dyn")
    pr = _seat_pupil_radius("Solon", er * 0.85); canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")
    for (mx,my) in scute_centers: draw_pulse_dot(mx, my, s * 0.055, "Solon")
    flap = math.sin(c["phase"]*1.4)*0.12; fx0 = x + d*0.30*s; fy0 = y + 0.18*s; f_len = 1.30*s; f_ang = 0.60 + flap
    fx1 = fx0 - d*math.cos(f_ang)*f_len; fy1 = fy0 + math.sin(f_ang)*f_len
    flipper = [(fx0,fy0),(fx0-d*0.15*s,fy0+0.12*s),(fx1+d*0.06*s,fy1-0.10*s),(fx1,fy1+0.16*s),(fx1-d*0.10*s,fy1+0.22*s),(fx0-d*0.28*s,fy0+0.28*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(flipper,ldx,ldy,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in flipper for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    rx0 = x - d*0.82*s; ry0 = y + 0.20*s; rx1 = rx0 - d*0.30*s; ry1 = ry0 + 0.32*s
    rudder = [(rx0,ry0),(rx1-d*0.10*s,ry1-0.05*s),(rx1,ry1+0.08*s),(rx0+d*0.10*s,ry0+0.18*s)]
    canvas.create_polygon(*[p for pt in rudder for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")

LUMEN_BELL_PAL = [(0.0,"#5a48c8"),(0.30,"#8a5ad0"),(0.55,"#c860a0"),(0.78,"#e08070"),(1.0,"#f0a860")]
LUMEN_SPARKS = [{"age":random.uniform(0,1.0),"lane":i%3,"speed":random.uniform(0.5,0.8)} for i in range(5)]

def _grad_colour(stops, t):
    if t <= stops[0][0]: return stops[0][1]
    if t >= stops[-1][0]: return stops[-1][1]
    for i in range(len(stops)-1):
        if stops[i][0] <= t <= stops[i+1][0]:
            loc = (t-stops[i][0])/(stops[i+1][0]-stops[i][0]) if stops[i+1][0]>stops[i][0] else 0
            return lerp(stops[i][1],stops[i+1][1],loc)
    return stops[-1][1]

def draw_lumen(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H * ZOOM_FIXED * get_perspective_scale(y) * c["zoom"]
    breath = breath_offset("Lumen", amp=0.20); r = s * (1.0 + breath * 0.22)
    d = c["dir"]; lean = c["lean"]; lx = d * lean * r * 0.15
    body_h = hue(SEAT_BODY["Lumen"]); rim = _seat_rim("Lumen")
    left = x - r*1.15 - lx; right = x + r*1.15 - lx
    def bell_top(xx):
        dx = (xx - (x-lx))/r; return y - r*(0.80 - 0.45*dx*dx - 0.30*abs(dx))
    def bell_bot(xx):
        dx = (xx - (x-lx))/r; return y + r*(0.10 - 0.05*dx*dx)
    for k in range(24):
        fx0 = k/24; fx1 = (k+1)/24; x0 = left + (right-left)*fx0; x1 = left + (right-left)*fx1; mid_x = (x0+x1)/2
        col = lerp(_grad_colour(LUMEN_BELL_PAL, fx0), rim, 0.35)
        canvas.create_rectangle(x0, bell_top(mid_x)-r*0.10, x1, bell_bot(mid_x)-r*0.05, fill=col, outline="", tags="dyn")
    for k in range(24):
        fx0 = k/24; fx1 = (k+1)/24; x0 = left + (right-left)*fx0; x1 = left + (right-left)*fx1; mid_x = (x0+x1)/2
        col = lerp(_grad_colour(LUMEN_BELL_PAL, fx0), body_h, 0.55)
        canvas.create_rectangle(x0, bell_top(mid_x), x1, bell_bot(mid_x), fill=col, outline="", tags="dyn")
    er = s * 0.06; ex = x - lx; ey = y - r*0.45
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.85), outline="", tags="dyn")
    pr = _seat_pupil_radius("Lumen", er * 0.85); canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")
    for sp in LUMEN_SPARKS:
        sp["age"] += 0.012 * sp["speed"] * (1.0 - QUIET["level"]*0.7)
        if sp["age"] > 1.0: sp["age"] = 0.0; sp["speed"] = random.uniform(0.5,0.8); sp["lane"] = random.randint(0,2)
        lane_off = (sp["lane"]-1) * r * 0.35; px = x - lx + lane_off + math.sin(SCENE["t"]*2.0 + sp["lane"])*r*0.05
        py = y + r*0.10 - sp["age"] * r*0.80; fade = math.sin(sp["age"] * math.pi)
        pulse_a = clamp(SEAT_NETS["Lumen"].confidence() * 0.7 + SEAT_NETS["Lumen"].last_out * 0.3, 0.0, 1.0)
        rr = r * (0.045 + 0.030 * pulse_a) * fade
        if rr < 0.4: continue
        canvas.create_oval(px-rr*2.6, py-rr*2.6, px+rr*2.6, py+rr*2.6, fill=lerp(rim, hue(WATER_BOT), 0.55), outline="", tags="dyn")
        canvas.create_oval(px-rr, py-rr, px+rr, py+rr, fill="#ffffff", outline="", tags="dyn")
    for i in range(5):
        offset = (i - 2.0) * r * 0.30; phase = i * 0.6; pts = []
        for k in range(26):
            f = k/25; wave = math.sin(SCENE["t"]*1.6 + phase - f*4.2); amp = r * (0.05 + 0.35 * math.sin(f*3.14))
            ox = x - lx + offset + d*lean*f*r*0.15; pts.append((ox + wave*amp, y + r*4.5*f, f))
        for k in range(len(pts)-1):
            f0 = pts[k][2]; col = lerp(_grad_colour(LUMEN_BELL_PAL, f0), body_h, 0.30); w = max(1, int(r * 0.06 * (1 - 0.35*f0)))
            canvas.create_line(pts[k][0], pts[k][1], pts[k+1][0], pts[k+1][1], fill=col, width=w, capstyle="round", tags="dyn")

VERTEX_BODY = [(0.0,"#5a1a70"),(0.25,"#8a2a8a"),(0.50,"#c85090"),(0.75,"#e87870"),(1.0,"#ffd060")]

def draw_vertex(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H * ZOOM_FIXED * 0.9 * get_perspective_scale(y) * c["zoom"]
    breath = breath_offset("Vertex", amp=0.10); s *= (1.0 + breath * 0.20)
    d = c["dir"]; lean = c["lean"]; lx = d * lean * s * 0.10
    body_h = hue(SEAT_BODY["Vertex"]); rim = _seat_rim("Vertex")
    for side in (-1, 1):
        for i in range(3):
            base_y = y + s*(0.25 + i*0.24); base_x = x + lx + side*s*0.55
            scurry = math.sin(SCENE["t"]*6.0 + i*1.0 + side*0.7) * (1.0 - QUIET["level"]*0.8)
            knee_x = x + lx + side*s*(1.15 + scurry*0.05); knee_y = base_y - s*0.05 + i*s*0.06 + scurry*s*0.04
            tip_x  = x + lx + side*s*(1.55 + scurry*0.10); tip_y  = base_y + s*0.55 + scurry*s*0.10
            canvas.create_line(base_x+(-0.4*s*0.18), base_y+(-0.9*s*0.18), knee_x+(-0.4*s*0.18), knee_y+(-0.9*s*0.18), fill=rim, width=max(2,int(s*0.09)), capstyle="round", tags="dyn")
            canvas.create_line(knee_x+(-0.4*s*0.18), knee_y+(-0.9*s*0.18), tip_x+(-0.4*s*0.18), tip_y+(-0.9*s*0.18), fill=rim, width=max(2,int(s*0.08)), capstyle="round", tags="dyn")
            canvas.create_line(base_x, base_y, knee_x, knee_y, fill=lerp(body_h,"#000000",0.4), width=max(2,int(s*0.075)), capstyle="round", tags="dyn")
            canvas.create_line(knee_x, knee_y, tip_x, tip_y, fill=lerp(body_h,"#000000",0.4), width=max(2,int(s*0.065)), capstyle="round", tags="dyn")
    rx = s*1.08; ry = s*0.74; ys = int(y-ry); ye = int(y+ry)
    canvas.create_oval(x+lx-rx-s*0.16, y-ry-s*0.16, x+lx+rx+s*0.16, y+ry+s*0.16, fill=rim, outline="", tags="dyn")
    for yy in range(ys, ye+1):
        f = (yy-ys)/max(1, ye-ys); dy = (yy-y)/ry
        if abs(dy) >= 1: continue
        hw = rx * math.sqrt(1 - dy*dy); col = lerp(_grad_colour(VERTEX_BODY, f), body_h, 0.55)
        canvas.create_line(x+lx-hw, yy, x+lx+hw, yy, fill=col, width=1, tags="dyn")
    rng = random.Random(int(c["home_x"]) + 11); pulse_a = clamp(SEAT_NETS["Vertex"].confidence() * 0.7 + SEAT_NETS["Vertex"].last_out * 0.3, 0.0, 1.0)
    for _ in range(14):
        dx = rng.uniform(-0.85,0.85)*s; dy = rng.uniform(-0.55,0.55)*s
        if (dx/(1.08*s))**2 + (dy/(0.74*s))**2 > 1: continue
        rr = s * rng.uniform(0.025,0.045); base_col = rng.choice([hue("#fff8d0"), hue("#ffe8a0"), hue("#c8e8ff")])
        col = lerp(base_col, hue(SEAT_RIM["Vertex"]), pulse_a * 0.7)
        canvas.create_oval(x+lx+dx-rr, y+dy-rr, x+lx+dx+rr, y+dy+rr, fill=col, outline="", tags="dyn")
    for ex in (-0.42, 0.42):
        bx = x + lx + ex * s; by = y - s*0.28; tx = bx + d * lean * s * 0.10; ty = by - s*0.55
        canvas.create_line(bx, by, tx, ty, fill=lerp(body_h,"#000000",0.5), width=max(1,int(s*0.06)), tags="dyn")
        rr = s * 0.13; canvas.create_oval(tx-rr, ty-rr, tx+rr, ty+rr, fill=lerp(body_h,"#ffffff",0.85), outline="", tags="dyn")
        pr = _seat_pupil_radius("Vertex", rr * 0.85); canvas.create_oval(tx-pr, ty-pr, tx+pr, ty+pr, fill="#050510", outline="", tags="dyn")

PRISM_BODY = [(0.0,"#8a4818"),(0.30,"#c87820"),(0.55,"#ffd060"),(0.78,"#ffe8a0"),(1.0,"#fff8d8")]

def draw_prism(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H * ZOOM_FIXED * get_perspective_scale(y) * c["zoom"]
    breath = breath_offset("Prism", amp=0.04); d = c["dir"]; lean = c["lean"]; lx = d * lean * s * 0.08; y += breath * s * 0.1
    body_h = hue(SEAT_BODY["Prism"]); rim = _seat_rim("Prism")
    pts = [(x+0.42*s+lx,y),(x+0.28*s+lx,y-0.50*s),(x+0.05*s+lx,y-0.85*s),(x-0.10*s+lx,y-1.00*s),(x-0.30*s+lx,y-0.75*s),(x-0.55*s+lx,y-0.30*s),(x-0.60*s+lx,y),(x-0.55*s+lx,y+0.30*s),(x-0.30*s+lx,y+0.75*s),(x-0.10*s+lx,y+1.00*s),(x+0.05*s+lx,y+0.85*s),(x+0.28*s+lx,y+0.50*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(pts,-0.4,-0.9,s*0.20) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    tail_up = [(x-0.10*s+lx,y-1.00*s),(x+0.05*s+lx+d*lean*s*0.10,y-1.40*s),(x-0.20*s+lx+d*lean*s*0.15,y-1.85*s),(x-0.65*s+lx,y-1.35*s),(x-0.55*s+lx,y-0.30*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(tail_up,-0.4,-0.9,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    tail_dn = [(x-0.10*s+lx,y+1.00*s),(x+0.05*s+lx+d*lean*s*0.10,y+1.40*s),(x-0.20*s+lx+d*lean*s*0.15,y+1.85*s),(x-0.65*s+lx,y+1.35*s),(x-0.55*s+lx,y+0.30*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(tail_dn,-0.4,-0.9,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in tail_up for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in tail_dn for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    ys = [p[1] for p in pts]; y_min, y_max = min(ys), max(ys); y_rng = max(1, y_max - y_min); n = len(pts)
    for yy in range(int(y_min), int(y_max)+1):
        f = (yy-y_min)/y_rng; xs = []
        for i in range(n):
            p0 = pts[i]; p1 = pts[(i+1)%n]
            if p1[1] != p0[1] and min(p0[1],p1[1]) <= yy <= max(p0[1],p1[1]):
                loc = (yy-p0[1])/(p1[1]-p0[1]); xs.append(p0[0] + (p1[0]-p0[0])*loc)
        if len(xs) >= 2:
            xs.sort(); col = lerp(_grad_colour(PRISM_BODY, f), body_h, 0.60); canvas.create_line(xs[0], yy, xs[-1], yy, fill=col, width=1, tags="dyn")
    er = s * 0.09; ex = x + lx + 0.18*s; ey = y - 0.22*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.9), outline="", tags="dyn")
    pr = _seat_pupil_radius("Prism", er * 0.85); canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")
    for f in (0.2, 0.5, 0.8): draw_pulse_dot(x-s*0.3, y-s*(1.0-f*2.0), s*0.05, "Prism")

RIPPLE_PAL = [(0.0,"#ffb8d8"),(0.15,"#ff80b8"),(0.35,"#e060b0"),(0.55,"#b058c0"),(0.75,"#8050b8"),(1.0,"#5038a0")]

def draw_ripple(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H * ZOOM_FIXED * get_perspective_scale(y) * c["zoom"]
    breath = breath_offset("Ripple", amp=0.08); d = c["dir"]; lean = c["lean"]; lx = d * lean * s * 0.06; y += breath * s * 0.3
    body_h = hue(SEAT_BODY["Ripple"]); rim = _seat_rim("Ripple")
    tail_pts = [(x-0.08*s+lx,y+0.50*s),(x-0.20*s+lx,y+0.72*s),(x-0.32*s+lx,y+0.95*s),(x-0.28*s+lx,y+1.18*s),(x-0.05*s+lx,y+1.28*s),(x+0.20*s+lx,y+1.18*s),(x+0.30*s+lx,y+0.98*s),(x+0.20*s+lx,y+0.82*s),(x+0.00*s+lx,y+0.78*s),(x-0.10*s+lx,y+0.86*s),(x-0.10*s+lx,y+0.98*s),(x-0.02*s+lx,y+1.04*s)]
    for k in range(len(tail_pts)-1):
        f0 = k/(len(tail_pts)-1); x1, y1 = tail_pts[k]; x2, y2 = tail_pts[k+1]
        w = max(2, int(s*0.16 * (1.0 - 0.70*f0)))
        canvas.create_line(x1-0.4*s*0.16, y1-0.9*s*0.16, x2-0.4*s*0.16, y2-0.9*s*0.16, fill=rim, width=w, capstyle="round", tags="dyn")
        col = lerp(_grad_colour(RIPPLE_PAL, 0.85 + 0.15*((f0+(k+1)/(len(tail_pts)-1))/2)), body_h, 0.55)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w, capstyle="round", tags="dyn")
    body_pts = [(x+0.10*s+lx,y-0.85*s),(x+0.15*s+lx,y-0.55*s),(x+0.30*s+lx,y-0.15*s),(x+0.24*s+lx,y+0.20*s),(x+0.10*s+lx,y+0.50*s),(x-0.10*s+lx,y+0.50*s),(x-0.22*s+lx,y+0.15*s),(x-0.26*s+lx,y-0.20*s),(x-0.26*s+lx,y-0.55*s),(x-0.22*s+lx,y-0.82*s),(x-0.14*s+lx,y-0.88*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(body_pts,-0.4,-0.9,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    ys = [p[1] for p in body_pts]; y_min, y_max = min(ys), max(ys); y_rng = max(1, y_max - y_min); n = len(body_pts)
    for yy in range(int(y_min), int(y_max)+1):
        f = (yy-y_min)/y_rng; xs = []
        for i in range(n):
            p0 = body_pts[i]; p1 = body_pts[(i+1)%n]
            if p1[1] != p0[1] and min(p0[1],p1[1]) <= yy <= max(p0[1],p1[1]):
                loc = (yy-p0[1])/(p1[1]-p0[1]); xs.append(p0[0] + (p1[0]-p0[0])*loc)
        if len(xs) >= 2:
            xs.sort(); col = lerp(_grad_colour(RIPPLE_PAL, f), body_h, 0.60); canvas.create_line(xs[0], yy, xs[-1], yy, fill=col, width=1, tags="dyn")
    hx = x + 0.05*s + lx + d * lean * s * 0.15; hy = y - 1.10*s - lean * s * 0.05
    head_pts = [(hx-0.20*s,hy+0.10*s),(hx-0.16*s,hy-0.24*s),(hx+0.02*s,hy-0.32*s),(hx+0.18*s,hy-0.22*s),(hx+0.32*s,hy-0.14*s),(hx+0.58*s,hy-0.16*s),(hx+0.74*s,hy-0.14*s),(hx+0.62*s,hy-0.02*s),(hx+0.32*s,hy+0.08*s),(hx+0.18*s,hy+0.20*s),(hx+0.05*s,hy+0.22*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(head_pts,-0.4,-0.9,s*0.16) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*head_pts, fill=lerp(_grad_colour(RIPPLE_PAL, 0.10), body_h, 0.55), outline="", smooth=True, tags="dyn")
    for i in range(7):
        bx = hx + (-0.05 + i*0.062)*s; by = hy - 0.35*s; peak = s*(0.20 if i % 2 == 1 else 0.10)
        canvas.create_polygon(bx-s*0.022, by, bx+s*0.010, by-peak, bx+s*0.022, by, fill=rim, outline="", tags="dyn")
    er = s * 0.058; ex = x + lx + 0.13*s; ey = y - 1.16*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.9), outline="", tags="dyn")
    pr = _seat_pupil_radius("Ripple", er * 0.85); canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")
    for f in (0.2, 0.5, 0.8):
        idx = int(f * (len(body_pts)-1)); idx = min(idx, len(body_pts)-2); local = f * (len(body_pts)-1) - idx
        px = body_pts[idx][0] + (body_pts[idx+1][0]-body_pts[idx][0])*local; py = body_pts[idx][1] + (body_pts[idx+1][1]-body_pts[idx][1])*local
        draw_pulse_dot(px, py, s * 0.045, "Ripple")

CREATURE_DRAW = {"turtle":draw_solon,"jelly":draw_lumen,"crab":draw_vertex,"angel":draw_prism,"seahorse":draw_ripple}

def draw_creatures():
    for c in CREATURES:
        cx, cy = cam(c["x"], c["y"])
        save = (c["x"], c["y"]); c["x"], c["y"] = cx, cy
        draw_shadow(c)
        c["x"], c["y"] = save
    for c in CREATURES:
        cx, cy = cam(c["x"], c["y"])
        save = (c["x"], c["y"]); c["x"], c["y"] = cx, cy
        CREATURE_DRAW[c["name"]](c)
        c["x"], c["y"] = save

# ============ GUEST ENGINE ============
GUEST_LIBRARY = {
    "stranger_fish": {"color": "#80ffe0", "scale": 0.08, "shape": "fish"},
    "shore_frog": {"color": "#60ffd0", "scale": 0.06, "shape": "frog"},
    "rat": {"color": "#a0a0a0", "scale": 0.05, "shape": "rat"}
}

def spawn_guest(guest_type):
    if guest_type not in GUEST_LIBRARY: return
    info = GUEST_LIBRARY[guest_type]
    start_x = -W * 0.2 if random.random() < 0.5 else W * 1.2
    GUESTS.append({"type": guest_type, "x": start_x, "y": H * 0.5, "target_x": W * 0.5, "scale": info["scale"], "color": info["color"], "shape": info["shape"], "age": 0.0, "state": "entering", "timer": 0.0})

def update_guests(dt):
    global GUESTS
    alive = []
    for g in GUESTS:
        g["age"] += dt; g["timer"] += dt
        if g["state"] == "entering":
            g["x"] += (g["target_x"] - g["x"]) * 0.02
            if abs(g["x"] - g["target_x"]) < 10: g["state"] = "speaking"; g["timer"] = 0.0
        elif g["state"] == "speaking":
            if g["timer"] > 5.0 and not any_stream_active(): g["state"] = "leaving"; g["timer"] = 0.0
        elif g["state"] == "leaving":
            g["x"] -= W * 0.01
            if g["x"] < -W*0.2 or g["x"] > W*1.2: continue
        alive.append(g)
    GUESTS = alive

def draw_guests():
    for g in GUESTS:
        cx, cy = cam(g["x"], g["y"])
        s = g["scale"] * H * ZOOM_FIXED * get_perspective_scale(g["y"])
        col = hue(g["color"])
        fade = 1.0
        if g["state"] == "entering": fade = clamp((g["x"] - (-W*0.2)) / (W*0.7), 0.0, 1.0)
        elif g["state"] == "leaving": fade = clamp((g["x"] - (-W*0.2)) / (W*0.7), 0.0, 1.0)
        
        base_y = floor_top_y(g["x"] + SCENE["scroll_x"]) + H*0.02
        canvas.create_oval(cx-s*1.5, base_y-s*0.2, cx+s*1.5, base_y+s*0.2, fill="#050505", outline="", tags="dyn")
        
        if g["shape"] == "fish":
            canvas.create_oval(cx-s, cy-s*0.4, cx+s, cy+s*0.4, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_polygon(cx+s*0.8, cy, cx+s*1.5, cy-s*0.4, cx+s*1.5, cy+s*0.4, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_oval(cx-s*0.5, cy-s*0.1, cx-s*0.3, cy+s*0.1, fill=lerp("#050505", "#ffffff", fade), outline="", tags="dyn")
        elif g["shape"] == "frog":
            canvas.create_oval(cx-s, cy-s*0.5, cx+s, cy+s*0.5, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_oval(cx-s*0.8, cy-s*0.6, cx-s*0.4, cy-s*0.2, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_oval(cx+s*0.4, cy-s*0.6, cx+s*0.8, cy-s*0.2, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_oval(cx-s*0.7, cy-s*0.5, cx-s*0.5, cy-s*0.3, fill=lerp("#050505", "#ffffff", fade), outline="", tags="dyn")
            canvas.create_oval(cx+s*0.5, cy-s*0.5, cx+s*0.7, cy-s*0.3, fill=lerp("#050505", "#ffffff", fade), outline="", tags="dyn")
        elif g["shape"] == "rat":
            canvas.create_oval(cx-s*1.2, cy-s*0.4, cx+s*0.8, cy+s*0.4, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_oval(cx-s*0.2, cy-s*0.5, cx+s*0.2, cy-s*0.1, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_oval(cx-s*1.4, cy, cx-s*1.6, cy+s*0.2, fill=lerp("#050505", col, fade), outline="", tags="dyn")
            canvas.create_oval(cx-s*0.9, cy-s*0.1, cx-s*0.7, cy+s*0.1, fill=lerp("#050505", "#ffffff", fade), outline="", tags="dyn")

# ============ NEURAL COUNCIL LOGIC ============
def get_schema_state():
    container = 1.0 if EXTERO.get("focused") else 0.0
    agency = 1.0 if touch_energy() > 0.1 else 0.0
    part_whole = 1.0 if len(STREAMS) > 0 else 0.0
    return [container, agency, part_whole]

def update_arbiter():
    total_weight = 0.0
    for s in SEATS:
        net = SEAT_NETS[s]
        w = max(0.1, (net.confidence() * 1.5) - (net.loss * 2.0))
        net.attention = w
        total_weight += w
    if total_weight > 0:
        for s in SEATS: SEAT_NETS[s].attention *= (5.0 / total_weight)

def read_council_input():
    # 20 inputs total
    intero = [INTERO["session_warmth"], INTERO["chamber_strain"]]
    extero = [1.0 if EXTERO["focused"] else 0.0, touch_energy()]
    council = [SEAT_NETS[s].last_out for s in SEATS]
    schemas = get_schema_state()
    
    biome_water = 1.0 if CURRENT_BIOME == "water" else 0.0
    biome_forest = 1.0 if CURRENT_BIOME == "forest" else 0.0
    biome_beach = 1.0 if CURRENT_BIOME == "beach" else 0.0
    biome_castle = 1.0 if CURRENT_BIOME == "castle" else 0.0
    
    story_active = 1.0 if any_stream_active() else 0.0
    returning = 1.0 if PRIOR.get("visits", 0) > 1 else 0.0
    
    # V6 Banter & Social inputs
    banter_active = 1.0 if SCENE.get("is_banter") else 0.0
    social_story = 1.0 if SCENE.get("is_social") else 0.0
    
    return intero + extero + council + schemas + [biome_water, biome_forest, biome_beach, biome_castle, story_active, returning, banter_active, social_story]

def council_target(seat):
    base_target = 0.0
    
    # V6 Personality Adjustments (Vertex Lead, Solon Muted)
    if seat == "Solon":
        base_target = 0.1 if EXTERO["focused"] else 0.0
    elif seat == "Vertex":
        base_target = 1.0 
    elif seat == "Prism":
        base_target = 0.7 
    elif seat == "Lumen":
        base_target = 0.5
    elif seat == "Ripple":
        base_target = 0.5
        
    age_str = PRIOR.get("age", "0")
    try: age_val = int(age_str)
    except: age_val = 0
    
    if age_val > 0 and age_val < 18 and seat == "Prism": base_target += 0.15
    if age_val > 50 and seat == "Solon": base_target += 0.05
    if len(PRIOR.get("location", "")) > 1 and seat == "Lumen": base_target += 0.10

    if seat == "Ripple" and SCENE.get("last_biome") != CURRENT_BIOME:
        base_target += 0.25
        SCENE["last_biome"] = CURRENT_BIOME

    return clamp(base_target, 0.0, 1.0)

def update_council_nets(dt):
    x = read_council_input()
    update_arbiter()
    for seat in SEATS: SEAT_NETS[seat].step(x, council_target(seat))

def council_confidence(): return sum(SEAT_NETS[s].confidence() for s in SEATS) / len(SEATS)

def update_surprise(dt):
    total_surprise = 0.0; total_weight = 0.0
    for s in SEATS:
        net = SEAT_NETS[s]
        err = abs(net.last_out - net.last_target)
        total_surprise += err * net.attention; total_weight += net.attention
    SURPRISE["current"] = total_surprise / max(0.1, total_weight)
    SURPRISE["smooth"] += (SURPRISE["current"] - SURPRISE["smooth"]) * 0.05

def update_valence(dt):
    presence = 1.0 if EXTERO["focused"] else 0.0; activity = 1.0 if len(STREAMS) > 0 else 0.0
    target = (0.35 + presence*0.15 + activity*0.05 + council_confidence()*0.25 - SURPRISE["smooth"]*0.30 - QUIET["level"]*0.20)
    VALENCE["target"] = clamp(target, 0.0, 1.0); VALENCE["level"] += (VALENCE["target"] - VALENCE["level"]) * 0.008

def update_harmony(dt):
    outputs = [SEAT_NETS[s].last_out for s in SEATS]
    mean = sum(outputs) / len(outputs)
    variance = sum((x - mean) ** 2 for x in outputs) / len(outputs)
    target_harmony = 1.0 - clamp(variance * 12.0, 0.0, 1.0)
    HARMONY["target"] = target_harmony
    HARMONY["level"] += (HARMONY["target"] - HARMONY["level"]) * 0.05

# --- END OF CHUNK 2/3 ---

# ============ V7 CHUNK 3/3: STORY ENGINE, PHRASE ENGINE, & MAIN LOOP ============
# Layers 12-14, 16-18, 25-32. The soul, the banter, the V5 bubbles, and the loop.
# =======================================================================

RITUAL = {"active": False, "index": 0, "t": 0.0, "last_run": -999.0}
CRISIS = {"level": 0.0, "active": False, "last_trigger": 0.0}
BOOT_STATE = {"fired": False}

# ============ THE PHRASE ENGINE (MINI-MATRIX) ============
WORD_POOL = {
    "objects": ["a smooth stone", "an old shell", "a piece of green glass", "a feather", "a rusted nail", "a piece of dried kelp"],
    "places": ["under the big rock", "by the kelp", "in the dark trench", "on the dry sand", "near the surface", "in the castle hall"],
    "feelings": ["warm", "quiet", "strange", "familiar", "heavy", "soft"]
}

def generate_dynamic_story():
    obj = random.choice(WORD_POOL["objects"])
    plc = random.choice(WORD_POOL["places"])
    feel = random.choice(WORD_POOL["feelings"])
    
    food = PRIOR.get("fav_food", "")
    game = PRIOR.get("fav_game", "")
    
    if food and random.random() < 0.6:
        return [
            ("Vertex", f"I found {obj} {plc} today."),
            ("Lumen", "What was it like?"),
            ("Vertex", f"It felt {feel}. It reminded me of {food}."),
            ("Prism", "How does a stone remind you of that?"),
            ("Vertex", "It just does. The mind works in quiet ways.")
        ]
    elif game and random.random() < 0.6:
        return [
            ("Vertex", f"I was watching the sand {plc}."),
            ("Solon", "Watching what?"),
            ("Vertex", f"The way it moves. It looks like a game of {game}."),
            ("Ripple", "The world plays its own games."),
        ]
    else:
        return [
            ("Vertex", f"I found {obj} {plc}."),
            ("Lumen", "Did you keep it?"),
            ("Vertex", "No. I left it where it was."),
            ("Prism", "Why?"),
            ("Vertex", "Because it belonged there.")
        ]

# ============ THE STORY LIBRARY (SOCIAL & STATIC) ============
STORY_LIBRARY = [
    # --- SOCIAL THEMES ---
    {"name": "social_bully", "biome": "any", "trigger": "visitor_quiet", "social": True, "lines": [
        ("Vertex", "I saw someone push a smaller crab today."), ("Lumen", "Why did they do that?"),
        ("Vertex", "Because they were scared."), ("Prism", "Does fear make people mean?"), 
        ("Vertex", "Sometimes. But it doesn't have to.")
    ]},
    {"name": "social_hygiene", "biome": "any", "trigger": "morning", "social": True, "lines": [
        ("Lumen", "The water feels clean today."), ("Vertex", "I washed my shell."), 
        ("Prism", "Does it feel different?"), ("Vertex", "It feels lighter. And I can see the light better.")
    ]},
    {"name": "social_work", "biome": "any", "trigger": "high_strain", "social": True, "lines": [
        ("Vertex", "I have been moving stones all day."), ("Solon", "Why?"), 
        ("Vertex", "To build a wall."), ("Lumen", "A wall for what?"), 
        ("Vertex", "For a place to rest. But I am too tired to rest now."), ("Ripple", "Work is heavy when it has no end.")
    ]},
    {"name": "social_play", "biome": "any", "trigger": "visitor_quiet", "social": True, "lines": [
        ("Prism", "I found a shiny stone."), ("Vertex", "What will you do with it?"), 
        ("Prism", "Just look at it."), ("Solon", "Is that a game?"), 
        ("Prism", "Yes. It is the game of looking."), ("Ripple", "A small joy.")
    ]},
    {"name": "social_self_belief", "biome": "any", "trigger": "night", "social": True, "lines": [
        ("Prism", "The dark is very big."), ("Vertex", "It is."), 
        ("Prism", "I don't like it."), ("Vertex", "You don't have to like it. You just have to get through it."), 
        ("Lumen", "We are here with you."), ("Prism", "Okay. I can do that.")
    ]},

    # --- VERTEX STATIC STORIES ---
    {"name": "v_shadow", "biome": "any", "trigger": "night", "lines": [
        ("Vertex", "I watched the light move across the floor."), ("Lumen", "Did it change color?"),
        ("Vertex", "It went from grey to blue. Then it was gone."), ("Prism", "Where did it go?"), ("Vertex", "I don't know. But it will come back.")
    ]},
    {"name": "v_leaf", "biome": "forest", "trigger": "visitor_quiet", "lines": [
        ("Vertex", "A leaf fell on my shell today."), ("Lumen", "Did it stay?"), ("Vertex", "For a while. Then the wind took it."), ("Prism", "Where did it go?"), ("Vertex", "Somewhere else.")
    ]},
    {"name": "v_sand", "biome": "beach", "trigger": "morning", "lines": [
        ("Vertex", "The sand is cool this morning."), ("Solon", "The night air was cold."), ("Vertex", "It will warm up soon.")
    ]},
    {"name": "v_echo", "biome": "castle", "trigger": "night", "lines": [
        ("Vertex", "I heard a sound in the hall."), ("Lumen", "What kind of sound?"), ("Vertex", "Just a stone settling. But it echoed."), ("Ripple", "The walls remember.")
    ]},

    # --- SOLON STORIES (Nerfed) ---
    {"name": "s_sun", "biome": "any", "trigger": "morning", "lines": [
        ("Solon", "The sun is warm today."), ("Lumen", "It is."), ("Solon", "Good.")
    ]},

    # --- PRISM STORIES ---
    {"name": "p_hide", "biome": "any", "trigger": "visitor_quiet", "lines": [
        ("Prism", "I hid behind the big rock."), ("Vertex", "Why?"), ("Prism", "To see if anyone would look for me."), ("Lumen", "Did they?"), ("Prism", "Yes. You did.")
    ]},

    # --- RIPPLE STORIES ---
    {"name": "r_hour", "biome": "any", "trigger": "night", "lines": [
        ("Ripple", "The hour turns."), ("Solon", "The clock is ticking."), ("Ripple", "We are still here.")
    ]}
]

def select_story():
    if ONBOARDING["active"] or INQUIRY["active"]: return None

    # 1. Dynamic Story Check (25% chance if they have answered an inquiry)
    if (PRIOR.get("fav_food") or PRIOR.get("fav_game")) and random.random() < 0.25:
        lines = generate_dynamic_story()
        return {"name": "dynamic", "lines": lines, "trigger": "random", "social": False}

    triggers = []
    b = EXTERO.get("battery")
    
    if b is not None and b < 15 and not EXTERO.get("charging"): triggers.append("battery_low")
    if EXTERO.get("charging"): triggers.append("battery_charging")
    if INTERO["chamber_strain"] > 0.6: triggers.append("high_strain")
    if not EXTERO["focused"]: triggers.append("visitor_absent")
    if touch_energy() > 0.1: triggers.append("visitor_touch")
    if PRIOR.get("visits", 0) > 0 and INTERO["session_mins"] < 1.0: triggers.append("returning_visitor")
    if touch_energy() <= 0.1 and EXTERO["focused"]: triggers.append("visitor_quiet")
    if EXTERO["rhythm"] == "night": triggers.append("night")
    if EXTERO["rhythm"] == "morning": triggers.append("morning")
    if random.random() < 0.15: triggers.append("random")
    
    biome_stories = [s for s in STORY_LIBRARY if s["biome"] == CURRENT_BIOME or s["biome"] == "any"]
    
    # Prioritize Vertex for the first few stories of a session
    if INTERO["session_mins"] < 5.0:
        vertex_stories = [s for s in biome_stories if s["lines"][0][0] == "Vertex" and s["name"] not in PLAYED_STORIES]
        if vertex_stories: biome_stories = vertex_stories
    
    candidates = [s for s in biome_stories if s["trigger"] in triggers and s["name"] not in PLAYED_STORIES]
    if not candidates:
        candidates = [s for s in biome_stories if s["name"] not in PLAYED_STORIES]
    if not candidates:
        PLAYED_STORIES.clear()
        candidates = [s for s in biome_stories if s["trigger"] in triggers]
        if not candidates: candidates = biome_stories
        
    if len(candidates) > 1 and RHYTHM.get("last_seat"):
        filtered = [s for s in candidates if s["lines"][0][0] != RHYTHM["last_seat"]]
        if filtered: candidates = filtered
            
    choice = random.choice(candidates)
    PLAYED_STORIES.add(choice["name"])
    RHYTHM["last_seat"] = choice["lines"][0][0]
    return choice

def begin_next_event():
    if DIALOGUE_QUEUE["active"] or any_stream_active() or INQUIRY["active"]: return
    
    story = select_story()
    if not story: return
    
    # Check for Banter (30% chance for Vertex stories)
    if story["lines"][0][0] == "Vertex" and random.random() < 0.3:
        SCENE["is_banter"] = True
        banter_lines = [
            ("Vertex", "I have a story."),
            ("Prism", "Tell us!"),
            ("Solon", "*yawn* Here we go...")
        ]
        DIALOGUE_QUEUE["lines"] = banter_lines + story["lines"]
    else:
        SCENE["is_banter"] = False
        DIALOGUE_QUEUE["lines"] = list(story["lines"])
        
    SCENE["is_social"] = story.get("social", False)
        
    DIALOGUE_QUEUE["index"] = 0
    DIALOGUE_QUEUE["gap"] = 0.5 # Fast pacing
    DIALOGUE_QUEUE["t"] = 0.0
    DIALOGUE_QUEUE["active"] = True
    DIALOGUE_QUEUE["current_seat"] = None
    
    STATUS_TEXT["text"] = "The council is speaking."

# ============ THE INQUIRY SYSTEM ============
def start_inquiry():
    global ENTRY_BOX
    INQUIRY["active"] = True
    INQUIRY["step"] += 1
    INQUIRY["last_run"] = time.time()
    DIALOGUE_QUEUE["active"] = False
    STREAMS.clear()
    
    prompt = ""
    if INQUIRY["step"] == 1: prompt = "What is your favorite food?"
    elif INQUIRY["step"] == 2: prompt = "What is your favorite game?"
    elif INQUIRY["step"] == 3: prompt = "What is your favorite biome?"
    else: INQUIRY["active"] = False; return
    
    STATUS_TEXT["text"] = "The council has a question."
    ENTRY_BOX = tk.Entry(root, font=("Helvetica", 18), bg="#05020a", fg="#ffe8a0", insertbackground="#ffe8a0", justify="center", relief="flat", highlightthickness=1, highlightbackground="#ffe8a0")
    ENTRY_BOX.place(relx=0.5, rely=0.5, anchor="center", width=W*0.6, height=H*0.05)
    ENTRY_BOX.focus_set()
    ENTRY_BOX.bind("<Return>", process_inquiry_input)

def process_inquiry_input(event):
    global ENTRY_BOX
    text = ENTRY_BOX.get().strip()
    
    if INQUIRY["step"] == 1: PRIOR["fav_food"] = text
    elif INQUIRY["step"] == 2: PRIOR["fav_game"] = text
    elif INQUIRY["step"] == 3: 
        PRIOR["fav_biome"] = text
        if text.lower() in ["water", "pond"]: swap_biome("water")
        elif text.lower() in ["forest", "woods"]: swap_biome("forest")
        elif text.lower() in ["beach", "sand"]: swap_biome("beach")
        elif text.lower() in ["castle", "stone"]: swap_biome("castle")
    
    ENTRY_BOX.destroy()
    ENTRY_BOX = None
    INQUIRY["active"] = False
    save_state(MOOD["current"], INTERO["chamber_strain"])
    
    DIALOGUE_QUEUE["lines"] = [("Vertex", "Noted."), ("Lumen", "Thank you for telling us.")]
    DIALOGUE_QUEUE["index"] = 0; DIALOGUE_QUEUE["t"] = 0.0; DIALOGUE_QUEUE["active"] = True; DIALOGUE_QUEUE["current_seat"] = None
    STATUS_TEXT["text"] = "Edenshore"
    canvas.focus_set()

# ============ DIALOGUE ENGINE (V5 BUBBLES + HARD CEILING) ============
def chunk_text(text, max_chars=18):
    clauses = []; current = ""
    for ch in text:
        current += ch
        if ch in (",", ";", ":", ".", "?", "!", "—", "-"):
            clauses.append(current.strip()); current = ""
    if current.strip(): clauses.append(current.strip())
    chunks = []
    for clause in clauses:
        words = clause.split(); current = ""
        for w in words:
            if len(w) > max_chars:
                if current: chunks.append(current); current = ""
                for i in range(0, len(w), max_chars): chunks.append(w[i:i+max_chars])
                continue
            if not current: current = w
            elif len(current) + 1 + len(w) <= max_chars: current += " " + w
            else: chunks.append(current); current = w
        if current: chunks.append(current)
    return chunks

def spawn_stream(seat, text, stagger=0.8, bubble_life=5.0):
    if PRIOR.get("name"):
        text = text.replace("visitor", PRIOR["name"]).replace("Visitor", PRIOR["name"])
        
    creature = next((c for c in CREATURES if c["seat"] == seat), None)
    if not creature and seat != "Guest": return
    chunks = chunk_text(text)
    if not chunks: return
    start_x = creature["x"] if creature else W*0.5
    start_y = creature["y"] if creature else H*0.5
    STREAMS.append({"seat":seat,"colour":SEAT_COLOUR.get(seat, "#ffffff"),"chunks":chunks,"start_x":start_x,"start_y":start_y-H*0.05,"age":0.0,"bubbles":[],"spawned":set(),"stagger":stagger,"bubble_life":bubble_life})

def any_stream_active(): return len(STREAMS) > 0

def update_streams(dt):
    global STREAMS
    alive = []
    for st in STREAMS:
        st["age"] += dt
        for i, chunk in enumerate(st["chunks"]):
            if st["age"] >= i * st["stagger"] and i not in st["spawned"]:
                st["spawned"].add(i)
                arc_dir = 1 if st["start_x"] < W*0.5 else -1
                st["bubbles"].append({"i":i,"chunk":chunk,"birth":st["age"],"phase":random.uniform(0,6.28),"arc_dir":arc_dir})
        st["bubbles"] = [b for b in st["bubbles"] if (st["age"] - b["birth"]) < st["bubble_life"] + 0.5]
        if st["age"] < (len(st["chunks"])-1)*st["stagger"] + st["bubble_life"] + 2.0: alive.append(st)
    STREAMS = alive

def draw_streams():
    arc_cap = W*0.12
    for st in STREAMS:
        sx0 = st["start_x"]; sy0 = st["start_y"]; col = hue(st["colour"])
        
        # V7 Hard Ceiling: Calculate max rise based on starting height
        max_rise = max(H*0.1, sy0 - H*0.18)
        
        for b in st["bubbles"]:
            p = clamp((st["age"] - b["birth"])/st["bubble_life"], 0.0, 1.0)
            alpha = p/0.10 if p < 0.10 else (1.0-p)/0.20 if p > 0.80 else 1.0
            if alpha < 0.02: continue
            
            cy = sy0 - max_rise*math.sin(p*math.pi*0.5) # Capped rise
            cx = sx0 + clamp(b["arc_dir"]*arc_cap*math.sin(p*math.pi*0.85), -arc_cap, arc_cap) + math.sin(SCENE["t"]*1.4 + b["phase"])*W*0.005
            cx, cy = cam(cx, cy)
            fs = max(14, int(H * 0.020)); r = min(max(H * 0.055, len(b["chunk"]) * fs * 0.60 * 1.10), H * 0.100) * ZOOM_FIXED
            rim_col = lerp(col, hue(WATER_BOT), 0.40)
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="", outline=rim_col, width=max(1,int(r*0.012)), tags="dyn")
            hr = r*0.14; hx = cx - r*0.60; hy = cy - r*0.60
            canvas.create_oval(hx-hr, hy-hr, hx+hr, hy+hr, fill=lerp(hue(WATER_BOT), "#ffffff", alpha*0.85), outline="", tags="dyn")
            canvas.create_text(cx, cy, text=b["chunk"], fill=lerp(hue(WATER_BOT), hue(BUBBLE_TEXT), alpha), font=font_full(fs, True), tags="dyn")

def update_rhythm(dt):
    if ONBOARDING["active"] or INQUIRY["active"]: return
    
    if DIALOGUE_QUEUE["active"]:
        DIALOGUE_QUEUE["t"] += dt
        if DIALOGUE_QUEUE["current_seat"] is None:
            if DIALOGUE_QUEUE["t"] >= DIALOGUE_QUEUE["gap"]:
                if DIALOGUE_QUEUE["index"] >= len(DIALOGUE_QUEUE["lines"]):
                    DIALOGUE_QUEUE["active"] = False
                    STATUS_TEXT["text"] = "Edenshore"
                    return
                seat, text = DIALOGUE_QUEUE["lines"][DIALOGUE_QUEUE["index"]]
                spawn_stream(seat, text)
                DIALOGUE_QUEUE["current_seat"] = seat
                DIALOGUE_QUEUE["t"] = 0.0
                DIALOGUE_QUEUE["index"] += 1
        else:
            if not any_stream_active() and DIALOGUE_QUEUE["t"] >= 0.4:
                DIALOGUE_QUEUE["current_seat"] = None
                DIALOGUE_QUEUE["t"] = 0.0
        return

    if any_stream_active() or RITUAL["active"] or CRISIS["active"]:
        return
    
    if INTERO["session_mins"] - RITUAL["last_run"] > 20.0:
        RITUAL["active"] = True; RITUAL["index"] = 0; RITUAL["t"] = 0.0; RITUAL["last_run"] = INTERO["session_mins"]; return
        
    if not BOOT_STATE["fired"] and (time.time() - START_TIME) >= 0.5:
        BOOT_STATE["fired"] = True; begin_next_event(); return
        
    RHYTHM["time_since_last_story"] += dt
    if RHYTHM["time_since_last_story"] > 3.0:
        RHYTHM["time_since_last_story"] = 0.0
        if INQUIRY["step"] < 3 and (time.time() - INQUIRY["last_run"]) > 120.0:
            start_inquiry()
        else:
            begin_next_event()

def update_ritual(dt):
    if not RITUAL["active"]: return
    RITUAL["t"] += dt
    if RITUAL["t"] > 1.5:
        if RITUAL["index"] >= 5: RITUAL["active"] = False; return
        seats = ["Solon", "Vertex", "Lumen", "Prism", "Ripple"]
        lines = ["Time is passing.", "Noted.", f"Is {PRIOR.get('name','the visitor')} still there?", "It happens every time.", "The hour turns. We are still here."]
        spawn_stream(seats[RITUAL["index"]], lines[RITUAL["index"]], stagger=0.8, bubble_life=4.0)
        RITUAL["index"] += 1; RITUAL["t"] = 0.0

def check_crisis():
    b = EXTERO["battery"]; low_bat = (b is not None and b < 5 and not EXTERO["charging"]); high_strain = (INTERO["chamber_strain"] > 0.95)
    if (low_bat or high_strain) and not CRISIS["active"]:
        CRISIS["active"] = True; CRISIS["last_trigger"] = time.time(); STREAMS.clear(); DIALOGUE_QUEUE["active"] = False
        STATUS_TEXT["text"] = "The chamber is struggling."
    elif not low_bat and not high_strain and CRISIS["active"]:
        if time.time() - CRISIS["last_trigger"] > 30.0: CRISIS["active"] = False

def update_crisis(dt):
    if not CRISIS["active"]: return
    CRISIS["level"] += (1.0 - CRISIS["level"]) * 0.05
    if not any_stream_active() and random.random() < 0.01:
        text = random.choice(["It is getting dark.", "We can wait here.", "You can put the phone down.", "We will stay."])
        spawn_stream("Ripple", text, stagger=1.5, bubble_life=6.0); CRISIS["last_trigger"] = time.time()

def update_biome_reactor(dt):
    if HARMONY["level"] < 0.3: BIOME_REACTOR["weather"] = "fog"
    else: BIOME_REACTOR["weather"] = "calm"
        
    if BIOME_REACTOR["weather"] == "fog":
        BIOME_REACTOR["timer"] += dt
        if BIOME_REACTOR["timer"] > 10.0 and HARMONY["level"] > 0.5:
            BIOME_REACTOR["timer"] = 0.0; BIOME_REACTOR["weather"] = "calm"

# ============ BIOME SWAP & UI BUTTONS ============
def swap_biome(new_biome):
    global CURRENT_BIOME
    if new_biome == CURRENT_BIOME: return
    CURRENT_BIOME = new_biome
    generate_biome_data(CURRENT_BIOME)
    
    for k, b in UI_BUTTONS.items():
        target = {"pond":"water", "forest":"forest", "beach":"beach", "castle":"castle"}[k]
        b["active"] = (target == CURRENT_BIOME)
    
    STATUS_TEXT["text"] = f"The {CURRENT_BIOME} is awake."
    RHYTHM["time_since_last_story"] = 0.0
    STREAMS.clear()
    DIALOGUE_QUEUE["active"] = False

def draw_ui_buttons():
    for key, btn in UI_BUTTONS.items():
        col = hue(GLOW_WARM) if btn["active"] else lerp(hue(WATER_BOT), UI_COL, 0.30)
        canvas.create_rectangle(btn["x"]-W*0.10, btn["y"]-H*0.03, btn["x"]+W*0.10, btn["y"]+H*0.03, fill="#000000", outline="", stipple="gray25", tags="ui")
        canvas.create_text(btn["x"], btn["y"], text=btn["text"], fill=col, font=font_full(H*0.022, True), tags="ui")

def render_ui():
    canvas.delete("ui")
    draw_ui_buttons()

# ============ INPUT ============
_last_touch_xy = [None, None]

def on_press(e):
    if ONBOARDING["active"] or INQUIRY["active"]: return

    for key, btn in UI_BUTTONS.items():
        if abs(e.x - btn["x"]) < W*0.12 and abs(e.y - btn["y"]) < H*0.05:
            target = {"pond":"water", "forest":"forest", "beach":"beach", "castle":"castle"}[key]
            swap_biome(target)
            return

    now = time.time()
    EXTERO["touch_x"]=e.x; EXTERO["touch_y"]=e.y; EXTERO["touch_at"]=now; EXTERO["touch_count_session"] += 1; INTERO["been_touched"]=True; _last_touch_xy[0]=e.x; _last_touch_xy[1]=e.y

def on_motion(e):
    if _last_touch_xy[0] is not None:
        _last_touch_xy[0]=e.x; _last_touch_xy[1]=e.y; EXTERO["touch_x"]=e.x; EXTERO["touch_y"]=e.y; EXTERO["touch_at"]=time.time()

def on_focus_in(e=None): EXTERO["focused"]=True
def on_focus_out(e=None): EXTERO["focused"]=False

canvas.bind("<Button-1>", on_press)
canvas.bind("<B1-Motion>", on_motion)
canvas.bind("<ButtonRelease-1>", lambda e: _last_touch_xy.__setitem__(0, None))
root.bind("<FocusIn>", on_focus_in)
root.bind("<FocusOut>", on_focus_out)

# ============ NESSY ============
def _nessy_arc(cx, base_y, rx, ry, steps=20):
    return [(cx + math.cos(math.pi*(1 - i/steps))*rx, base_y - math.sin(math.pi*(1 - i/steps))*ry) for i in range(steps+1)]
def _nessy_rim_body(pts, offset, rim_col, body_col):
    canvas.create_polygon(*[p for pt in [(x+offset[0], y+offset[1]) for x,y in pts] for p in pt], fill=rim_col, outline="", smooth=True, tags="nessy")
    canvas.create_polygon(*[p for pt in pts for p in pt], fill=body_col, outline="", smooth=True, tags="nessy")

def draw_nessy():
    s = H * 0.055 * ZOOM_FIXED
    cx, cy = cam(NESSY["x"], H * 0.13 + NESSY["dip"] * H * 0.04)
    rim = hue(NESSY_RIM_BASE) if NESSY["bright"] <= 0.02 else lerp(hue(NESSY_RIM_BASE), hue(GLOW_WARM), NESSY["bright"] * 0.5)
    hump_r = s * 1.0
    for i in range(3):
        hx = cx - s * 1.05 * (i + 1)
        _nessy_rim_body(_nessy_arc(hx, cy + s*0.05, hump_r, hump_r * 0.95), (0,-6), rim, NESSY_BODY)
    neck_pts = []
    for i in range(17):
        f = i / 16; y = cy + s*0.05 - f * s * 2.5; curve = (math.sin(f * math.pi * 1.2) * s * 0.55 - f * s * 0.15); x_center = cx + s * 0.15 + curve; w = s * (0.55 - f * 0.25)
        neck_pts.append((x_center - w, y))
    for i in range(16, -1, -1):
        f = i / 16; y = cy + s*0.05 - f * s * 2.5; curve = (math.sin(f * math.pi * 1.2) * s * 0.55 - f * s * 0.15); x_center = cx + s * 0.15 + curve; w = s * (0.55 - f * 0.25)
        neck_pts.append((x_center + w, y))
    _nessy_rim_body(neck_pts, (0, -5), rim, NESSY_BODY)
    head_cx = cx + s * 0.15 + (math.sin(math.pi * 1.2) * s * 0.55 - s * 0.15); head_cy = cy + s*0.05 - s * 2.5
    head_pts = [(head_cx-s*0.35, head_cy+s*0.10),(head_cx-s*0.25, head_cy-s*0.22),(head_cx+s*0.05, head_cy-s*0.28),(head_cx+s*0.45, head_cy-s*0.20),(head_cx+s*0.70, head_cy-s*0.08),(head_cx+s*0.45, head_cy+s*0.06),(head_cx+s*0.05, head_cy+s*0.14),(head_cx-s*0.25, head_cy+s*0.16)]
    _nessy_rim_body(head_pts, (0, -4), rim, NESSY_BODY)
    er = s * 0.045
    canvas.create_oval(head_cx+s*0.25-er, head_cy-s*0.05-er, head_cx+s*0.25+er, head_cy-s*0.05+er, fill=lerp(hue(GLOW_WARM), "#ffffff", NESSY["bright"]*0.6), outline="", tags="nessy")
    for i in range(3):
        hx = cx - s * 1.05 * (i + 1)
        canvas.create_oval(hx - s*0.7, cy + s*0.10, hx + s*0.7, cy + s*0.34, fill=hue("#3a1028"), outline="", tags="nessy")

def draw_touch_glow():
    te = touch_energy()
    if te < 0.05: return
    cx, cy = cam(EXTERO["touch_x"], EXTERO["touch_y"])
    base_r = min(W,H)*0.022; r = base_r*(0.45 + 0.55*te)
    col = lerp(hue(GLOW_COOL), hue(GLOW_WARM), 0.35 + MOOD["current"]*0.55)
    canvas.create_oval(cx-r*2, cy-r*2, cx+r*2, cy+r*2, fill=lerp(hue(WATER_BOT), col, te*0.10), outline="", tags="dyn")
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=lerp(hue(WATER_BOT), col, te*0.45), outline="", tags="dyn")

# ============ RENDER PASSES ============
def render_background():
    render_biome_background()
    if STATUS_TEXT["text"]:
        canvas.create_text(W/2, 40, text=STATUS_TEXT["text"], fill="white", font=font_full(H*0.022, True), tags="bg")
    
    if ONBOARDING["active"]:
        canvas.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray50", outline="", tags="bg")
        prompt = ""
        if ONBOARDING["step"] == 1: prompt = "What is your name?"
        elif ONBOARDING["step"] == 2: prompt = "How old are you?"
        elif ONBOARDING["step"] == 3: prompt = "Where are you from?"
        canvas.create_text(W/2, H*0.4, text=prompt, fill=hue(GLOW_WARM), font=font_full(H*0.035, True), tags="bg")
        canvas.create_text(W/2, H*0.6, text="Press Enter to confirm", fill=UI_COL, font=font_full(H*0.018, False), tags="bg")

    if INQUIRY["active"]:
        canvas.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray50", outline="", tags="bg")
        prompt = ""
        if INQUIRY["step"] == 1: prompt = "What is your favorite food?"
        elif INQUIRY["step"] == 2: prompt = "What is your favorite game?"
        elif INQUIRY["step"] == 3: prompt = "What is your favorite biome?"
        canvas.create_text(W/2, H*0.4, text=prompt, fill=hue(GLOW_WARM), font=font_full(H*0.035, True), tags="bg")

def render_nessy():
    canvas.delete("nessy")
    draw_nessy()

def render_dynamic():
    canvas.delete("dyn")
    draw_particles()
    draw_creatures()
    draw_guests()
    draw_streams()
    draw_touch_glow()

def render_near(): render_biome_near()
def render_foreground(): render_biome_foreground()

# ============ BOOT & MAIN LOOP ============
make_creatures()

threading.Thread(target=_boot_audio, daemon=True).start()
print(f"[Edenshore] V7 online. Biome: {CURRENT_BIOME.upper()}. Name: {PRIOR.get('name','None')}")

LAST_TICK = [time.time()]
SHUTDOWN = {"saved": False}

def _final_save():
    if SHUTDOWN["saved"]: return
    SHUTDOWN["saved"] = True
    try: save_state(MOOD["current"], INTERO["chamber_strain"])
    except Exception: pass

def on_close():
    _final_save()
    try: root.destroy()
    except Exception: pass

root.protocol("WM_DELETE_WINDOW", on_close)

def tick():
    now = time.time(); dt = clamp(now - LAST_TICK[0], 0.01, 0.15); LAST_TICK[0] = now
    SCENE["t"] += dt; PULSE["phase"] += dt*0.4
    
    update_bell(dt); update_quiet(dt)
    read_extero(); update_intero(); compute_mood_target()
    update_mood(dt); update_strain(dt); update_breath(dt)
    
    update_scroll(dt)
    update_creatures(dt)
    update_guests(dt)
    spawn_particles(dt)
    update_leviathans(dt)
    
    update_council_nets(dt)
    update_surprise(dt)
    update_valence(dt)
    update_harmony(dt)
    update_arbiter()
    update_nessy(dt)
    
    update_biome_reactor(dt)
    check_crisis(); update_crisis(dt); update_ritual(dt)
    update_streams(dt); update_rhythm(dt)
    
    if now - SCENE["last_save"] > 20:
        SCENE["last_save"] = now
        save_state(MOOD["current"], INTERO["chamber_strain"])

    render_background()
    render_nessy()
    render_dynamic()
    render_near()
    render_foreground()
    render_ui() 
    
    root.after(50, tick)

render_background()
render_nessy()
render_ui()
try: tick()
finally: _final_save()
root.mainloop()

# ============ END EDEN WORLD-V7 ============
# --- END OF CHUNK 3/3 ---