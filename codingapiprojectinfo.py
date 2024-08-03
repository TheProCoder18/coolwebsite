import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import smtplib
from email.mime.text import MIMEText

class WorkflowApp:
    def __init__(self, master):
        self.master = master
        master.title("Workflow Application")

        # Predefined client names and their email addresses
        self.clients = {
            "Client A": "bibbyv@gmail.com",
            "Client B": "jteammedia7@gmail.com",
            "Client C": "nataliavarghese7@gmail.com"
        }

        # Database setup
        self.conn = sqlite3.connect('workflow.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS data
            (id INTEGER PRIMARY KEY,
             client_name TEXT,
             field1 TEXT,
             field2 TEXT,
             field3 TEXT,
             field4 TEXT,
             approved INTEGER DEFAULT 0)
        ''')
        self.conn.commit()

        # Create tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.submit_frame = ttk.Frame(self.notebook)
        self.review_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.submit_frame, text="Submit Data")
        self.notebook.add(self.review_frame, text="Review Data")

        self.create_submit_tab()
        self.create_review_tab()

    def create_submit_tab(self):
        # Create and layout input fields
        fields = ['Client Name', 'Field 1', 'Field 2', 'Field 3', 'Field 4']
        self.entries = {}

        for i, field in enumerate(fields):
            label = ttk.Label(self.submit_frame, text=field)
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)

            if field == 'Client Name':
                entry = ttk.Combobox(self.submit_frame, values=list(self.clients.keys()))
            else:
                entry = ttk.Entry(self.submit_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field] = entry

        submit_button = ttk.Button(self.submit_frame, text="Submit", command=self.submit_data)
        submit_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def create_review_tab(self):
        self.tree = ttk.Treeview(self.review_frame, columns=('Client', 'Field1', 'Field2', 'Field3', 'Field4'), show='headings')
        self.tree.heading('Client', text='Client')
        self.tree.heading('Field1', text='Field 1')
        self.tree.heading('Field2', text='Field 2')
        self.tree.heading('Field3', text='Field 3')
        self.tree.heading('Field4', text='Field 4')
        self.tree.pack(fill=tk.BOTH, expand=True)

        approve_button = ttk.Button(self.review_frame, text="Approve Selected", command=self.approve_data)
        approve_button.pack(pady=10)

        self.load_review_data()

    def submit_data(self):
        data = [self.entries[field].get() for field in ['Client Name', 'Field 1', 'Field 2', 'Field 3', 'Field 4']]
        if data[0] not in self.clients:
            messagebox.showerror("Error", "Please select a valid client name")
            return
        self.cursor.execute('''
            INSERT INTO data (client_name, field1, field2, field3, field4)
            VALUES (?, ?, ?, ?, ?)
        ''', data)
        self.conn.commit()
        messagebox.showinfo("Success", "Data submitted successfully")
        self.clear_entries()
        self.load_review_data()

    def clear_entries(self):
        for entry in self.entries.values():
            if hasattr(entry, 'set'):
                entry.set('')
            else:
                entry.delete(0, tk.END)

    def load_review_data(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT id, client_name, field1, field2, field3, field4 FROM data WHERE approved = 0")
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', iid=row[0], values=row[1:])

    def approve_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to approve")
            return

        item_id = selected_item[0]
        self.cursor.execute("UPDATE data SET approved = 1 WHERE id = ?", (item_id,))
        self.conn.commit()

        # Fetch client data
        self.cursor.execute("SELECT client_name, field1, field2, field3, field4 FROM data WHERE id = ?", (item_id,))
        client_data = self.cursor.fetchone()

        # Send email
        self.send_email(client_data)

        self.tree.delete(item_id)
        messagebox.showinfo("Success", "Data approved and email sent")

    def send_email(self, client_data):
        sender_email = "jteammedia7@gmail.com"  # Replace with your Gmail address
        sender_password = "qzct irpj ahwt rxau"  # Replace with your App Password
        receiver_email = self.clients[client_data[0]]

        message = MIMEText(f"Your data has been approved:\nField 1: {client_data[1]}\nField 2: {client_data[2]}\nField 3: {client_data[3]}\nField 4: {client_data[4]}")
        message['Subject'] = 'Data Approval Notification'
        message['From'] = sender_email
        message['To'] = receiver_email

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Email sent successfully to {receiver_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkflowApp(root)
    root.mainloop()