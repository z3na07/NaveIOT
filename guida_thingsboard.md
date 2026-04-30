# Guida ThingsBoard — Dashboard "Cruise-IoT Monitor"
## Progetto 5E · Fase 5

---

## PANORAMICA

Questa guida copre tutto il necessario per configurare ThingsBoard Cloud e
realizzare la Dashboard richiesta dalla specifica di progetto:

1. Registrazione e accesso a ThingsBoard Cloud
2. Creazione del Device `GIOT-001` e recupero dell'Access Token
3. Configurazione del Device Profile con regole di allarme
4. Creazione degli Entity Alias
5. Creazione della Dashboard con tutti i widget richiesti
6. Test e verifica del flusso dati

---

## PARTE 1 — REGISTRAZIONE E ACCESSO

### Passo 1.1 — Creare l'account

1. Aprire il browser e andare su: **https://thingsboard.cloud**
2. Cliccare su **"Try it free"** oppure **"Sign Up"**
3. Compilare il form:
   - Full Name: inserire il proprio nome
   - Email: inserire un'email valida
   - Password: scegliere una password sicura
4. Cliccare **"Create Account"**
5. Aprire la casella email e cliccare sul link di conferma ricevuto
6. Tornare su https://thingsboard.cloud e fare **Login**

> Il piano gratuito (Community/Trial) è sufficiente per questo progetto.

---

## PARTE 2 — CREAZIONE DEL DEVICE

### Passo 2.1 — Aprire la sezione Entities → Devices

1. Nel menu laterale sinistro cliccare su **"Entities"**
2. Dal sotto-menu cliccare su **"Devices"**
3. Apparirà la lista dei device (inizialmente vuota)

### Passo 2.2 — Creare il device GIOT-001

1. Cliccare sul pulsante **"+"** (Add device) in alto a destra
2. Selezionare **"Add new device"**
3. Compilare il form:
   - **Name:** `GIOT-001`
   - **Label:** `Gateway Nave 1` (opzionale, descrittivo)
   - **Device Profile:** `default` (per ora lasciare il default)
4. Cliccare **"Next: Credentials"**
5. Nella scheda Credentials:
   - **Credentials type:** lasciare `Access token`
   - **Access token:** ThingsBoard ne genera uno automaticamente
   - Copiare il token mostrato (es. `A1b2C3d4E5f6G7h8I9j0`)
6. Cliccare **"Add"** per confermare

> IMPORTANTE: Salvare subito il token copiato. Servirà nel file `parametri.json`.

### Passo 2.3 — Inserire il token nel progetto

Aprire `configurazione/parametri.json` e sostituire il valore di `TB_ACCESS_TOKEN`:

```json
{
  "TB_ACCESS_TOKEN": "A1b2C3d4E5f6G7h8I9j0"
}
```

---

## PARTE 3 — DEVICE PROFILE E REGOLE DI ALLARME

Il Device Profile definisce le soglie che attivano gli allarmi visibili
nella Dashboard (temperatura fuori range, umidità fuori range, ecc.).

### Passo 3.1 — Creare un Device Profile dedicato

1. Menu laterale → **"Profiles"** → **"Device Profiles"**
2. Cliccare **"+"** → **"Add device profile"**
3. Nome: `Profilo-Nave`
4. Cliccare **"Next"** fino alla scheda **"Alarm Rules"**

### Passo 3.2 — Aggiungere la regola allarme Temperatura Alta

1. Nella scheda **"Alarm Rules"** cliccare **"Add alarm rule"**
2. Compilare:
   - **Alarm type:** `Temperatura Alta`
   - **Severity:** `Critical`
3. Nella sezione **"Create alarm"** cliccare **"Add condition"**
4. Cliccare su **"Add key filter"**:
   - **Key type:** `Time series`
   - **Key:** `temperatura`
   - **Value type:** `Numeric`
   - **Operation:** `greater than`
   - **Value:** `35`
5. Cliccare **"Add"** → **"Save"**

### Passo 3.3 — Aggiungere la regola allarme Temperatura Bassa

Ripetere il Passo 3.2 con:
- **Alarm type:** `Temperatura Bassa`
- **Severity:** `Warning`
- **Condition:** `temperatura` → `less than` → `15`

### Passo 3.4 — Aggiungere la regola allarme Umidità Alta

Ripetere con:
- **Alarm type:** `Umidita Alta`
- **Severity:** `Warning`
- **Condition:** `umidita` → `greater than` → `80`

### Passo 3.5 — Salvare e assegnare il profilo al device

