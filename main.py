import sys
import sqlite3
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import os


class DatabaseManager:
    def __init__(self, db_name="gestion_etudiants.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Initialise la base de données avec toutes les tables nécessaires"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Table des départements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')

        # Table des formations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                nb_annees INTEGER NOT NULL,
                departement_id INTEGER,
                FOREIGN KEY (departement_id) REFERENCES departements (id)
            )
        ''')

        # Table des étudiants
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS etudiants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT NOT NULL UNIQUE,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT,
                telephone TEXT
            )
        ''')

        # Table des inscriptions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etudiant_id INTEGER,
                formation_id INTEGER,
                annee_inscription INTEGER,
                FOREIGN KEY (etudiant_id) REFERENCES etudiants (id),
                FOREIGN KEY (formation_id) REFERENCES formations (id)
            )
        ''')

        # Table des matières
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matieres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                credits INTEGER NOT NULL,
                formation_id INTEGER,
                annee INTEGER NOT NULL,
                semestre INTEGER NOT NULL,
                FOREIGN KEY (formation_id) REFERENCES formations (id)
            )
        ''')

        # Table des notes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etudiant_id INTEGER,
                matiere_id INTEGER,
                note REAL,
                semestre INTEGER,
                FOREIGN KEY (etudiant_id) REFERENCES etudiants (id),
                FOREIGN KEY (matiere_id) REFERENCES matieres (id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

class DepartementDialog(QDialog):
    def __init__(self, parent=None, departement_data=None):
        super().__init__(parent)
        self.departement_data = departement_data
        self.setWindowTitle("Ajouter Département" if not departement_data else "Modifier Département")
        self.setModal(True)
        self.resize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.nom_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)

        if self.departement_data:
            self.nom_edit.setText(self.departement_data[1])
            self.description_edit.setText(self.departement_data[2] or "")

        form_layout.addRow("Nom:", self.nom_edit)
        form_layout.addRow("Description:", self.description_edit)

        layout.addLayout(form_layout)

        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        return {
            'nom': self.nom_edit.text(),
            'description': self.description_edit.toPlainText()
        }

