# llm_ui.py - Final working version for your setup
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import os
from dotenv import load_dotenv

load_dotenv()

from llm_tools_tester import run_llm_with_tools

# Import from your local piper file (we renamed it to my_piper.py)
from my_piper import generate_tts_wav, get_piper_voice

    # ── Dark mode colours ──────────────────────────────────────────
BG       = "#1e1e1e"   # window / frame background
BG_WIDGET= "#2d2d2d"   # chat box, entry, combobox background
FG       = "#e0e0e0"   # normal text
FG_DIM   = "#888888"   # labels, secondary text
BTN_BG   = "#3a3a3a"   # button background
BTN_FG   = "#ffffff"   # button text
ACCENT   = "#00bcd4"   # cyan accent (voice label, border hints)

class JarvisUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jarvis - Lightweight Tester")
        self.root.geometry("950x720")
        self.root.configure(bg=BG)

        self.chat = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state='disabled', font=("Arial", 11),
            bg=BG_WIDGET, fg=FG, insertbackground=FG,
            selectbackground="#444", selectforeground=FG,
            relief="flat", borderwidth=0
        )
        self.chat.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(self.root, bg=BG)
        input_frame.pack(fill=tk.X, padx=15, pady=8)

        self.entry = tk.Entry(
            input_frame, font=("Arial", 12),
            bg=BG_WIDGET, fg=FG, insertbackground=FG,
            relief="flat", borderwidth=4
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_message())

        tk.Button(
            input_frame, text="Send", command=self.send_message, width=12,
            bg=BTN_BG, fg=BTN_FG, activebackground="#555", activeforeground=FG,
            relief="flat", borderwidth=0
        ).pack(side=tk.RIGHT)

        # Voice selector
        ctrl_frame = tk.Frame(self.root, bg=BG)
        ctrl_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(ctrl_frame, text="Voice:", bg=BG, fg=ACCENT).pack(side=tk.LEFT, padx=(0,5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
            fieldbackground=BG_WIDGET, background=BG_WIDGET,
            foreground=FG, selectbackground=BG_WIDGET, selectforeground=FG,
            arrowcolor=FG, bordercolor=BTN_BG
        )

        self.voice_var = tk.StringVar(value="en_US-eminem-medium.onnx")
        voices = [f for f in os.listdir("voices") if f.endswith(".onnx")]
        self.voice_combo = ttk.Combobox(
            ctrl_frame, textvariable=self.voice_var, values=voices,
            state="readonly", width=45, style="Dark.TCombobox"
        )
        self.voice_combo.pack(side=tk.LEFT, padx=8)

        tk.Button(
            ctrl_frame, text="Play Last Reply", command=self.play_last_reply,
            bg=BTN_BG, fg=BTN_FG, activebackground="#555", activeforeground=FG,
            relief="flat", borderwidth=0
        ).pack(side=tk.RIGHT)

        self.status = tk.Label(self.root, text="Ready", fg="#00e676", bg=BG, font=("Arial", 12))
        self.status.pack(pady=12)

        self.messages = [
            {"role": "system", "content": "You are Jarvis, a helpful home assistant butler."}
        ]
        self.last_reply = ""

        self.root.mainloop()

    def send_message(self):
        text = self.entry.get().strip()
        if not text: 
            return
        self.append_chat("You", text)
        self.entry.delete(0, tk.END)
        self.status.config(text="Thinking...", fg="#ffb300")

        threading.Thread(target=self.run_llm, args=(text,), daemon=True).start()

    def run_llm(self, user_text):
        self.messages.append({"role": "user", "content": user_text})

        try:
            updated_messages = run_llm_with_tools(self.messages)
            self.messages = updated_messages

            last_msg = self.messages[-1]
            if hasattr(last_msg, "content"):
                reply = last_msg.content
            elif isinstance(last_msg, dict):
                reply = last_msg.get("content", "")
            else:
                reply = str(last_msg)

            self.last_reply = reply.strip() if reply else "Sorry, I couldn't respond."
            self.append_chat("Jarvis", self.last_reply)
        except Exception as e:
            self.append_chat("Jarvis", f"Error: {str(e)}")
            print("LLM Error:", e)

        self.status.config(text="Ready", fg="#00e676")

    def append_chat(self, sender, text):
        self.chat.config(state='normal')
        self.chat.insert(tk.END, f"{sender}: {text}\n\n")
        self.chat.see(tk.END)
        self.chat.config(state='disabled')

    def play_last_reply(self):
        if not self.last_reply:
            return
        threading.Thread(target=self.generate_and_play, daemon=True).start()

    def generate_and_play(self):
        self.status.config(text="Generating speech...", fg="blue")
        wav_path = "temp_last_reply.wav"

        try:
            selected_voice = self.voice_var.get()
            success = generate_tts_wav(self.last_reply, wav_path, model_name=selected_voice)

            if success and os.path.exists(wav_path):
                self.status.config(text="Playing...", fg="#ce93d8")
                os.startfile(wav_path)
            else:
                self.append_chat("System", "Failed to generate audio.")
        except Exception as e:
            self.append_chat("System", f"TTS Error: {e}")
            print("TTS Exception:", e)

        self.status.config(text="Ready", fg="#00e676")


if __name__ == "__main__":
    print("Starting Jarvis Lightweight UI...")
    print(f"Found {len([f for f in os.listdir('voices') if f.endswith('.onnx')])} voice models.")
    JarvisUI()