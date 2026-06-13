# Suno – Referenz & Spickzettel

Praxis-Referenz für das Schreiben von Songtexten und Prompts in Suno
(Stand: Modelle v4 / v4.5 / v5, 2026). Tags sind **Signale, keine Garantien** –
das Modell folgt ihnen meist, aber nicht zu 100 %.

---

## 1. Das Grundprinzip: zwei getrennte Felder

Suno hat zwei Eingaben, die man strikt trennen sollte:

| Feld | Was reinkommt | Was NICHT reinkommt |
|------|---------------|---------------------|
| **Style / Style of Music** (das Genre-/Sound-Feld) | Genre, Tempo-Gefühl, Instrumente, Stimm-Charakter, Mix, Stimmung | Keine Lyrics, keine `[Verse]`-Tags |
| **Lyrics** (das Text-Feld) | Songtext + Struktur-Tags in `[ ]` + Ad-libs in `( )` | Keine Sound-Beschreibungen, keine Sternchen `*`, keine Genre-Begriffe |

**Faustregel:** Sound → Style-Feld. Struktur & Text → Lyrics-Feld.

---

## 2. Das Style-Feld (Sound-Beschreibung)

Kurz, modular, kommagetrennt. Bewährte Formel:

> Genre + Subgenre, Tempo-Gefühl, 3–4 Kerninstrumente, Stimm-Absicht, Mix, eine Stimmung

**Beispiel:**
```
melodic techno, 124 bpm feel, rolling bass, airy synths,
restrained vocal hook, clean club mix, late-night tension
```

Tipps:
- **Tempo lieber beschreibend** als nur BPM ("driving", "laid-back", "halftime feel").
- Die **ersten 20–30 Wörter** wirken am stärksten – Wichtigstes nach vorne.
- Gleiches Style-Feld wiederverwenden und nur Lyrics tauschen → konsistente Songs.
- Immer nur **eine Variable** ändern, um zu sehen was wirkt.
- Für Dialekt/Sprache: hier z. B. `Austrian dialect vocals`, `Viennese`,
  `Austropop` ergänzen (siehe Abschnitt 8).

---

## 3. Das Lyrics-Feld: Struktur-Tags `[ ]`

Bracketed Section-Labels gliedern den Song. Erkannte Standard-Tags:

```
[Intro]            Eröffnung / Atmosphäre (optional: [Intro: Acoustic guitar])
[Verse]            Strophe / Erzähl-Teil  (auch [Verse 1], [Verse 2])
[Pre-Chorus]       Aufbau / Spannung vor dem Refrain
[Chorus]           Refrain / Hook – der stärkste Teil
[Post-Chorus]      Nachklang nach dem Refrain
[Bridge]           Kontrast-Teil, meist nach dem 2. Refrain
[Break]            Pause / Instrumental-Unterbruch
[Breakdown]        Reduzierter, gestripppter Teil
[Build] / [Build-Up]  steigende Spannung
[Drop]             Einschlag / Beat-Drop (EDM)
[Hook]             eingängiger Wiederhol-Teil
[Instrumental]     reiner Instrumentalteil
[Guitar Solo]      Solo (analog: [Piano Solo], [Drum Fill])
[Final Chorus]     Refrain kehrt größer zurück
[Outro]            Ausklang / Auflösung
[End]              klares Ende (gegen langes Ausfaden)
```

**Schreibweise:**
- Tag steht in **eckigen Klammern**, allein auf einer eigenen Zeile, danach der Text.
- Tags **kurz halten** (1–3 Wörter). Lange/seltene Tags werden ignoriert –
  oder schlimmstenfalls **mitgesungen** (z. B. `[Soaring Guitar Solo with Divebomb]`
  landet dann wörtlich im Gesang).

**Beispiel-Gerüst:**
```
[Intro]

[Verse 1]
... Zeile ...
... Zeile ...

[Pre-Chorus]
...

[Chorus]
...

[Verse 2]
...

[Bridge]
...

[Final Chorus]
...

[Outro]
```

---

## 4. Gesangs- & Stimm-Tags

In `[ ]`, vor der jeweiligen Sektion oder am Sektions-Tag angehängt:

```
[Female Vocal] / [Male Vocal]      Geschlecht
[Duet]                             Wechselgesang
[Group Vocals]                     alle zusammen / Chor
[Whisper] / [Whispered]            geflüstert
[Spoken Word]                      gesprochen, rhythmisch
[Belted]                           kraftvoll / laut geschmettert
[Harmonies]                        mehrstimmig
[Vocoder] / [Reverb]               Effekte
```

