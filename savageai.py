import tkinter as tk
from tkinter import scrolledtext
import threading
import requests
import json
import time

# ─── CONFIG ───────────────────────────────────────────────
MODEL = "savageai"  # change to codellama:7b-instruct-q3_K_S if needed
OLLAMA_URL = "http://localhost:11434/api/generate"

# ─── COLORS ───────────────────────────────────────────────
BG_DARK       = "#0d0a0e"
BG_PANEL      = "#140f17"
BG_INPUT      = "#1c1220"
PINK_BRIGHT   = "#ff69b4"
PINK_MID      = "#d44f8e"
PINK_FADED    = "#8b3a62"
PINK_GLOW     = "#ff85c2"
PINK_SUBTLE   = "#2a1525"
TEXT_WHITE    = "#f5e6ef"
TEXT_GRAY     = "#9e7a8f"
BORDER_PINK   = "#4a1f3a"

# ─── FONTS ────────────────────────────────────────────────
FONT_TITLE    = ("Georgia", 15, "bold")
FONT_MSG      = ("Consolas", 11)
FONT_INPUT    = ("Consolas", 11)
FONT_BTN      = ("Georgia", 11, "bold")
FONT_LABEL    = ("Georgia", 9)
FONT_TIME     = ("Consolas", 8)

