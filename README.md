# 📦 Intranet-Warenwirtschafts- & Produkttest-Dashboard

Ein hochgradig ergonomisches, kaufmännisches Dashboard auf Basis von **Python & NiceGUI (Quasar/Tailwind)** zur effizienten Erfassung von Artikeln und Lieferanten-Testergebnissen. Das System läuft clientseitig zuckfrei und ist speziell für den Breitbild-Einsatz optimiert.

---

## 🛠️ Bereits implementierte Core-Features & Architektur

### 1. Robustes Relationales Datenmodell (SQLite)
* **Künstliche Hintergrund-ID:** Alle Tabellen-Verknüpfungen und Bild-Operationen im RAM laufen stramm über einen künstlichen Primärschlüssel (`ID INTEGER PRIMARY KEY AUTOINCREMENT`). Stammdatenänderungen sind vollkommen entkoppelt.
* **ArtikelNummer-Sicherheit:** Die Spalte `ArtikelNummer` im SQL-Kern ist als `UNIQUE` deklariert. Das System blockiert Dubletten unerbittlich, *bevor* Datei-Operationen ausgeführt werden.
* **Automatische Migration:** Die `database.py` migriert alte Tabellenstrukturen beim Serverstart vollautomatisch auf das neue ID-Schema.

### 2. Autonome Medien- & Galerie-Engine (`media.py` / `media_panel.py`)
* **Unzerstörbare Bild-Rename-Logik:** Ändert Otto nachträglich eine Artikelnummer, benennt Python alle Kacheln auf der Festplatte (`_supplier_`) im selben Bruchteil einer Sekunde geräuschlos um.
* **Autonome SSD-Bereinigung:** Beim Leeren der Maske oder Löschen von Artikeln fegt eine Bereinigungs-Logik verwaiste "Geisterbilder" restlos von der Festplatte.
* **Interaktive Lupe:** Das Großbild verfügt über ein stabiles, nativeres Klick-Zoom-Verhalten (Scale-Effekt), das perfekt im Fenster-Viewport stehen bleibt.

### 3. Kaufmännische Ergonomie & Workflow
* **Lieferanten-Fluchtung:** Bestell-Nr. und Bestellt-Datum fluchten unzertrennlich in Zeile 1 der Erfassungsmaske, gefolgt von Art.-Nr. und kaufmännischem Preis-Formatierer (erzwingt z.B. `45,90 €`).
* **Chronologische SQL-Sortierung:** Die Artikelliste links sortiert die Datensätze standardmäßig datenbankseitig nach dem Bestelldatum (`ORDER BY BestellDatum DESC`), wobei das Datum auf der Festplatte im performanten ISO-Format (`JJJJ-MM-TT`) liegt und für Ottos Augen live in `TT.MM.JJJJ` umgerechnet wird.
* **Einklapp-Gedächtnis:** Der Splitter lässt sich wegklappen und kehrt über ein natives Python-Event verlässlich auf die 30%-Auswahl zurück.

### 4. Amazon-Bewertungsmodul (Eingeleitet)
* **Modulare Struktur:** Der dritte, einklappbare Border-Kasten für das Bewertungsmanagement ist visuell integriert und an eine neue, verknüpfte Tabelle `Bewertungen` angedockt (`FOREIGN KEY` mit `ON DELETE CASCADE`).
* **Textbausteine & Android-Emoji-Board:** Eine editierbare Baustein-Zeile (per Komma trennbar) generiert dynamisch klickbare Überschriften. Ein nach Kategorien sortiertes, 6-spaltiges Emoji-Board ist links unter dem Label verbaut.

---

## 🎯 Offene Roadmap für die neue Session

1. **Cursor-Injektions-Begradigung (`review_panel.py`):** Die Textbausteine und Emojis werden aktuell noch am Textende angehängt. Ziel ist die finale Behebung des Fokus-Verlusts, damit die Injektion präzise an der blinkenden Cursor-Position einrastet.
2. **ISO-Umstellung für das Lieferdatum:** Das Lieferdatum soll exakt dieselbe performante ISO-Behandlung (`JJJJ-MM-TT`) im SQL-Kern erfahren wie das Bestelldatum, um spätere Zeitraum-Auswertungen (z. B. Lieferdauer-Berechnungen) zu ermöglichen.
3. **Mitarbeiter-Reward- & Rollensystem:** Implementierung einer zeitraumbezogenen Punkte-Metrik (z. B. auf 30-Tage-Basis). Fleißige Artikelerfassungen und detaillierte Rezensionen generieren Live-Punkte, die vollautomatisch privilegierte Tester-Rollen ("Premium-Tester") für exklusive, hochpreisige Waren freischalten oder entziehen.