Kombiniert mit Sektion:
```
[Verse 1 - Whispered]
[Chorus - Belted]
[Chorus - Group Vocals]
```

---

## 5. Ad-libs & Vokal-Cues: runde Klammern `( )`

Kleine Gesangs-Anweisungen oder Echo-/Backing-Vocals stehen in **runden**
Klammern – **innerhalb** der Lyrics, eigene Zeile, direkt **vor** der Zeile,
auf die sie sich beziehen:

```
(softly)
Ich geh durch d'Nacht...

(building energy)
Und auf amoi steht alles still

I siech di (oh-oh)        ← Backing-/Echo direkt in der Zeile
```

**Sparsam einsetzen:** 1–2 Cues wirken, 10 Cues verwirren das Modell und
zerstören den Text.

---

## 6. Instrument- & Produktions-Tags

```
[Piano] [808s] [Distorted Guitar] [Strings] [Synth] [Brass]
[Guitar Solo] [Drum Fill] [Bass Drop] [Instrumental Break]
```

Optionale Dynamik-/Stimmungs-Descriptoren (sparsam):
```
[Energy: High] / [Energy: Medium]
[Mood: melancholic]
[Tempo: slow]
```

---

## 7. Platzierungs-Regeln (das Wichtigste)

1. **Top-load:** Palette/Stimmung/Energie vor die erste Textzeile setzen.
2. **Lokalisieren:** Energie-/Stimmungs-Tag direkt **vor** die Sektion, die
   sich ändern soll – nicht global verstreuen.
3. **Klammern konsequent:** `[ ]` = Struktur/Anweisung, `( )` = Ad-lib/Cue.
4. **Ohne Tags** behandelt Suno deinen Text als Rohmaterial und ordnet ihn
   beliebig um – Struktur-Tags geben dir die Kontrolle zurück.
5. **Tags sind Signale, keine Garantie.** Wenn etwas ignoriert wird: kürzen,
   umformulieren oder in mehreren Generationen testen.

---

## 8. Tipps für österreichischen Dialekt / Austropop

- **Sprache im Lyrics-Feld** schreiben wie es klingen soll – phonetisch im
  Dialekt (`i` statt „ich", `net` statt „nicht", `oida`, `ned`, `wos`, `hod`).
  Suno singt weitgehend das, was im Text steht.
- **Im Style-Feld** den Klang vorgeben, z. B.:
  `Austropop, Austrian/Viennese dialect vocals, acoustic guitar, warm,
  storytelling, 90s Austropop feel`
- Bekannte Klangwelten als Referenz: Wienerlied, Austropop, Mundart-Pop,
  Liedermacher/Singer-Songwriter.
- Reim & Metrum im Dialekt selbst sauber bauen – Suno übernimmt Betonung
  grob aus deiner Silbenzahl pro Zeile.
- Vorsicht: sehr seltene Dialektwörter kann das Modell „verschlucken" oder
  hochdeutsch glätten – ggf. phonetischer schreiben.

---

## 9. Mini-Vorlage zum Kopieren

**Style-Feld:**
```
Austropop, warm acoustic guitar, soft drums, intimate Austrian dialect vocals,
storytelling, mid-tempo, nostalgic
```

**Lyrics-Feld:**
```
[Intro]

[Verse 1]
(softly)
... Dialekt-Zeile ...
... Dialekt-Zeile ...

[Pre-Chorus]
... Aufbau ...

[Chorus]
... Hook, eingängig ...
... Hook-Wiederholung ...

[Verse 2]
...

[Bridge]
(building energy)
...

[Final Chorus]
...

[Outro]
```

---

## Quellen

- [Suno Tags List – Metatags, Voice & Style Tags (Musci.io, 2026)](https://musci.io/blog/suno-tags)
- [Suno AI Meta Tags & Song Structure Guide – Jack Righteous](https://jackrighteous.com/en-us/pages/suno-ai-meta-tags-guide)
- [How to structure prompts for Suno AI (Style vs. Lyrics)](https://howtopromptsuno.com/making-music)
- [Suno Lyric Prompts – Template Guide with Section Tags & Vocal Cues (Medium, 2026)](https://medium.com/@aitooldiscovery/suno-ai-lyric-prompts-complete-template-guide-with-section-tags-and-vocal-cues-2026-d5a87bcdd032)
- [Suno Lyrics Formatting: Tags That Work (HookGenius, 2026)](https://hookgenius.app/learn/suno-lyrics-formatting/)
- [Suno AI Metatags Guide: 500+ Pro Tags (OpenMusicPrompt, 2026)](https://openmusicprompt.com/blog/suno-ai-metatags-guide)
