import tkinter as tk
from tkinter import scrolledtext
from expert import *

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema experto")

        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.message_entry = tk.Entry(root, width=80)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.expert = PsychologicalExpertSystem(model)
        self.questions = [
            "From 1 to 5 how do you rate your sleep quality? (1 the worst, 5 the best)",
            "From 1 to 5 how do you rate your physical activity level? (1 the least, 5 the most)",
            "From 1 to 5 how do you rate your diet quality? (1 the worst, 5 the best)",
            "From 1 to 5 how do you rate your social support or wellness? (1 the least, 5 the most)"
        ]
        self.user_responses = []  # Almacena las respuestas del usuario
        self.current_question = 0

        self.ask_question()

    def ask_question(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            self.display_message("Chat: " + question)
        else:
            self.process_responses()
            self.display_message("Would you like to answer again? (yes/no)")

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            if message.lower() == "yes":
                self.reset_chat()
            elif message.lower() == "no":
                self.display_message("Thank you for using the Mental health Expert System!")
            else:
                self.user_responses.append(message)  # Almacena la respuesta del usuario
                self.display_message("You: " + message)
                self.message_entry.delete(0, tk.END)
                self.current_question += 1
                self.ask_question()

    def process_responses(self):
        self.display_message("System: Processing responses...")
         
        for i, response in enumerate(self.user_responses):
            self.display_message(f"System: Response {i + 1}: {response}")
            # Procesar cada respuesta con el sistema experto si es necesario
            response_int = int(response)
        user_responses=self.user_responses
        self.expert.declare(Fact(sleep_quality=int(user_responses[0])))
        self.expert.declare(Fact(activity_level=int(user_responses[1])))
        self.expert.declare(Fact(diet_quality=int(user_responses[2])))
        self.expert.declare(Fact(social_support=int(user_responses[3])))
        self.expert.run()
        print("Recommendation:", self.expert.facts)
        print(self.expert.facts[5]["recommendation"])
        self.display_message("System: " + self.expert.facts[5]["recommendation"])

    def reset_chat(self):
        self.user_responses = []
        self.current_question = 0
        self.ask_question()

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
