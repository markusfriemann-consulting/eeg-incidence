# Methodology

"Flow B is allocated to each Bundesland in proportion to its share of total federal tax contribution (Bund's share of Gemeinschaftsteuern + Bundessteuern). This reflects the legal financing mechanism since July 2022, when EEG payments transitioned from EEG-Umlage on electricity consumption to financing from the federal budget."

Flow B (financing burden) is allocated to each Bundesland proportional to the Bund's share of taxes collected in that Bundesland. The Bund share is computed by summing the federal portions of joint taxes (Lohnsteuer 42.5%, Einkommensteuer 42.5%, n.v.St.v.Ertrag 50%, Abgeltungsteuer 44%, Körperschaftsteuer 50%) plus the federal portion of Gewerbesteuerumlage from BMF Übersicht 5a (4. Quartal 2024). Total: €185,721 Mio. This represents direct contribution to the federal budget; pure Bundessteuern (Energiesteuer, Tabaksteuer, etc.) and 100% Ländersteuern are not allocable per Land in this published source and are excluded. The allocation thus reflects ~70% of total federal revenue, with the same proportional structure assumed to apply to the unallocable remainder.


# Methodology

## Question
Which Bundesländer are net recipients and which are net payers in the
2024 EEG system?

## Approach
For each of the 16 Bundesländer plus the offshore zone (AWZ):

  netto_position = verguetung_erhalten - finanzierungslast

where:

- verguetung_erhalten: sum of 2024 EEG-Zahlungen at the Anlage-level
  (Bewegungsdaten 4 ÜNB) joined to Bundesland via MaStR registration
  (€22.67 Mrd total, 99.7% match coverage)

- finanzierungslast: each Land's allocated share of the €18.49 Mrd
  EEG-Finanzierungsbedarf 2024 (federal budget transfer to ÜNB),
  proportional to its 2024 contribution to federal tax revenue
  (Bund-Anteil from BMF Übersicht 5a, 4. Quartal 2024)

## Limitations
- Federal tax allocation reflects ~70% of total federal revenue; the
  remainder (pure Bundessteuern, etc.) cannot be allocated per Land in
  the published source and is assumed to scale proportionally.
- Offshore wind (~€2.07 Mrd) is registered in the AWZ, not in any Land,
  but is paid for by all Länder via the federal budget.
- 0.32% of payments (€73 M) cannot be matched to MaStR registration
  (mostly decommissioned units excluded from the dim_anlage scope).

## Findings
[your top winner/loser bullets here]

## Hinweise zur Bilanzierung

### Warum „Vergütung erhalten" und „Finanzierungslast" sich nicht aufheben

Die Summe aller `verguetung_erhalten_eur` (€22,67 Mrd) ist um etwa
€4 Mrd höher als die Summe aller `finanzierungslast_eur` (€18,49 Mrd).
Das ist kein Datenfehler, sondern strukturell: Die ÜNB erlösen aus dem
Verkauf des EEG-Stroms an der Strombörse zusätzliche Einnahmen
(2024: ~€1 Mrd) und nutzen einen Teil eines vorhandenen Kontostandes,
sodass der Bundeshaushalt den Differenzbetrag tragen muss, nicht die
volle Auszahlungssumme.

### Welche Zahlen in welcher Sicht stehen

- **Vergütung erhalten** misst, was Anlagenbetreiber in einem Bundesland
  konkret an Geld bekommen haben. Diese Zahl ist exakt aus den
  Bewegungsdaten der ÜNB rekonstruiert.

- **Finanzierungslast** misst, was die Steuerzahler eines Bundeslandes
  über den Bundeshaushalt anteilig getragen haben. Diese Zahl ist
  modelliert aus dem realen EEG-Finanzierungsbedarf 2024
  (€18,49 Mrd, Quelle: EEG-Konto Jahresabschluss) multipliziert mit
  dem Anteil des Bundeslandes am Bundesanteil der gemeinschaftlichen
  Steuern (Quelle: BMF Übersicht 5a, 4. Quartal 2024).

- **Netto-Position** ist die Differenz dieser beiden Größen und
  beantwortet die Kernfrage: Wer profitiert wirtschaftlich vom
  EEG-System, und wer trägt die Kosten?

Die Diskrepanz von ~€4 Mrd ist also kein Bug, sondern die Differenz
zwischen Bruttoauszahlung (was ankommt) und Nettokosten für den Bund
(was finanziert werden muss).

### Was bedeutet die Summe der Netto-Positionen?

Wenn man die Netto-Positionen aller Bundesländer und der AWZ aufsummiert,
ergibt sich kein Nullbetrag, sondern ein Plus von ca. €4,2 Mrd.

Das ist kein Bilanzfehler, sondern entspricht den Vermarktungserlösen, die
die Übertragungsnetzbetreiber 2024 aus dem Börsenverkauf des EEG-Stroms
erzielten. Diese Erlöse fließen ins System hinein, ohne aus dem
Bundeshaushalt zu kommen — sie sind die Marktwertschöpfung der EEG-Anlagen
selbst.

Anders ausgedrückt: Von den €22,67 Mrd Vergütungen an Anlagenbetreiber
finanzierten €18,49 Mrd der Steuerzahler (Bundeshaushalt) und €4,18 Mrd
das System selbst durch den Börsenverkauf seines Stroms.