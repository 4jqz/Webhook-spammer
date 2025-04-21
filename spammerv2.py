import tkinter as tk
from tkinter import messagebox
import requests
import time
import sys
import threading
import json
import os

class Config:
    @staticmethod
    def getConfig():
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()
        config_path = os.path.join(base_dir, 'config.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError("config.json not found")
        with open(config_path) as f:
            return json.load(f)

class Webhook:
    def __init__(self, webhook):
        self.name = None
        self.config = Config.getConfig()
        self.webhook = webhook

    @staticmethod
    def CheckValid(webhook):
        r = requests.get(webhook)
        return r.status_code == 200

    def DeleteWebhook(self):
        if not self.CheckValid(self.webhook):
            raise IOError("Invalid Webhook")
        requests.post(self.webhook, headers={"Content-Type": "application/json"}, json=self.config["deletemessage"])
        requests.delete(self.webhook)

    def SendWebhook(self, output_text):
        if not self.CheckValid(self.webhook):
            raise IOError("Invalid webhook")
        while True:
            r = requests.post(self.webhook, headers={"Content-Type": "application/json"}, json=self.config["spammessage"])
            if r.status_code == 429:
                self._insert_text(output_text, "[-] Rate limited, waiting 5 seconds\n")
                time.sleep(5)
            elif r.status_code == 404:
                self._insert_text(output_text, "[-] Webhook got deleted\n")
                break
            elif r.status_code == 200:
                self._insert_text(output_text, "Webhook sent successfully\n")

    def GetInformations(self, output_text):
        if not self.CheckValid(self.webhook):
            raise IOError("Invalid token")
        r = requests.get(self.webhook)
        payload = r.json()
        self.name = payload.get("name", "Unknown")
        self._insert_text(output_text, f"Webhook name: {self.name}\n")

    def _insert_text(self, widget, text):
        widget.after(0, widget.insert, tk.END, text)

class WebhookManagerGUI:
    def __init__(self, master):
        self.master = master
        master.title("4jqz's Webhook Manager")
        try:
            master.iconbitmap('icon.ico')
        except Exception:
            pass

        self.webhook_label = tk.Label(master, text="Webhook URL:")
        self.webhook_label.grid(row=0, column=0, padx=5, pady=5)
        self.webhook_entry = tk.Entry(master, width=50)
        self.webhook_entry.grid(row=0, column=1, padx=5, pady=5)

        self.send_button = tk.Button(master, text="Send", command=self.send_webhook)
        self.send_button.grid(row=1, column=0, padx=5, pady=5)

        self.delete_button = tk.Button(master, text="Delete", command=self.delete_webhook)
        self.delete_button.grid(row=1, column=1, padx=5, pady=5)

        self.get_info_button = tk.Button(master, text="Get Info", command=self.get_webhook_info)
        self.get_info_button.grid(row=1, column=2, padx=5, pady=5)

        self.output_text = tk.Text(master, wrap=tk.WORD, height=10)
        self.output_text.grid(row=2, columnspan=3, padx=5, pady=5)

    def send_webhook(self):
        webhook_url = self.webhook_entry.get()
        if webhook_url:
            try:
                webhook = Webhook(webhook_url)
                threading.Thread(target=webhook.SendWebhook, args=(self.output_text,), daemon=True).start()
                self.output_text.insert(tk.END, f"Webhook spamming started: {webhook_url}\n")
            except IOError as e:
                self.output_text.insert(tk.END, f"Error: {e}\n")
        else:
            messagebox.showerror("Error", "Please enter a webhook URL")

    def delete_webhook(self):
        webhook_url = self.webhook_entry.get()
        if webhook_url:
            try:
                webhook = Webhook(webhook_url)
                webhook.DeleteWebhook()
                self.output_text.insert(tk.END, f"Webhook deleted: {webhook_url}\n")
            except IOError as e:
                self.output_text.insert(tk.END, f"Error: {e}\n")
        else:
            messagebox.showerror("Error", "Please enter a webhook URL")

    def get_webhook_info(self):
        webhook_url = self.webhook_entry.get()
        if webhook_url:
            try:
                webhook = Webhook(webhook_url)
                webhook.GetInformations(self.output_text)
            except IOError as e:
                self.output_text.insert(tk.END, f"Error: {e}\n")
        else:
            messagebox.showerror("Error", "Please enter a webhook URL")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebhookManagerGUI(root)
    root.mainloop()