class SavageAIChat:
    def __init__(self, root):
        self.root = root
        self.root.title("SavageAI — Local CodeLlama")
        self.root.geometry("820x700")
        self.root.minsize(600, 500)
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        self.is_generating = False
        self.conversation_history = []

        self._build_ui()
        self._add_welcome_message()

    def _build_ui(self):
        # ── TOP BAR ──
        topbar = tk.Frame(self.root, bg=BG_PANEL, height=58)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        # pink accent line at top
        accent = tk.Frame(self.root, bg=PINK_MID, height=2)
        accent.pack(fill="x", side="top")

        # dot indicators
        dots_frame = tk.Frame(topbar, bg=BG_PANEL)
        dots_frame.pack(side="left", padx=16, pady=18)
        for color in [PINK_BRIGHT, PINK_MID, PINK_FADED]:
            d = tk.Canvas(dots_frame, width=11, height=11, bg=BG_PANEL, highlightthickness=0)
            d.create_oval(1, 1, 10, 10, fill=color, outline="")
            d.pack(side="left", padx=3)

        # title
        title_frame = tk.Frame(topbar, bg=BG_PANEL)
        title_frame.pack(side="left", padx=10)
        tk.Label(title_frame, text="✦ SavageAI", font=FONT_TITLE,
                 fg=PINK_BRIGHT, bg=BG_PANEL).pack(side="left")
        tk.Label(title_frame, text="  local · offline · unfiltered",
                 font=FONT_LABEL, fg=TEXT_GRAY, bg=BG_PANEL).pack(side="left", pady=2)

        # status dot
        self.status_frame = tk.Frame(topbar, bg=BG_PANEL)
        self.status_frame.pack(side="right", padx=20)
        self.status_dot = tk.Canvas(self.status_frame, width=9, height=9,
                                     bg=BG_PANEL, highlightthickness=0)
        self.status_dot.create_oval(1, 1, 8, 8, fill=PINK_BRIGHT, outline="", tags="dot")
        self.status_dot.pack(side="left", padx=(0, 6))
        self.status_label = tk.Label(self.status_frame, text="ready",
                                      font=FONT_LABEL, fg=TEXT_GRAY, bg=BG_PANEL)
        self.status_label.pack(side="left")

        # clear button
        clear_btn = tk.Button(topbar, text="clear", font=FONT_LABEL,
                               fg=PINK_FADED, bg=BG_PANEL, bd=0, cursor="hand2",
                               activeforeground=PINK_BRIGHT, activebackground=BG_PANEL,
                               command=self._clear_chat)
        clear_btn.pack(side="right", padx=4)

        # ── CHAT AREA ──
        chat_outer = tk.Frame(self.root, bg=BG_DARK)
        chat_outer.pack(fill="both", expand=True, padx=0, pady=0)

        self.chat_frame = tk.Frame(chat_outer, bg=BG_DARK)
        self.chat_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.chat_frame, bg=BG_DARK,
                                 highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical",
                                       command=self.canvas.yview,
                                       bg=BG_PANEL, troughcolor=BG_DARK,
                                       activebackground=PINK_FADED)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.messages_container = tk.Frame(self.canvas, bg=BG_DARK)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.messages_container, anchor="nw"
        )

        self.messages_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # ── BOTTOM INPUT AREA ──
        bottom_accent = tk.Frame(self.root, bg=BORDER_PINK, height=1)
        bottom_accent.pack(fill="x")

        bottom = tk.Frame(self.root, bg=BG_PANEL, pady=14)
        bottom.pack(fill="x", side="bottom")

        input_wrap = tk.Frame(bottom, bg=BORDER_PINK, padx=1, pady=1)
        input_wrap.pack(fill="x", padx=16, pady=0)

        input_inner = tk.Frame(input_wrap, bg=BG_INPUT)
        input_inner.pack(fill="x")

        self.input_box = tk.Text(input_inner, height=3, font=FONT_INPUT,
                                  bg=BG_INPUT, fg=TEXT_WHITE,
                                  insertbackground=PINK_BRIGHT,
                                  relief="flat", bd=8, wrap="word",
                                  selectbackground=PINK_FADED)
        self.input_box.pack(fill="x", side="left", expand=True)
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)
        self.input_box.focus()

        # placeholder
        self._set_placeholder()
        self.input_box.bind("<FocusIn>", self._clear_placeholder)
        self.input_box.bind("<FocusOut>", self._restore_placeholder)

        btn_frame = tk.Frame(input_inner, bg=BG_INPUT)
        btn_frame.pack(side="right", padx=8, pady=6)

        self.send_btn = tk.Button(btn_frame, text="⟶", font=("Georgia", 16, "bold"),
                                   fg=PINK_BRIGHT, bg=BG_INPUT, bd=0,
                                   cursor="hand2", activeforeground=PINK_GLOW,
                                   activebackground=BG_INPUT,
                                   command=self._send_message)
        self.send_btn.pack()

        # bottom hint
        hint = tk.Label(bottom, text="Enter to send  ·  Shift+Enter for newline  ·  running locally on your machine",
                        font=("Consolas", 8), fg=TEXT_GRAY, bg=BG_PANEL)
        hint.pack(pady=(6, 0))

    def _set_placeholder(self):
        self.input_box.insert("1.0", "ask me something, genius...")
        self.input_box.config(fg=PINK_FADED)
        self._placeholder_active = True

    def _clear_placeholder(self, event=None):
        if self._placeholder_active:
            self.input_box.delete("1.0", "end")
            self.input_box.config(fg=TEXT_WHITE)
            self._placeholder_active = False

    def _restore_placeholder(self, event=None):
        if not self.input_box.get("1.0", "end").strip():
            self._set_placeholder()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_to_bottom(self):
        self.root.after(100, lambda: self.canvas.yview_moveto(1.0))

    def _add_welcome_message(self):
        self._add_bot_message(
            "yo. i'm SavageAI — your local, offline, unfiltered coding assistant.\n\n"
            "i run entirely on YOUR machine. no cloud. no subscription. no bs.\n\n"
            "ask me to write code, debug your garbage, or explain concepts. let's go. 🔥"
        )

    def _add_user_message(self, text):
        wrapper = tk.Frame(self.messages_container, bg=BG_DARK)
        wrapper.pack(fill="x", padx=16, pady=(8, 4))

        # timestamp
        t = time.strftime("%H:%M")
        tk.Label(wrapper, text=f"you · {t}", font=FONT_TIME,
                 fg=TEXT_GRAY, bg=BG_DARK).pack(anchor="e")

        # bubble
        bubble_outer = tk.Frame(wrapper, bg=PINK_MID, padx=1, pady=1)
        bubble_outer.pack(anchor="e", pady=(2, 0))

        bubble = tk.Frame(bubble_outer, bg=PINK_SUBTLE)
        bubble.pack()

        msg = tk.Label(bubble, text=text, font=FONT_MSG,
                       fg=TEXT_WHITE, bg=PINK_SUBTLE,
                       wraplength=500, justify="left",
                       padx=14, pady=10, anchor="w")
        msg.pack()

        self._scroll_to_bottom()

    def _add_bot_message(self, text=""):
        wrapper = tk.Frame(self.messages_container, bg=BG_DARK)
        wrapper.pack(fill="x", padx=16, pady=(8, 4))

        # timestamp
        t = time.strftime("%H:%M")
        tk.Label(wrapper, text=f"savageai · {t}", font=FONT_TIME,
                 fg=PINK_FADED, bg=BG_DARK).pack(anchor="w")

        # bubble
        bubble_outer = tk.Frame(wrapper, bg=BORDER_PINK, padx=1, pady=1)
        bubble_outer.pack(anchor="w", pady=(2, 0))

        bubble = tk.Frame(bubble_outer, bg=BG_PANEL)
        bubble.pack()

        self.bot_label = tk.Label(bubble, text=text, font=FONT_MSG,
                                   fg=TEXT_WHITE, bg=BG_PANEL,
                                   wraplength=560, justify="left",
                                   padx=14, pady=10, anchor="w")
        self.bot_label.pack()

        self._scroll_to_bottom()
        return self.bot_label

    def _update_status(self, text, color=TEXT_GRAY):
        self.status_label.config(text=text, fg=color)
        self.status_dot.delete("dot")
        self.status_dot.create_oval(1, 1, 8, 8, fill=color, outline="", tags="dot")

    def _on_enter(self, event):
        if not event.state & 0x1:  # shift not held
            self._send_message()
            return "break"

    def _send_message(self):
        if self.is_generating:
            return
        if self._placeholder_active:
            return

        text = self.input_box.get("1.0", "end").strip()
        if not text:
            return

        self.input_box.delete("1.0", "end")
        self._set_placeholder()

        self._add_user_message(text)
        self.conversation_history.append({"role": "user", "content": text})

        bot_label = self._add_bot_message("▌")
        self.is_generating = True
        self._update_status("generating...", PINK_BRIGHT)
        self.send_btn.config(state="disabled", fg=PINK_FADED)

        thread = threading.Thread(
            target=self._stream_response,
            args=(text, bot_label),
            daemon=True
        )
        thread.start()

    def _build_prompt(self, user_text):
        # build prompt with history
        prompt = ""
        for msg in self.conversation_history[-6:]:  # last 6 messages for context
            if msg["role"] == "user":
                prompt += f"[INST] {msg['content']} [/INST]\n"
            else:
                prompt += f"{msg['content']}\n"
        return prompt

    def _stream_response(self, user_text, bot_label):
        prompt = self._build_prompt(user_text)
        full_response = ""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": prompt, "stream": True},
                stream=True,
                timeout=120
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    token = data.get("response", "")
                    full_response += token

                    # update label in main thread
                    display = full_response + "▌"
                    self.root.after(0, lambda t=display: bot_label.config(text=t))
                    self.root.after(0, self._scroll_to_bottom)

                    if data.get("done"):
                        break

            # final update without cursor
            self.root.after(0, lambda: bot_label.config(text=full_response))
            self.conversation_history.append({"role": "assistant", "content": full_response})

        except requests.exceptions.ConnectionError:
            error = "⚠ can't connect to Ollama!\n\nMake sure 'ollama serve' is running in CMD."
            self.root.after(0, lambda: bot_label.config(text=error, fg=PINK_MID))

        except Exception as e:
            error = f"⚠ error: {str(e)}"
            self.root.after(0, lambda: bot_label.config(text=error, fg=PINK_MID))

        finally:
            self.is_generating = False
            self.root.after(0, lambda: self._update_status("ready", PINK_BRIGHT))
            self.root.after(0, lambda: self.send_btn.config(state="normal", fg=PINK_BRIGHT))

    def _clear_chat(self):
        for widget in self.messages_container.winfo_children():
            widget.destroy()
        self.conversation_history = []
        self._add_welcome_message()

# ─── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()

    # remove default title bar styling on windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = SavageAIChat(root)
    root.mainloop()