1. Cliccare **"Add"** per salvare il Device Profile
2. Tornare su **"Entities"** → **"Devices"** → cliccare su `GIOT-001`
3. Cliccare sull'icona matita (Edit)
4. Nel campo **"Device Profile"** selezionare `Profilo-Nave`
5. Cliccare **"Apply changes"**

---

## PARTE 4 — ENTITY ALIASES

Gli Alias permettono di creare una Dashboard dinamica: l'utente seleziona
la nave dal menu e tutti i widget si aggiornano automaticamente.

### Passo 4.1 — Aprire la sezione Dashboard

1. Menu laterale → **"Dashboards"**
2. Cliccare **"+"** → **"Create new dashboard"**
3. Nome: `Cruise-IoT Monitor`
4. Cliccare **"Add"**
5. Aprire la dashboard appena creata cliccando sul suo nome
6. Cliccare **"Edit"** (icona matita in basso a destra)

### Passo 4.2 — Creare l'Entity Alias per la selezione della Nave

1. In modalità Edit cliccare sull'icona **"Entity aliases"** (icona a forma di link)
2. Cliccare **"Add alias"**
3. Compilare:
   - **Alias name:** `Dispositivo Selezionato`
   - **Filter type:** `Entity list`
   - **Type:** `Device`
   - **Entity list:** cercare e selezionare `GIOT-001`
4. Cliccare **"Add"** → **"Save"**

> Quando in futuro aggiungerete più navi, cambiate il Filter type in
> `Entity name contains` con il valore `GIOT` per includerle tutte automaticamente.

---

## PARTE 5 — CREAZIONE DEI WIDGET

Ora si aggiungono i widget uno per uno alla Dashboard.
Ogni widget viene aggiunto cliccando **"Add widget"** (icona "+" in basso a destra
della Dashboard in modalità Edit).

---

### WIDGET 1 — Termometro Circolare (Gauge Temperatura)

**Scopo:** Mostrare la temperatura in tempo reale con soglie di colore.

1. Cliccare **"Add widget"**
2. Nel catalogo widget cercare: **"Radial gauge"** oppure **"Gauge"**
3. Selezionare la categoria **"Gauges"** → scegliere **"Radial gauge"**
4. Cliccare **"Add"**

**Configurazione Datasource:**
1. In **"Datasource"** selezionare **"Entity alias"** → `Dispositivo Selezionato`
2. In **"Data key"** scrivere `temperatura` e premere Invio
3. Cliccare su **"Data key settings"** (icona ingranaggio accanto alla chiave)
4. Impostare **"Label":** `Temperatura (°C)`
5. Cliccare **"Save"**

**Configurazione Advanced (soglie colore):**
1. Cliccare sulla scheda **"Advanced"** o **"Widget settings"**
2. Impostare:
   - **Min value:** `0`
   - **Max value:** `50`
3. Nella sezione **"Ticks/Levels"** aggiungere le soglie:
   - `0–20` → colore **Blu** (freddo)
   - `20–28` → colore **Verde** (comfort)
   - `28–35` → colore **Giallo** (warning)
   - `35–50` → colore **Rosso** (critical)
4. In **"Unit title":** scrivere `°C`
5. Cliccare **"Add"**

---

### WIDGET 2 — Indicatore Umidità (Barra)

**Scopo:** Mostrare l'umidità relativa con indicatore a barra.

1. Cliccare **"Add widget"**
2. Cercare **"Linear gauge"** nella categoria **"Gauges"**
3. Cliccare **"Add"**

**Configurazione Datasource:**
1. Stessa procedura del Widget 1, ma la chiave è `umidita`
2. **Label:** `Umidità (%)`

**Advanced:**
- **Min:** `0` — **Max:** `100`
- Soglie:
  - `0–30` → **Giallo** (secco)
  - `30–70` → **Verde** (comfort)
  - `70–100` → **Rosso** (troppo umido)
- **Unit title:** `%`

---

### WIDGET 3 — Grafico Storico Temperatura e Umidità (Time Series)

**Scopo:** Visualizzare l'andamento delle ultime 24 ore con zoom e tooltip.

1. Cliccare **"Add widget"**
2. Categoria: **"Charts"** → scegliere **"Time series chart"**
3. Cliccare **"Add"**

**Configurazione Datasource:**
1. In **"Datasource"** → **"Entity alias"** → `Dispositivo Selezionato`
2. Aggiungere due chiavi:
   - Prima chiave: `temperatura` → Label: `Temperatura (°C)` → colore rosso
   - Cliccare **"Add data key"** → seconda chiave: `umidita` → Label: `Umidità (%)` → colore blu