class FormationDialog(QDialog):
    def __init__(self, parent=None, formation_data=None, departements=None):
        super().__init__(parent)
        self.formation_data = formation_data
        self.departements = departements or []
        self.setWindowTitle("Ajouter Formation" if not formation_data else "Modifier Formation")
        self.setModal(True)
        self.resize(400, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.nom_edit = QLineEdit()
        self.nb_annees_spin = QSpinBox()
        self.nb_annees_spin.setRange(1, 10)
        self.nb_annees_spin.setValue(3)

        self.departement_combo = QComboBox()
        for dept in self.departements:
            self.departement_combo.addItem(dept[1], dept[0])

        if self.formation_data:
            self.nom_edit.setText(self.formation_data[1])
            self.nb_annees_spin.setValue(self.formation_data[2])
            # Sélectionner le bon département
            for i in range(self.departement_combo.count()):
                if self.departement_combo.itemData(i) == self.formation_data[3]:
                    self.departement_combo.setCurrentIndex(i)
                    break

        form_layout.addRow("Nom:", self.nom_edit)
        form_layout.addRow("Nombre d'années:", self.nb_annees_spin)
        form_layout.addRow("Département:", self.departement_combo)

        layout.addLayout(form_layout)

        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        return {
            'nom': self.nom_edit.text(),
            'nb_annees': self.nb_annees_spin.value(),
            'departement_id': self.departement_combo.currentData()
        }

class EtudiantDialog(QDialog):
    def __init__(self, parent=None, etudiant_data=None):
        super().__init__(parent)
        self.etudiant_data = etudiant_data
        self.setWindowTitle("Ajouter Étudiant" if not etudiant_data else "Modifier Étudiant")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.matricule_edit = QLineEdit()
        self.nom_edit = QLineEdit()
        self.prenom_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.telephone_edit = QLineEdit()

        if self.etudiant_data:
            self.matricule_edit.setText(self.etudiant_data[1])
            self.nom_edit.setText(self.etudiant_data[2])
            self.prenom_edit.setText(self.etudiant_data[3])
            self.email_edit.setText(self.etudiant_data[4] or "")
            self.telephone_edit.setText(self.etudiant_data[5] or "")

        form_layout.addRow("Matricule:", self.matricule_edit)
        form_layout.addRow("Nom:", self.nom_edit)
        form_layout.addRow("Prénom:", self.prenom_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Téléphone:", self.telephone_edit)

        layout.addLayout(form_layout)

        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        return {
            'matricule': self.matricule_edit.text(),
            'nom': self.nom_edit.text(),
            'prenom': self.prenom_edit.text(),
            'email': self.email_edit.text(),
            'telephone': self.telephone_edit.text()
        }

class MatiereDialog(QDialog):
    def __init__(self, parent=None, matiere_data=None):
        super().__init__(parent)
        self.matiere_data = matiere_data
        self.setWindowTitle("Ajouter Matière" if not matiere_data else "Modifier Matière")
        self.setModal(True)
        self.resize(400, 200)
        self.setup_ui()


    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.nom_edit = QLineEdit()
        self.credits_spin = QSpinBox()
        self.credits_spin.setRange(1, 20)
        self.credits_spin.setValue(3)

        self.annee_spin = QSpinBox()
        self.annee_spin.setRange(1, 10)
        self.annee_spin.setValue(1)

        if self.matiere_data:
            self.nom_edit.setText(self.matiere_data[1])
            self.credits_spin.setValue(self.matiere_data[2])
            self.annee_spin.setValue(self.matiere_data[4])
            self.semestre_combo.setCurrentText(str(self.matiere_data[5]))

        form_layout.addRow("Nom:", self.nom_edit)
        form_layout.addRow("Crédits:", self.credits_spin)
        form_layout.addRow("Année:", self.annee_spin)

        layout.addLayout(form_layout)

        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)
        self.semestre_combo = QComboBox()
        self.semestre_combo.addItems(["1", "2"])
        form_layout.addRow("Semestre:", self.semestre_combo)

    def get_data(self):
        return {
            'nom': self.nom_edit.text(),
            'credits': self.credits_spin.value(),
            'annee': self.annee_spin.value(),
            'semestre': int(self.semestre_combo.currentText())
        }

class DepartementsTab(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel("Gestion des Départements")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Boutons d'action
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Ajouter Département")
        self.edit_btn = QPushButton("Modifier")
        self.delete_btn = QPushButton("Supprimer")

        self.add_btn.clicked.connect(self.add_departement)
        self.edit_btn.clicked.connect(self.edit_departement)
        self.delete_btn.clicked.connect(self.delete_departement)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table des départements
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departements")
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))

    def add_departement(self):
        dialog = DepartementDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['nom']:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO departements (nom, description) VALUES (?, ?)",
                                   (data['nom'], data['description']))
                    conn.commit()
                    self.load_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Succès", "Département ajouté avec succès!")
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Ce nom de département existe déjà!")
                finally:
                    conn.close()

    def edit_departement(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            dept_id = int(self.table.item(current_row, 0).text())
            dept_data = (dept_id,
                         self.table.item(current_row, 1).text(),
                         self.table.item(current_row, 2).text())

            dialog = DepartementDialog(self, dept_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data['nom']:
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE departements SET nom=?, description=? WHERE id=?",
                                   (data['nom'], data['description'], dept_id))
                    conn.commit()
                    conn.close()
                    self.load_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Succès", "Département modifié avec succès!")

    def delete_departement(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            dept_id = int(self.table.item(current_row, 0).text())
            reply = QMessageBox.question(self, "Confirmation",
                                         "Êtes-vous sûr de vouloir supprimer ce département?")
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM departements WHERE id=?", (dept_id,))
                conn.commit()
                conn.close()
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Succès", "Département supprimé avec succès!")

class FormationsTab(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel("Gestion des Formations")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Boutons d'action
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Ajouter Formation")
        self.edit_btn = QPushButton("Modifier")
        self.delete_btn = QPushButton("Supprimer")
        self.manage_subjects_btn = QPushButton("Gérer Matières")
        self.manage_students_btn = QPushButton("Gérer Étudiants")

        self.add_btn.clicked.connect(self.add_formation)
        self.edit_btn.clicked.connect(self.edit_formation)
        self.delete_btn.clicked.connect(self.delete_formation)
        self.manage_subjects_btn.clicked.connect(self.manage_subjects)
        self.manage_students_btn.clicked.connect(self.manage_students)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.manage_subjects_btn)
        button_layout.addWidget(self.manage_students_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table des formations
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Nb Années", "Département"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.id, f.nom, f.nb_annees, d.nom 
            FROM formations f 
            LEFT JOIN departements d ON f.departement_id = d.id
        ''')
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))

    def get_departements(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departements")
        data = cursor.fetchall()
        conn.close()
        return data

    def add_formation(self):
        departements = self.get_departements()
        if not departements:
            QMessageBox.warning(self, "Erreur", "Vous devez d'abord créer au moins un département!")
            return

        dialog = FormationDialog(self, None, departements)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['nom']:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO formations (nom, nb_annees, departement_id) VALUES (?, ?, ?)",
                               (data['nom'], data['nb_annees'], data['departement_id']))
                conn.commit()
                conn.close()
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Succès", "Formation ajoutée avec succès!")

    def edit_formation(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            formation_id = int(self.table.item(current_row, 0).text())

            # Récupérer les données complètes
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM formations WHERE id=?", (formation_id,))
            formation_data = cursor.fetchone()
            conn.close()

            departements = self.get_departements()
            dialog = FormationDialog(self, formation_data, departements)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data['nom']:
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE formations SET nom=?, nb_annees=?, departement_id=? WHERE id=?",
                                   (data['nom'], data['nb_annees'], data['departement_id'], formation_id))
                    conn.commit()
                    conn.close()
                    self.load_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Succès", "Formation modifiée avec succès!")

    def delete_formation(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            formation_id = int(self.table.item(current_row, 0).text())
            reply = QMessageBox.question(self, "Confirmation",
                                         "Êtes-vous sûr de vouloir supprimer cette formation?")
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM formations WHERE id=?", (formation_id,))
                conn.commit()
                conn.close()
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Succès", "Formation supprimée avec succès!")

    def manage_subjects(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            formation_id = int(self.table.item(current_row, 0).text())
            formation_name = self.table.item(current_row, 1).text()
            dialog = SubjectsManagementDialog(self, self.db_manager, formation_id, formation_name)
            dialog.exec()

    def manage_students(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            formation_id = int(self.table.item(current_row, 0).text())
            formation_name = self.table.item(current_row, 1).text()
            dialog = StudentsManagementDialog(self, self.db_manager, formation_id, formation_name)
            dialog.exec()

class SubjectsManagementDialog(QDialog):
    def __init__(self, parent, db_manager, formation_id, formation_name):
        super().__init__(parent)
        self.db_manager = db_manager
        self.formation_id = formation_id
        self.formation_name = formation_name
        self.setWindowTitle(f"Gestion des Matières - {formation_name}")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel(f"Matières de la formation: {self.formation_name}")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # Boutons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Ajouter Matière")
        self.edit_btn = QPushButton("Modifier")
        self.delete_btn = QPushButton("Supprimer")

        self.add_btn.clicked.connect(self.add_matiere)
        self.edit_btn.clicked.connect(self.edit_matiere)
        self.delete_btn.clicked.connect(self.delete_matiere)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Crédits", "Année", "Semestre"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM matieres WHERE formation_id=? ORDER BY annee, nom",
                       (self.formation_id,))
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col in range(5):  # Afficher les 4 colonnes
                self.table.setItem(row, col,
                                   QTableWidgetItem(str(item[col]) if col < len(item) else QTableWidgetItem("")))

    def add_matiere(self):
        dialog = MatiereDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['nom']:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO matieres (nom, credits, formation_id, annee, semestre) VALUES (?, ?, ?, ?, ?)",
                    (data['nom'], data['credits'], self.formation_id, data['annee'], data['semestre']))
                conn.commit()
                conn.close()
                self.load_data()
                QMessageBox.information(self, "Succès", "Matière ajoutée avec succès!")

    def edit_matiere(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            matiere_id = int(self.table.item(current_row, 0).text())

            # Récupérer les données complètes
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM matieres WHERE id=?", (matiere_id,))
            matiere_data = cursor.fetchone()
            conn.close()

            dialog = MatiereDialog(self, matiere_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data['nom']:
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE matieres SET nom=?, credits=?, annee=? WHERE id=?",
                                   (data['nom'], data['credits'], data['annee'], matiere_id))
                    conn.commit()
                    conn.close()
                    self.load_data()
                    QMessageBox.information(self, "Succès", "Matière modifiée avec succès!")

    def delete_matiere(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            matiere_id = int(self.table.item(current_row, 0).text())
            reply = QMessageBox.question(self, "Confirmation",
                                         "Êtes-vous sûr de vouloir supprimer cette matière?")
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM matieres WHERE id=?", (matiere_id,))
                conn.commit()
                conn.close()
                self.load_data()
                QMessageBox.information(self, "Succès", "Matière supprimée avec succès!")

class StudentsManagementDialog(QDialog):
    def __init__(self, parent, db_manager, formation_id, formation_name):
        super().__init__(parent)
        self.db_manager = db_manager
        self.formation_id = formation_id
        self.formation_name = formation_name
        self.setWindowTitle(f"Gestion des Étudiants - {formation_name}")
        self.setModal(True)
        self.resize(800, 500)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel(f"Étudiants inscrits à: {self.formation_name}")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # Section d'inscription
        inscription_group = QGroupBox("Inscrire un étudiant")
        inscription_layout = QHBoxLayout()

        self.etudiant_combo = QComboBox()
        self.load_available_students()

        self.inscrire_btn = QPushButton("Inscrire")
        self.inscrire_btn.clicked.connect(self.inscrire_etudiant)

        inscription_layout.addWidget(QLabel("Étudiant:"))
        inscription_layout.addWidget(self.etudiant_combo)
        inscription_layout.addWidget(self.inscrire_btn)
        inscription_layout.addStretch()

        inscription_group.setLayout(inscription_layout)
        layout.addWidget(inscription_group)

        # Boutons d'action
        button_layout = QHBoxLayout()
        self.desinscrire_btn = QPushButton("Désinscrire")
        self.notes_btn = QPushButton("Gérer Notes")

        self.desinscrire_btn.clicked.connect(self.desinscrire_etudiant)
        self.notes_btn.clicked.connect(self.gerer_notes)

        button_layout.addWidget(self.desinscrire_btn)
        button_layout.addWidget(self.notes_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table des étudiants inscrits
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Matricule", "Nom", "Prénom", "Email", "Téléphone"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def load_available_students(self):
        """Charge les étudiants non inscrits à cette formation"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, e.matricule, e.nom, e.prenom 
            FROM etudiants e 
            WHERE e.id NOT IN (
                SELECT i.etudiant_id 
                FROM inscriptions i 
                WHERE i.formation_id = ?
            )
        ''', (self.formation_id,))
        data = cursor.fetchall()
        conn.close()

        self.etudiant_combo.clear()
        for etudiant in data:
            self.etudiant_combo.addItem(f"{etudiant[1]} - {etudiant[2]} {etudiant[3]}", etudiant[0])

    def load_data(self):
        """Charge les étudiants inscrits à cette formation"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.matricule, e.nom, e.prenom, e.email, e.telephone
            FROM etudiants e
            JOIN inscriptions i ON e.id = i.etudiant_id
            WHERE i.formation_id = ?
        ''', (self.formation_id,))
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col in range(5):
                self.table.setItem(row, col, QTableWidgetItem(str(item[col]) if item[col] else ""))

        # Recharger les étudiants disponibles
        self.load_available_students()

    def inscrire_etudiant(self):
        if self.etudiant_combo.currentData():
            etudiant_id = self.etudiant_combo.currentData()

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO inscriptions (etudiant_id, formation_id, annee_inscription) VALUES (?, ?, ?)",
                           (etudiant_id, self.formation_id, 2024))  # Année par défaut
            conn.commit()
            conn.close()

            self.load_data()
            QMessageBox.information(self, "Succès", "Étudiant inscrit avec succès!")

    def desinscrire_etudiant(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            matricule = self.table.item(current_row, 0).text()

            # Récupérer l'ID de l'étudiant
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM etudiants WHERE matricule = ?", (matricule,))
            etudiant_id = cursor.fetchone()[0]

            reply = QMessageBox.question(self, "Confirmation",
                                         "Êtes-vous sûr de vouloir désinscrire cet étudiant?")
            if reply == QMessageBox.StandardButton.Yes:
                cursor.execute("DELETE FROM inscriptions WHERE etudiant_id = ? AND formation_id = ?",
                               (etudiant_id, self.formation_id))
                conn.commit()
                conn.close()

                self.load_data()
                QMessageBox.information(self, "Succès", "Étudiant désinscrit avec succès!")

    def gerer_notes(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            matricule = self.table.item(current_row, 0).text()
            nom = self.table.item(current_row, 1).text()
            prenom = self.table.item(current_row, 2).text()

            # Récupérer l'ID de l'étudiant
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM etudiants WHERE matricule = ?", (matricule,))
            etudiant_id = cursor.fetchone()[0]
            conn.close()

            dialog = NotesManagementDialog(self, self.db_manager, etudiant_id,
                                           f"{nom} {prenom}", self.formation_id)
            dialog.exec()

class NotesManagementDialog(QDialog):
    def __init__(self, parent, db_manager, etudiant_id, etudiant_name, formation_id):
        super().__init__(parent)
        self.db_manager = db_manager
        self.etudiant_id = etudiant_id
        self.etudiant_name = etudiant_name
        self.formation_id = formation_id
        self.setWindowTitle(f"Gestion des Notes - {etudiant_name}")
        self.setModal(True)
        self.resize(700, 500)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel(f"Notes de: {self.etudiant_name}")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # Section d'ajout de note
        note_group = QGroupBox("Saisir une note")
        note_layout = QHBoxLayout()

        self.matiere_combo = QComboBox()
        self.note_spin = QDoubleSpinBox()
        self.note_spin.setRange(0, 20)
        self.note_spin.setDecimals(2)

        self.add_note_btn = QPushButton("Ajouter Note")
        self.add_note_btn.clicked.connect(self.add_note)

        note_layout.addWidget(QLabel("Matière:"))
        note_layout.addWidget(self.matiere_combo)
        note_layout.addWidget(QLabel("Note:"))
        note_layout.addWidget(self.note_spin)
        note_layout.addWidget(self.add_note_btn)
        note_layout.addStretch()

        note_group.setLayout(note_layout)
        layout.addWidget(note_group)

        # Boutons d'action
        button_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Modifier Note")
        self.delete_btn = QPushButton("Supprimer Note")
        self.bulletin_btn = QPushButton("Générer Bulletin")

        self.edit_btn.clicked.connect(self.edit_note)
        self.delete_btn.clicked.connect(self.delete_note)
        self.bulletin_btn.clicked.connect(self.generate_bulletin)

        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.bulletin_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table des notes
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Matière", "Note", "Semestre", "Crédits", "Année"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Moyennes
        self.moyennes_label = QLabel()
        self.moyennes_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.moyennes_label)

        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        self.load_matieres()

    def load_matieres(self):
        """Charge les matières de la formation"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, credits, annee FROM matieres WHERE formation_id = ? ORDER BY annee, nom",
                       (self.formation_id,))
        data = cursor.fetchall()
        conn.close()

        self.matiere_combo.clear()
        for matiere in data:
            self.matiere_combo.addItem(f"{matiere[1]} (Année {matiere[3]})", matiere[0])

    def load_data(self):
        """Charge les notes de l'étudiant"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.nom, n.note, n.semestre, m.credits, m.annee
            FROM notes n
            JOIN matieres m ON n.matiere_id = m.id
            WHERE n.etudiant_id = ?
            ORDER BY m.annee, m.nom, n.semestre
        ''', (self.etudiant_id,))
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col in range(5):
                self.table.setItem(row, col, QTableWidgetItem(str(item[col]) if item[col] else ""))

        self.calculate_moyennes()

    def calculate_moyennes(self):
        """Calcule et affiche les moyennes"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # Moyenne générale
        cursor.execute('''
            SELECT AVG(n.note), SUM(m.credits)
            FROM notes n
            JOIN matieres m ON n.matiere_id = m.id
            WHERE n.etudiant_id = ?
        ''', (self.etudiant_id,))
        result = cursor.fetchone()

        if result and result[0]:
            moyenne_generale = round(result[0], 2)
            total_credits = result[1] or 0

            # Moyenne par semestre
            cursor.execute('''
                SELECT n.semestre, AVG(n.note), COUNT(*)
                FROM notes n
                WHERE n.etudiant_id = ?
                GROUP BY n.semestre
            ''', (self.etudiant_id,))
            moyennes_semestre = cursor.fetchall()

            text = f"Moyenne générale: {moyenne_generale}/20 (Total crédits: {total_credits})\n"
            for sem in moyennes_semestre:
                text += f"Semestre {sem[0]}: {round(sem[1], 2)}/20 ({sem[2]} matières)\n"

            self.moyennes_label.setText(text)
        else:
            self.moyennes_label.setText("Aucune note saisie")

        conn.close()

    def add_note(self):
        if self.matiere_combo.currentData():
            matiere_id = self.matiere_combo.currentData()
            note = self.note_spin.value()
            conn = self.db_manager.get_connection()


            cursor = conn.cursor()

            # Récupérer le semestre de la matière
            cursor.execute("SELECT semestre FROM matieres WHERE id = ?", (matiere_id,))
            semestre = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM notes WHERE etudiant_id = ? AND matiere_id = ? AND semestre = ?",
                           (self.etudiant_id, matiere_id, semestre))

            existing = cursor.fetchone()

            if existing:
                QMessageBox.warning(self, "Erreur", "Une note existe déjà pour cette matière et ce semestre!")
            else:
                cursor.execute("INSERT INTO notes (etudiant_id, matiere_id, note, semestre) VALUES (?, ?, ?, ?)",
                               (self.etudiant_id, matiere_id, note, semestre))

                conn.commit()
                self.load_data()
                QMessageBox.information(self, "Succès", "Note ajoutée avec succès!")

            conn.close()

    def edit_note(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            matiere = self.table.item(current_row, 0).text()
            note_value = float(self.table.item(current_row, 1).text())
            semestre = int(self.table.item(current_row, 2).text())

            # Dialog simple pour modifier la note
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Modifier Note - {matiere}")
            dialog.setModal(True)

            layout = QFormLayout()

            note_spin = QDoubleSpinBox()
            note_spin.setRange(0, 20)
            note_spin.setDecimals(2)
            note_spin.setValue(note_value)

            semestre_combo = QComboBox()
            semestre_combo.addItems(["1", "2"])
            semestre_combo.setCurrentText(str(semestre))

            layout.addRow("Note:", note_spin)
            layout.addRow("Semestre:", semestre_combo)

            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                          QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)

            layout.addWidget(button_box)
            dialog.setLayout(layout)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_note = note_spin.value()
                new_semestre = int(semestre_combo.currentText())

                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE notes 
                    SET note = ?, semestre = ? 
                    WHERE etudiant_id = ? 
                    AND matiere_id = (SELECT id FROM matieres WHERE nom = ?)
                    AND semestre = ?
                ''', (new_note, new_semestre, self.etudiant_id, matiere, semestre))
                conn.commit()
                conn.close()

                self.load_data()
                QMessageBox.information(self, "Succès", "Note modifiée avec succès!")

    def delete_note(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            matiere = self.table.item(current_row, 0).text()
            semestre = int(self.table.item(current_row, 2).text())

            reply = QMessageBox.question(self, "Confirmation",
                                         "Êtes-vous sûr de vouloir supprimer cette note?")
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM notes 
                    WHERE etudiant_id = ? 
                    AND matiere_id = (SELECT id FROM matieres WHERE nom = ?)
                    AND semestre = ?
                ''', (self.etudiant_id, matiere, semestre))
                conn.commit()
                conn.close()

                self.load_data()
                QMessageBox.information(self, "Succès", "Note supprimée avec succès!")

    def generate_bulletin(self):
        """Génère un bulletin de notes"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # Récupérer les informations de l'étudiant
        cursor.execute("SELECT matricule, nom, prenom FROM etudiants WHERE id = ?", (self.etudiant_id,))
        etudiant_info = cursor.fetchone()

        # Récupérer toutes les notes avec détails
        cursor.execute('''
            SELECT m.nom, n.note, n.semestre, m.credits, m.annee
            FROM notes n
            JOIN matieres m ON n.matiere_id = m.id
            WHERE n.etudiant_id = ?
            ORDER BY m.annee, n.semestre, m.nom
        ''', (self.etudiant_id,))
        notes = cursor.fetchall()

        # Calculs des moyennes
        cursor.execute('''
            SELECT AVG(n.note), SUM(m.credits)
            FROM notes n
            JOIN matieres m ON n.matiere_id = m.id
            WHERE n.etudiant_id = ?
        ''', (self.etudiant_id,))
        moyenne_result = cursor.fetchone()

        conn.close()

        # Créer le bulletin
        bulletin = BulletinDialog(self, etudiant_info, notes, moyenne_result)
        bulletin.exec()

class BulletinDialog(QDialog):
    def __init__(self, parent, etudiant_info, notes, moyenne_result):
        super().__init__(parent)
        self.etudiant_info = etudiant_info
        self.notes = notes
        self.moyenne_result = moyenne_result
        self.setWindowTitle("Bulletin de Notes")
        self.setModal(True)
        self.resize(600, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # En-tête du bulletin
        header = QLabel("BULLETIN DE NOTES")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)

        # Informations étudiant
        info_text = f"""
        Matricule: {self.etudiant_info[0]}
        Nom: {self.etudiant_info[1]}
        Prénom: {self.etudiant_info[2]}
        """
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label)

        # Tableau des notes
        bulletin_text = QTextEdit()
        bulletin_text.setReadOnly(True)

        content = "<h3>Détail des Notes</h3>"
        content += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        content += "<tr><th>Matière</th><th>Année</th><th>Semestre</th><th>Note</th><th>Crédits</th></tr>"

        for note in self.notes:
            matiere, valeur_note, semestre, credits, annee = note
            content += f"<tr><td>{matiere}</td><td>{annee}</td><td>{semestre}</td><td>{valeur_note}</td><td>{credits}</td></tr>"

        content += "</table>"

        # Moyennes
        if self.moyenne_result and self.moyenne_result[0]:
            moyenne_generale = round(self.moyenne_result[0], 2)
            total_credits = self.moyenne_result[1] or 0
            content += f"<h3>Résultats</h3>"
            content += f"<p><strong>Moyenne Générale:</strong> {moyenne_generale}/20</p>"
            content += f"<p><strong>Total Crédits:</strong> {total_credits}</p>"

            # Appréciation
            if moyenne_generale >= 16:
                appreciation = "Très Bien"
            elif moyenne_generale >= 14:
                appreciation = "Bien"
            elif moyenne_generale >= 12:
                appreciation = "Assez Bien"
            elif moyenne_generale >= 10:
                appreciation = "Passable"
            else:
                appreciation = "Insuffisant"

            content += f"<p><strong>Appréciation:</strong> {appreciation}</p>"

        bulletin_text.setHtml(content)
        layout.addWidget(bulletin_text)

        # Boutons
        button_layout = QHBoxLayout()
        print_btn = QPushButton("Imprimer")
        close_btn = QPushButton("Fermer")

        print_btn.clicked.connect(self.print_bulletin)
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(print_btn)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def print_bulletin(self):
        QMessageBox.information(self, "Impression", "Fonctionnalité d'impression à implémenter")

class EtudiantsTab(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Titre
        title = QLabel("Gestion des Étudiants")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Boutons d'action
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Ajouter Étudiant")
        self.edit_btn = QPushButton("Modifier")
        self.delete_btn = QPushButton("Supprimer")

        self.add_btn.clicked.connect(self.add_etudiant)
        self.edit_btn.clicked.connect(self.edit_etudiant)
        self.delete_btn.clicked.connect(self.delete_etudiant)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table des étudiants
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Matricule", "Nom", "Prénom", "Email", "Téléphone"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM etudiants ORDER BY nom, prenom")
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))

    def add_etudiant(self):
        dialog = EtudiantDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['matricule'] and data['nom'] and data['prenom']:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO etudiants (matricule, nom, prenom, email, telephone) VALUES (?, ?, ?, ?, ?)",
                        (data['matricule'], data['nom'], data['prenom'], data['email'], data['telephone']))
                    conn.commit()
                    self.load_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Succès", "Étudiant ajouté avec succès!")
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Erreur", "Ce matricule existe déjà!")
                finally:
                    conn.close()

    def edit_etudiant(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            etudiant_id = int(self.table.item(current_row, 0).text())
            etudiant_data = []
            for col in range(6):
                etudiant_data.append(self.table.item(current_row, col).text())

            dialog = EtudiantDialog(self, etudiant_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data['matricule'] and data['nom'] and data['prenom']:
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE etudiants SET matricule=?, nom=?, prenom=?, email=?, telephone=? WHERE id=?",
                                   (data['matricule'], data['nom'], data['prenom'], data['email'], data['telephone'],
                                    etudiant_id))
                    conn.commit()
                    conn.close()
                    self.load_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Succès", "Étudiant modifié avec succès!")

    def delete_etudiant(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            etudiant_id = int(self.table.item(current_row, 0).text())
            reply = QMessageBox.question(self, "Confirmation",
                                         "Êtes-vous sûr de vouloir supprimer cet étudiant?")
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM etudiants WHERE id=?", (etudiant_id,))
                conn.commit()
                conn.close()
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Succès", "Étudiant supprimé avec succès!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.setWindowTitle("Système de Gestion des Étudiants")
        self.setGeometry(100, 100, 1200, 800)

        self.setup_ui()

        # Connecter les signaux pour la mise à jour automatique
        self.connect_update_signals()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Titre principal
        title = QLabel("Système de Gestion des Étudiants et des Notes")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        # Onglets
        self.tab_widget = QTabWidget()

        # Créer les onglets
        self.departements_tab = DepartementsTab(self.db_manager)
        self.formations_tab = FormationsTab(self.db_manager)
        self.etudiants_tab = EtudiantsTab(self.db_manager)

        # Ajouter les onglets
        self.tab_widget.addTab(self.departements_tab, "Départements")
        self.tab_widget.addTab(self.formations_tab, "Formations")
        self.tab_widget.addTab(self.etudiants_tab, "Étudiants")

        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)

    def connect_update_signals(self):
        """Connecte les signaux pour la mise à jour automatique des onglets"""
        # Quand les départements changent, mettre à jour les formations
        self.departements_tab.data_changed.connect(self.formations_tab.load_data)

        # Quand les formations changent, mettre à jour les autres onglets si nécessaire
        self.formations_tab.data_changed.connect(self.refresh_all_tabs)

        # Quand les étudiants changent, rafraîchir si nécessaire
        self.etudiants_tab.data_changed.connect(self.refresh_all_tabs)

    def refresh_all_tabs(self):
        """Rafraîchit tous les onglets"""
        self.departements_tab.load_data()
        self.formations_tab.load_data()
        self.etudiants_tab.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())