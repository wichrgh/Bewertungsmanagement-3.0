# Bewertungsmanagement 3.0
### Strategisches Intranet-Warenwirtschafts- & Produkttest-Dashboard

Ein hochoptimiertes, kaufmännisches Kontrollzentrum zur Erfassung, Verwaltung und Ertrags-Auswertung von Produkttests. Da Lieferantenportale oft intransparent agieren, befähigt dieses Tool den Anwender (Otto), die eigene Performance, finanzielle Gegenwerte (Warenertrag) und Lieferanten-Zuverlässigkeiten autark zu überwachen.

---

## 🎯 Strategische Kernfunktionen & Kern-Engines

### 📊 1. Performanz- & Ertrags-Cockpit (Live-KPIs)
* **Waren-Ertragsrechner:** Live-Ermittlung des akkumulierten Gegenwerts der behaltenden Testartikel (Maximaler, minimaler und durchschnittlicher Artikelpreis pro Bericht).
* **Rezensions-Performance:** Echtzeit-Metrik über verfasste Berichte mitsamt passiver Unterscheidung in qualifizierte Premium-Berichte.
* **Verlust- & Schwund-Metrik:** Erfassung und finanzielle Summierung von auf dem Postweg verloren gegangenen oder gestohlenen Paketen zur harten Lieferanten-Evaluation.

### ✍️ 2. Autonome Medien- & Rezensions-Engine
* **Clientseitige Cursor-Injektion:** Emojis und dynamische Textbausteine werden im 0-Millisekunden-Takt rein über den Browser-Scope exakt an der blinkenden Cursor-Position der Textarea eingeschleust.
* **1:1 Klartext-Übertragung:** Verzicht auf störendes Markdown-Sondermarkup (`**`), um maximale Kompatibilität mit restriktiven Lieferantenportalen bei voller kaufmännischer Layout-Kontrolle zu sichern.
* **Full-Screen-Lightbox mit Lupe:** Proportionale, verzerrungsfreie Bildvergrößerung (2.5x) in einem den gesamten Viewport ausnutzenden Overlay mitsamt mausabhängiger, seidenweicher Fokus-Verschiebung.

### ⚙️ 3. Relationales Stammdaten-Kontrollzentrum
* **On-Demand Hot-Reload:** Kaskadierende Auswahlfelder (Lieferanten, Reward-Profile, Testzeiträume) ziehen sich Daten reaktiv über native `focus`-Bypasses im Moment des Klicks frisch aus der Datenbank.
* **Nahtlosigkeits-Historie:** Chronologische Auflistung vergangener Testperioden direkt in der Zuweisungsmaske, um Überlappungen bei Neuaktivierungen blind auszuschließen.
* **Isolierte Kalender-Käfige:** Physische Kapselung der Quasar-Menüstrukturen im DOM, um fehlerhafte Feld-Überschreibungen (z. B. Lieferdatum schreibt in Bestelldatum) technisch unmöglich zu machen.

---

## 📦 Architektur & Tech-Stack

* **Backend-Logik:** Python 3 (Strikte Trennung in relationale SQLite-Datenbankzugriffe, kaufmännische Validierungselemente und Event-Steuerungen).
* **Frontend-UI:** NiceGUI (Kombination aus Vue/Quasar-Komponenten und Tailwind CSS für schlanke, zuckfreie Oberflächen-Animationen).
* **Datenmodell:** SQLite (Datenbank `projekte.db`). Datumsfelder werden datenbankseitig im strikten ISO-Format (`JJJJ-MM-TT`) für performante Zeitraum-Auswertungen gespeichert und erst im UI reaktiv in das deutsche Format (`TT.MM.JJJJ`) übersetzt.
* **Dateisystem-Schutz:** Integrierter Garbage-Collector, der verwaiste Medien auf der Festplatte automatisch mit dem SQL-Datenbestand abgleicht und bereinigt.

---

## 📂 Repository-Struktur

```text
├── projekte.db            # Relationale SQLite-Datenbank (wird auto-generiert)
├── main.py                # Core-Routing, Kopfzeile & KPI-Cockpit
├── database.py            # SQL-Schema, Datenbankoperationen & KPI-Berechnungen
├── details.py             # Rechter Bedienbereich (Artikel-Stammdaten)
├── events.py              # Entkoppelte kaufmännische Validierungs- & Speicher-Handler
├── media.py               # Asynchrones Bild-Handling & Client-DOM-Targeting
├── media_panel.py         # Zweispaltiger Medienkasten mitsamt Lightbox-Lupe
└── review_panel.py        # Amazon-Bewertungsmodul & reaktives Baustein-System
```

---

## 🚀 Inbetriebnahme

1. **Abhängigkeiten installieren:**
   ```bash
   pip install nicegui
   ```
2. **Dashboard starten:**
   ```bash
   python main.py
   ```
3. Das Tool öffnet sich automatisch unter `http://localhost:8090`. Die Datenbankstrukturen initialisieren sich beim Erststart vollautomatisch im Hintergrund.