3. Cliccare su ciascuna chiave per assegnare l'asse Y:
   - `temperatura` → **Axis:** `Left`
   - `umidita` → **Axis:** `Right` (asse secondario)

**Configurazione Time Window:**
1. Cliccare sulla scheda **"Time window"** (icona orologio in alto nel widget)
2. Selezionare **"Realtime"** → **"Last 24 hours"**
3. Attivare **"Show aggregation buttons"** per permettere zoom

**Advanced:**
- Attivare **"Enable zoom":** sì
- Attivare **"Show points on line":** sì (migliora la leggibilità)
- **Tooltip:** attivare `Show tooltip` per mostrare i valori al passaggio del mouse

---

### WIDGET 4 — LED Connettività (Stato Invio Dati)

**Scopo:** Mostrare un LED rosso se il device non invia dati da più di 5 minuti.

1. Cliccare **"Add widget"**
2. Categoria: **"Status indicators"** → scegliere **"Entity status"**
   oppure cercare **"Simple card"** o **"LED indicator"**
3. In alternativa usare **"HTML card"** per un controllo completo

**Metodo consigliato — usando "Value card" con soglia:**
1. Selezionare **"Value card"** dalla categoria **"Cards"**
2. **Datasource:** `Dispositivo Selezionato`
3. **Data key:** selezionare il tipo **"Attribute"** → **"Server attribute"**
   → cercare `active`

**Configurazione soglia colore:**
1. Nella scheda **"Advanced"** attivare **"Color function"**
2. Inserire la funzione JavaScript:

```javascript
// Cambia colore in base all'ultimo invio
// ThingsBoard aggiorna 'active' automaticamente dopo 5 min di silenzio
if (value === true) {
    return 'green';
} else {
    return 'red';
}
```

3. **Label:** `Connettività Device`
4. In **"Widget settings"** impostare l'icona: cercare `wifi` o `sensors`

> ThingsBoard marca automaticamente un device come `active = false` dopo
> 5 minuti senza telemetria, che è esattamente il requisito della specifica.

---

### WIDGET 5 — Tabella Allarmi con pulsante Acknowledge

**Scopo:** Mostrare gli allarmi attivi con possibilità di riconoscerli.

1. Cliccare **"Add widget"**
2. Categoria: **"Alarm widgets"** → selezionare **"Alarms table"**
3. Cliccare **"Add"**

**Configurazione Datasource:**
1. **Alarm source:** `Dispositivo Selezionato`
2. Attivare **"Search propagated alarms":** sì

**Configurazione colonne visibili:**
- Spuntare: `Created time`, `Type`, `Severity`, `Status`, `Originator`
- Deselezionare le colonne non necessarie

**Configurazione filtri:**
1. **Alarm status filter:**
   - Spuntare `Active`
   - Spuntare `Acknowledged`
2. **Severity:** lasciare tutto selezionato

**Aggiungere il pulsante Acknowledge:**
1. Nella scheda **"Actions"** del widget cliccare **"Add action"**
2. Compilare:
   - **Action name:** `Riconosci`
   - **Icon:** `done` o `check`
   - **Action type:** `Acknowledge alarm`
3. Cliccare **"Add"**

> Il pulsante apparirà come icona nella colonna destra della tabella.
> Cliccandolo l'allarme cambia stato da `Active` ad `Acknowledged`.

---

### WIDGET 6 (BONUS) — Mappa Navale (Image Map)

**Scopo:** Planimetria della nave con cabine che cambiano colore in base agli allarmi.

1. Cliccare **"Add widget"**
2. Categoria: **"Maps"** → selezionare **"Image map"**
3. Cliccare **"Add"**

**Configurazione immagine:**
1. Nella scheda **"Image map settings"** cliccare **"Upload image"**
2. Caricare la planimetria della nave (file PNG/JPG)
   - In assenza di una planimetria reale, creare un rettangolo semplice
     con cabine numerate usando qualsiasi editor grafico

**Aggiungere i marker delle cabine:**
1. Cliccare **"Add datasource"**
2. Selezionare `Dispositivo Selezionato`
3. Cliccare sulla mappa nel punto dove posizionare il marker della cabina
4. Il marker mostrerà il nome del device

**Color function per allarmi:**
1. Nelle impostazioni del marker attivare **"Color function"**
2. Inserire:

```javascript
// Verde = nessun allarme, Giallo = warning, Rosso = critical
if (alarmCount > 0) {
    return '#FF4444';  // Rosso
} else {
    return '#44BB44';  // Verde
}
```

---

## PARTE 6 — LAYOUT E IMPOSTAZIONI FINALI

### Passo 6.1 — Organizzare il layout della Dashboard

In modalità Edit trascinare i widget per organizzarli:

