import flet as ft
import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nom TEXT, prenom TEXT, age INTEGER, 
                            email TEXT, adresses TEXT, Ncin TEXT UNIQUE)''')
        self.conn.commit()

    def insert_user(self, nom, prenom, age, email, adresses, ncin):
        self.cursor.execute('''INSERT INTO users (nom, prenom, age, email, adresses, Ncin) 
                          VALUES (?, ?, ?, ?, ?, ?)''',
                          (nom, prenom, age, email, adresses, ncin))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute('''SELECT id, nom, prenom, age, email, adresses, Ncin FROM users''')
        return self.cursor.fetchall()

    def update_user(self, id, nom, prenom, age, email, adresses, ncin):
        self.cursor.execute('''UPDATE users SET nom=?, prenom=?, age=?, 
                           email=?, adresses=?, Ncin=? WHERE id=?''',
                          (nom, prenom, age, email, adresses, ncin, id))
        self.conn.commit()

    def delete_user(self, id):
        self.cursor.execute('''DELETE FROM users WHERE id=?''', (id,))
        self.conn.commit()


class LoginPage(ft.UserControl):
    def __init__(self, page: ft.Page, switch_to_entry):
        super().__init__()
        page.scroll="auto"
        self.page = page
        self.switch_to_entry = switch_to_entry
        
    def build(self):
        self.username = ft.TextField(label="Username", width=300)
        self.password = ft.TextField(label="Password", password=True, width=300)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Login", size=30, color=ft.colors.BLUE),
                    self.username,
                    self.password,
                    ft.ElevatedButton(
                        text="Login",
                        on_click=self.login_clicked,
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    )
                ],
            ),
            padding=20,
            bgcolor=ft.colors.WHITE
        )

    def login_clicked(self, e):
        if self.username.value == "admin" and self.password.value == "admin":
            self.switch_to_entry()
        else:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Invalid credentials!"))
            )


class EntryPage(ft.UserControl):
    def __init__(self, page: ft.Page, db: Database, switch_to_display):
        super().__init__()
        self.page = page
        page.scroll="auto"
        self.db = db
        self.switch_to_display = switch_to_display
        
    def build(self):
        self.nom = ft.TextField(label="Nom", width=300)
        self.prenom = ft.TextField(label="Prenom", width=300)
        self.age = ft.TextField(label="Age", width=300)
        self.email = ft.TextField(label="Email", width=300)
        self.adresses = ft.TextField(label="Adresses", width=300)
        self.ncin = ft.TextField(label="NCIN", width=300)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Enter User Details", size=30, color=ft.colors.BLUE),
                    self.nom,
                    self.prenom,
                    self.age,
                    self.email,
                    self.adresses,
                    self.ncin,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                text="Submit",
                                on_click=self.submit_clicked,
                                bgcolor=ft.colors.GREEN,
                                color=ft.colors.WHITE
                            ),
                            ft.ElevatedButton(
                                text="View Data",
                                on_click=lambda _: self.switch_to_display(),
                                bgcolor=ft.colors.BLUE,
                                color=ft.colors.WHITE
                            )
                        ]
                    )
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
            bgcolor=ft.colors.WHITE
        )

    def submit_clicked(self, e):
        try:
            self.db.insert_user(
                self.nom.value,
                self.prenom.value,
                int(self.age.value),
                self.email.value,
                self.adresses.value,
                self.ncin.value
            )
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("User added successfully!"))
            )
            self.clear_fields()
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"))
            )

    def clear_fields(self):
        self.nom.value = ""
        self.prenom.value = ""
        self.age.value = ""
        self.email.value = ""
        self.adresses.value = ""
        self.ncin.value = ""
        self.update()


class DisplayPage(ft.UserControl):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        self.page = page
        page.scroll="auto"
        self.db = db
        self.edit_dialog = None

    def build(self):
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Actions")),
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nom")),
                ft.DataColumn(ft.Text("Prenom")),
                ft.DataColumn(ft.Text("Age")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Adresses")),
                ft.DataColumn(ft.Text("NCIN")),
            ],
            rows=[],
        )
        
        table_container = ft.Container(
            content=ft.Column(
                [ft.Row([self.data_table], scroll=ft.ScrollMode.ALWAYS)],
                scroll=ft.ScrollMode.ALWAYS
            ),
            expand=True,
            height=400
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("User Records", size=30, color=ft.colors.BLUE),
                    ft.ElevatedButton(
                        text="Refresh",
                        on_click=self.refresh_data,
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    ),
                    table_container
                ],
                expand=True
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            expand=True
        )

    def refresh_data(self, e=None):
        self.data_table.rows.clear()
        users = self.db.get_all_users()
        
        for user in users:
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_color=ft.colors.BLUE,
                                    on_click=lambda e, user=user: self.edit_user(user)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.RED,
                                    on_click=lambda e, id=user[0]: self.delete_user(id)
                                )
                            ])
                        ),
                        ft.DataCell(ft.Text(user[0])),  # ID
                        ft.DataCell(ft.Text(user[1])),  # Nom
                        ft.DataCell(ft.Text(user[2])),  # Prenom
                        ft.DataCell(ft.Text(user[3])),  # Age
                        ft.DataCell(ft.Text(user[4])),  # Email
                        ft.DataCell(ft.Text(user[5])),  # Adresses
                        ft.DataCell(ft.Text(user[6])),  # NCIN
                    ]
                )
            )
        self.update()

    def edit_user(self, user):
        edit_fields = {
            'nom': ft.TextField(label="Nom", value=user[1]),
            'prenom': ft.TextField(label="Prenom", value=user[2]),
            'age': ft.TextField(label="Age", value=str(user[3])),
            'email': ft.TextField(label="Email", value=user[4]),
            'adresses': ft.TextField(label="Adresses", value=user[5]),
            'ncin': ft.TextField(label="NCIN", value=user[6])
        }

        def save_changes(e):
            try:
                self.db.update_user(
                    user[0],  # ID
                    edit_fields['nom'].value,
                    edit_fields['prenom'].value,
                    int(edit_fields['age'].value),
                    edit_fields['email'].value,
                    edit_fields['adresses'].value,
                    edit_fields['ncin'].value
                )
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("User updated successfully!"))
                )
                self.edit_dialog.open = False
                self.refresh_data()
            except Exception as ex:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"))
                )
                
        self.edit_dialog = ft.AlertDialog(
            title=ft.Text("Edit User"),
            content=ft.Column(
                controls=list(edit_fields.values()),
                scroll=ft.ScrollMode.AUTO
            ),
            
            actions=[
                ft.ElevatedButton("Save", on_click=save_changes),
                ft.ElevatedButton("Cancel",                                 
                on_click=lambda e:  setattr(self.edit_dialog, 'open', False))
                
            ]
            
        )
        self.page.dialog = self.edit_dialog
        self.edit_dialog.open = True
        self.page.update()

    def delete_user(self, id):
        self.db.delete_user(id)
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("User deleted successfully!"))
        )
        self.refresh_data()


def main(page: ft.Page):
    page.title = "User Management System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 800
    db = Database()
    
    def switch_to_entry():
        page.clean()
        page.add(navbar, entry_page)

    def switch_to_display():
        page.clean()
        page.add(navbar, display_page)
        display_page.refresh_data()

    def switch_to_login():
        page.clean()
        page.add(navbar, login_page)

    navbar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.LOGIN, label="Login"),
            ft.NavigationDestination(icon=ft.icons.ADD, label="Entry"),
            ft.NavigationDestination(icon=ft.icons.LIST, label="Display")
        ],
        on_change=lambda e: [
            switch_to_login,
            switch_to_entry,
            switch_to_display
        ][e.control.selected_index]()
    )

    login_page = LoginPage(page, switch_to_entry)
    entry_page = EntryPage(page, db, switch_to_display)
    display_page = DisplayPage(page, db)

    page.add(navbar, login_page)


if __name__ == "__main__":
    ft.app(target=main)