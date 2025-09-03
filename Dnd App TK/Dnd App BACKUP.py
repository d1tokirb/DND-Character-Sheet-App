import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# --- Pillow is optional ---
try:
    from PIL import Image, ImageTk  # type: ignore
    PIL_AVAILABLE = True
except Exception:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False


class DnDCharacterSheet(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("D&D 5e Character Sheet")
        self.geometry("1920x1080")

        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        top_frame = tk.Frame(scroll_frame)
        top_frame.pack(fill="x", padx=10, pady=10)

        # Profile Picture
        self.profile_frame = tk.Frame(top_frame)
        self.profile_frame.pack(side="left", padx=5)

        # Default 48x48 gray image with circular mask:
        if PIL_AVAILABLE:
            default_img = Image.new("RGB", (48, 48), color="gray")
            mask = Image.new("L", (48, 48), 0)
            draw = Image.new("L", (48, 48), 0)
            from PIL import ImageDraw
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 48, 48), fill=255)
            default_img.putalpha(mask)
            self.profile_photo = ImageTk.PhotoImage(default_img)
        else:
            self.profile_photo = tk.PhotoImage(width=48, height=48)
            try:
                # fill the whole area with a light gray
                self.profile_photo.put("gray80", to=(0, 0, 48, 48))
            except Exception:
                pass

        self.profile_label = tk.Label(self.profile_frame, image=self.profile_photo, width=48, height=48)
        self.profile_label.pack()
        self.profile_label.bind("<Button-1>", lambda e: self.change_profile_picture())

        # Character Name
        self.name_var = tk.StringVar(value="Character Name")
        tk.Label(top_frame, text="Name:").pack(side="left")
        self.name_entry = tk.Entry(top_frame, textvariable=self.name_var, font=("Arial", 14), width=20)
        self.name_entry.pack(side="left", padx=5)

        # Character Class
        self.class_var = tk.StringVar(value="Select Class")
        classes = [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
            "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
            "Warlock", "Wizard"
        ]
        self.class_dropdown = ttk.Combobox(top_frame, textvariable=self.class_var, values=classes, state="readonly", width=15)
        self.class_dropdown.pack(side="left", padx=5)

        # Character Background
        self.background_var = tk.StringVar(value="Select Background")
        backgrounds = [
            "Acolyte", "Charlatan", "Criminal", "Entertainer", "Folk Hero",
            "Guild Artisan", "Hermit", "Noble", "Outlander", "Sage",
            "Sailor", "Soldier", "Urchin"
        ]
        self.background_dropdown = ttk.Combobox(top_frame, textvariable=self.background_var, values=backgrounds, state="readonly", width=20)
        self.background_dropdown.pack(side="left", padx=5)

        main_frame = tk.Frame(scroll_frame)
        main_frame.pack(fill="both", expand=True)

        # Ability Scores
        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(side="left", anchor="n", padx=10, pady=10, fill="both", expand=True)

        self.stats = {}
        self.stat_mod_labels = {}

        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

        for ability in abilities:
            row = tk.Frame(stats_frame)
            row.pack(anchor="w", pady=2)

            tk.Label(row, text=ability + ":").pack(side="left")

            var = tk.IntVar(value=10)
            entry = tk.Entry(row, textvariable=var, width=5)
            entry.pack(side="left", padx=5)

            mod_label = tk.Label(row, text="+0", width=4)
            mod_label.pack(side="left")

            var.trace_add("write", lambda *args, v=var, l=mod_label: self.update_modifier(v, l))

            self.stats[ability] = var
            self.stat_mod_labels[ability] = mod_label

        center_frame = tk.Frame(main_frame)
        center_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Health
        self.current_hp = tk.IntVar(value=20)
        self.max_hp = tk.IntVar(value=30)

        tk.Label(center_frame, text="Hit Points:").pack(anchor="w", pady=(0, 5))

        hp_frame = tk.Frame(center_frame)
        hp_frame.pack(fill="x", pady=(0, 10))

        self.current_hp_entry = tk.Entry(hp_frame, textvariable=self.current_hp, width=5)
        self.current_hp_entry.pack(side="left")

        tk.Label(hp_frame, text="/").pack(side="left")

        self.max_hp_entry = tk.Entry(hp_frame, textvariable=self.max_hp, width=5)
        self.max_hp_entry.pack(side="left")

        tk.Button(hp_frame, text="Update", command=self.update_health).pack(side="left", padx=10)

        self.hp_bar = ttk.Progressbar(center_frame, maximum=self.max_hp.get(), value=self.current_hp.get())
        self.hp_bar.pack(fill="x", pady=(0, 20))

        self.update_health()

        # Experience Points and Level
        self.current_xp = tk.IntVar(value=0)
        self.level = tk.IntVar(value=1)

        tk.Label(center_frame, text="Experience:").pack(anchor="w", pady=(0, 5))

        xp_frame = tk.Frame(center_frame)
        xp_frame.pack(fill="x")

        self.current_xp_entry = tk.Entry(xp_frame, textvariable=self.current_xp, width=7)
        self.current_xp_entry.pack(side="left")

        tk.Button(xp_frame, text="Update", command=self.update_xp).pack(side="left", padx=10)

        self.xp_bar = ttk.Progressbar(center_frame, maximum=300, value=self.current_xp.get())
        self.xp_bar.pack(fill="x", pady=5)

        self.level_label = tk.Label(center_frame, text=f"Level: {self.level.get()}")
        self.level_label.pack(anchor="w", pady=(0, 10))

        self.update_xp()

        # Skills and Proficiency Bonuses
        skills_frame = tk.Frame(main_frame)
        skills_frame.pack(side="right", anchor="n", padx=10, pady=10, fill="both", expand=True)

        tk.Label(skills_frame, text="Skills").pack(anchor="w")

        self.skills = {}
        skills_list = {
            "Strength": ["Athletics"],
            "Dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"],
            "Intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"],
            "Wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
            "Charisma": ["Deception", "Intimidation", "Performance", "Persuasion"]
        }

        for ability, skillnames in skills_list.items():
            for skill in skillnames:
                row = tk.Frame(skills_frame)
                row.pack(anchor="w", pady=1)
                tk.Label(row, text=skill + f" ({ability[:3]})").pack(side="left")
                label = tk.Label(row, text="+0", width=4)
                label.pack(side="left")
                self.skills[skill] = (ability, label)

    def change_profile_picture(self):
        # Use broader types if Pillow is available; otherwise limit to PNG/GIF (native Tk)
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.gif")] if PIL_AVAILABLE else [("PNG or GIF", "*.png *.gif")]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            try:
                if PIL_AVAILABLE:
                    img = Image.open(file_path)
                    # Prefer LANCZOS, fall back to BICUBIC/3 if not present
                    resample = getattr(Image, "LANCZOS", getattr(Image, "BICUBIC", 3))
                    img = img.resize((48, 48), resample)
                    mask = Image.new("L", (48, 48), 0)
                    from PIL import ImageDraw
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, 48, 48), fill=255)
                    img.putalpha(mask)
                    photo = ImageTk.PhotoImage(img)
                else:
                    # tk.PhotoImage supports PNG/GIF natively
                    photo = tk.PhotoImage(file=file_path)
                self.profile_photo = photo
                self.profile_label.config(image=self.profile_photo)
                self.profile_label.image = self.profile_photo
            except Exception as e:
                print("Error loading image:", e)

    def update_health(self):
        """Update the health bar to reflect current HP"""
        try:
            current = int(self.current_hp.get())
            maximum = int(self.max_hp.get())
            if maximum <= 0:
                maximum = 1
                self.max_hp.set(1)

            if current > maximum:
                current = maximum
                self.current_hp.set(maximum)
            elif current < 0:
                current = 0
                self.current_hp.set(0)

            self.hp_bar.config(maximum=maximum, value=current)
        except ValueError:
            pass

    def update_xp(self):
        """Update the XP bar and level based on current XP using D&D 5e progression"""
        xp_table = {
            1: 0,  2: 300,  3: 900,   4: 2700,  5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
        }
        try:
            current = int(self.current_xp.get())
            if current < 0:
                current = 0
                self.current_xp.set(0)
            # Determine level
            level = 1
            for lvl in range(1, 21):
                if current >= xp_table[lvl]:
                    level = lvl
                else:
                    break
            self.level.set(level)
            # Next level threshold for the bar
            next_level_xp = xp_table[level + 1] if level < 20 else xp_table[20]
            bar_value = current if current <= next_level_xp else next_level_xp
            self.xp_bar.config(maximum=next_level_xp, value=bar_value)
            self.level_label.config(text=f"Level: {self.level.get()}")
        except Exception:
            pass

    def update_modifier(self, var, label):
        try:
            score = int(var.get())
            modifier = (score - 10) // 2
            label.config(text=f"+{modifier}" if modifier >= 0 else f"{modifier}")
        except Exception:
            label.config(text="")
        self.update_skills()

    def update_skills(self):
        for skill, (ability, label) in self.skills.items():
            try:
                score = int(self.stats[ability].get())
                modifier = (score - 10) // 2
                label.config(text=f"+{modifier}" if modifier >= 0 else f"{modifier}")
            except Exception:
                label.config(text="")


if __name__ == "__main__":
    app = DnDCharacterSheet()
    app.mainloop()