```
┌─────────────────────────────────────────────────────┐
│           CRUISE-IoT MONITOR  [Selezione Nave ▼]    │
├───────────────┬───────────────┬─────────────────────┤
│  Termometro   │  Umidità      │  LED Connettività   │
│  (Gauge °C)   │  (Gauge %)    │  ● ONLINE           │
├───────────────┴───────────────┴─────────────────────┤
│         Grafico Storico 24h (Temp + Umidità)        │
│                                                      │
├─────────────────────────────────────────────────────┤
│              Tabella Allarmi Attivi                 │
│  Ora  │  Tipo  │  Gravità  │  Stato  │  [✓ ACK]   │
└─────────────────────────────────────────────────────┘
```

### Passo 6.2 — Aggiungere il menu di selezione nave (Entity Select)

1. Cliccare **"Add widget"**
2. Cercare **"Entity select"** o **"Entities hierarchy"**
3. Selezionare **"Entity select"**
4. Configurare per mostrare i device con nome che contiene `GIOT`
5. Collegare all'alias `Dispositivo Selezionato`
6. Posizionare in alto nella dashboard

> Quando l'utente cambia la selezione, tutti i widget si aggiornano automaticamente.

### Passo 6.3 — Impostare il tema e il titolo

1. In modalità Edit cliccare sull'icona **"Dashboard settings"** (ingranaggio)
2. **Title:** `Cruise-IoT Monitor`
3. **Auto-refresh interval:** `5 seconds` (per aggiornamento in tempo reale)
4. Opzionale → **"Dark theme":** attivare per la consultazione notturna

### Passo 6.4 — Salvare la Dashboard

1. Cliccare il pulsante **"Save"** (icona disco in basso a destra)
2. La Dashboard è ora attiva e visibile

---

## PARTE 7 — TEST DEL SISTEMA COMPLETO

### Passo 7.1 — Avviare i componenti in ordine

Aprire tre terminali separati:

**Terminale 1 — IoTPlatform (subscriber HiveMQ):**
```bash
cd iotp/
python archivia_iotp.py
```

**Terminale 2 — Gateway DA:**
```bash
python iotgwda.py
```

**Terminale 3 — Simulazione DC (se non si ha il Pico):**
```bash
python dc_simulato.py  # oppure avviare il Pico fisicamente
```

### Passo 7.2 — Verificare la ricezione su ThingsBoard

1. Aprire ThingsBoard → **"Entities"** → **"Devices"** → `GIOT-001`
2. Cliccare sulla scheda **"Latest telemetry"**
3. Dovrebbero apparire le chiavi: `temperatura`, `umidita`, `cabina`, `ponte`, ecc.
4. I valori si aggiornano ogni 5 secondi (INTERVALLO nel DC)

### Passo 7.3 — Aprire la Dashboard e verificare i widget

1. Menu → **"Dashboards"** → **"Cruise-IoT Monitor"**
2. Controllare che:
   - [ ] Il Gauge temperatura mostra un valore tra 10 e 40°C
   - [ ] Il Gauge umidità mostra un valore tra 20 e 90%
   - [ ] Il grafico storico inizia a popolarsi
   - [ ] Il LED connettività è verde
   - [ ] La tabella allarmi è vuota (nessun allarme se i valori sono nel range)

### Passo 7.4 — Testare un allarme

Per verificare che gli allarmi funzionino, modificare temporaneamente `dc.py`
oppure `misurazione.py` per inviare una temperatura > 35:

```python
# In misurazione.py, modificare temporaneamente:
def on_temperatura(N):
    return 40.0  # Valore fisso sopra soglia Critical (35°C)
```

Dopo qualche invio, nella tabella allarmi dovrebbe apparire `Temperatura Alta`
con gravità `Critical`. Testare il pulsante **Acknowledge**.

---

## RIEPILOGO FINALE

| Componente | Posizione | Ruolo |
|---|---|---|
| `dc.py` (Pico) | Raspberry Pi Pico W | Legge sensore DHT, invia via TCP |
| `iotgwda.py` | PC Gateway | Riceve TCP, pubblica su HiveMQ (criptato) + ThingsBoard (chiaro) |
| `archivia_iotp.py` | PC IoTPlatform | Subscriber HiveMQ, decripta, salva in `dbplatform.json` |
| ThingsBoard Cloud | Cloud | Riceve telemetria, gestisce allarmi, visualizza Dashboard |
| Dashboard | Browser/Tablet | Gauge, Grafico, LED, Allarmi |

Il progetto è ora completo dalla Fase 1 (lettura sensore) alla Fase 5 (Dashboard professionale).
