# Scatoletta Blistra

Un portapillole motorizzato open source per chi fa fatica ad aprire blister e scomparti: anziani, persone con artrite o con poca forza nelle mani. All'ora della dose la scatoletta suona e lo scrive sul display; l'utente preme il tasto grande e le pillole di quella dose cadono in un bicchierino che si sfila e si prende in mano.

![La scatoletta chiusa](docs/immagini/v5_chiusa.png)

**Modello 3D interattivo:** https://tigrisxvi.github.io/scatoletta-blistra/ (in inglese e in italiano)

**App Blistra:** https://tigrisxvi.github.io/blistra/ (si prova senza account con la modalità demo)

**Stato: prototipo v0.5, progettato e verificato solo al computer. Non è ancora stato stampato né provato su una scheda vera.**

> ⚠️ Non è un dispositivo medico certificato. Non usarlo come unico promemoria per farmaci importanti. Chi lo costruisce lo fa sotto la propria responsabilità.

## Novità della v1.3: più stretta, caroselli che sporgono

La v1.3 è la v1.2 con una **simmetria a mezzo giro**: la ruota sinistra ha stepper e ricarica dall'alto dietro, la destra davanti. Gli stepper sono girati verso il centro e il loro corpo passa sopra l'altra ruota, così il guscio torna largo 52,9 mm (la v1.2 era 64,2) e le cassette escono di 2 mm dai fianchi con una cornice. Il display è davanti, sotto le ruote. Modello in `cad/scatoletta_v13.py`, controlli in `cad/controlli_v13.py` (tutti verdi), file di stampa in [`v13/`](v13/LEGGIMI.md). Visore: [modello 3D v1.3](https://tigrisxvi.github.io/scatoletta-blistra/modello-3d/v13.html).

## Novità della v1.2: i pezzi veri

La v1.2 è la v1.0 adattata ai componenti comprati: stepper 28BYJ-48 con ULN2003, servo SG90, OLED 0,96", una sola cella di carico, cassette fissate con una vite M2,5, zero delle ruote con un pulsantino finecorsa. Modello in `cad/scatoletta_v12.py`, controlli in `cad/controlli_v12.py` (tutti verdi), file di stampa e ferramenta in [`v12/`](v12/LEGGIMI.md). Visore: [modello 3D v1.2](https://tigrisxvi.github.io/scatoletta-blistra/modello-3d/v12.html).

## Novità della v1.0: le correzioni del rapporto R&D

La v1.0 è la v0.9 con i problemi trovati nel [rapporto R&D](rd/) corretti. Modello in `cad/scatoletta_v10.py`; i controlli in `cad/controlli_v10.py` passano tutti (nessuna interferenza, croce, ricarica, cavi, stabilità). File di stampa in `v10/` (`v10/PARAMETRI_STAMPA.md`). Visore: [modello 3D v1.0](https://tigrisxvi.github.io/scatoletta-blistra/modello-3d/v10.html).

| | Problema nella v0.9 | Correzione nella v1.0 |
|---|---|---|
| I-1 | La ricarica dall'alto fa passare solo 5 pillole su 59 | Vaschetta stretta appesa alla cella in alto: due fondi a leva che si inclinano a 42° quando si apre lo sportello e tornano giù con una piccola molla a torsione. Passano le pillole fino a 6,3 × 12 × 16,7 mm: 36 su 55 (prima 5) |
| I-2 | Asse stampato con 0,3 mm di gioco: le lamelle toccano l'anello (93% di probabilità) | Spina d'acciaio 6 × 16 mm nella cassetta, foro della ruota alesato a 6,0 H7; lamelle a 0,3 mm |
| I-3 | A motore bloccato i denti del pignone arrivano a 36–83 MPa | Limite di corrente nel firmware (`firmware/v10/limite_coppia.h`): massimo 10 MPa; perno della croce d'acciaio |
| I-4 | Un dito sulla vaschetta può rompere le celle da 100 g | Fermi sotto le estremità libere delle due celle, a 0,5 mm |
| I-5 | Una dose di 5 farmaci copre il 119% della vaschetta pesata | Vaschetta 30 × 24 mm (prima 24 × 22), pareti da 6 mm |
| I-6, I-12 | Sportellini a 0,05 mm, lamelle da 0,76 e dentini da 1 mm: troppo fini per la stampa | Sportellini da 1,6 mm a uno strato (0,2) dai divisori, lamelle da 1,2, dentini da 1,2, cerniere in filo d'acciaio |
| I-7, I-13 | La scatoletta non sa se una pillola ci sta né se si può caricare | App 3.4.1: misure della pillola, elenco dei farmaci da non caricare (dabigatran), avviso per quelli sensibili all'umidità |
| I-8, I-10, I-11, I-14 | Parametri di stampa generici | PETG naturale e ugello d'acciaio per i pezzi a contatto; guscio in ASA o PC se sta al sole; piede con 2 pareti; PETG con almeno 45 MPa |
| I-9, I-15 | Il gel di silice si satura prima del previsto | Sensore di umidità AHT20 sotto il tetto (`firmware/v10/umidita.h`) e gel nuovo a ogni ricarica, almeno ogni 7 giorni |

Il piede è 2 mm più largo (110 mm) per restare sopra 40 gradi di stabilità di lato con i pezzi nuovi.

## Novità della v0.9

- **Croce di Malta.** Il meccanismo dei vecchi proiettori e degli orologi prende il posto di corona e pignone. Dietro ogni ruota ci sono 15 fessure, una sotto ogni divisorio. Il motorino gira un ingranaggio da 24 denti con un perno: a ogni giro il perno entra in una fessura e fa avanzare la ruota di uno scomparto esatto (24 gradi). Per il resto del giro un disco di blocco tiene ferma la ruota, anche senza corrente e anche se qualcuno prova a girarla a mano. `cad/croce_check.py` simula un giro intero dell'ingranaggio: nessun urto, 24,0 gradi esatti, ruota bloccata a riposo. Il perno dell'ingranaggio è una vite recuperata da un hard disk.
- **Ricarica dall'alto, pesata in entrata.** Nel tetto, davanti, ci sono due sportellini. Le pillole di uno scomparto cadono su una vaschetta appesa a una seconda cella di carico (canale B dello stesso HX711), che le pesa. Quando si richiude lo sportellino, il suo dito inclina la vaschetta di 30–36 gradi e le pillole scivolano nello scivolo fino allo scomparto in alto davanti (54 gradi). Niente motori in più. Una vite dell'hard disk avvitata nella chiglia tiene la vaschetta dritta. `cad/ricarica_check.py` controlla il movimento.
- **Entrata → uscita.** All'uscita la bilancia di sotto ripesa la dose: sono le stesse pillole, quindi deve pesare uguale. Nelle prove simulate (`firmware/test`) ferma il 100% degli scomparti sbagliati, anche con una pillola da 40 mg, senza falsi allarmi.
- **Tutto in PETG**, un solo materiale.

## In prova: v0.8, due ruote e due motorini (la più compatta)

Le ruote sono mosse da un ingranaggio sul bordo, con il motorino N20 nell'angolo dove la ruota tonda lascia spazio. Le dosi cadono su un **piattino pesato** (cella di carico da 100 g) che un micro servo apre solo se il peso è quello impostato nell'app; sotto c'è il bicchierino, in una nicchia aperta come in una macchina del caffè, con un magnete nella base e un sensore di Hall nel piede. Corpo scuro e cappello colorato a righine con gli spigoli tondi; tasto tondo da 21 mm sul cappello. Davanti, dietro una griglia, un altoparlante da 20 mm con amplificatore MAX98357A: suona la sveglia e può dire «È ora delle pillole». Ruote con corona dentata vera (modulo 1) e pignoni da 20 denti. I fili di sopra corrono sotto il tetto e scendono in un canale nella parete centrale; corrente da una presa USB-C dietro; l'antenna Wi-Fi dell'ESP32-S3 è a 15 mm dal metallo più vicino. Il visore simula le pillole con la fisica vera (Rapier).

**Stampa 3D:** tutti i pezzi in un solo materiale, PETG con ugello da 0,4 mm; pareti da 1,2 mm (3 passate), giochi da 0,3–0,4 mm per le parti che si muovono, denti a modulo 1. `cad/controlli_v8.py` sceglie per ogni pezzo il verso di stampa con meno sbalzi (le STL in `v8/2m/stl/stampa/` sono già girate così): servono supporti soprattutto sotto il tetto della nicchia del corpo. Il piede si stampa capovolto; la piastra di ferro si incolla da sotto, poi quattro piedini di gomma.

**Cassette e sportellini:** la cassetta (l'anello attorno alla ruota) è stampata opaca ed è aperta davanti. Ogni scomparto della ruota ha il suo sportellino trasparente (PETG trasparente), con una cerniera vicino al mozzo (perno: un pezzo di filo da 0,8 mm), due dentini che scattano sugli scivoli dei divisori e una linguetta per aprirlo con il dito. Gli sportellini girano con la ruota: le pillole non strisciano contro parti ferme, e per ricaricare si apre uno scomparto alla volta.

**Posizione delle ruote:** ogni ruota ha un magnete da 3 × 1 mm nella corona, sotto lo scomparto chiuso, e un sensore di Hall (DRV5032) nella parete centrale, a 1,7 mm attraverso il fondo della cassetta. La scatola si azzera all'accensione e a ogni giro, e se una ruota salta un dente se ne accorge e non dà la dose. Cosa deve fare il firmware: `firmware/v08_cosa_deve_fare.md`.

**Senza corrente:** orologio DS3231 con pila a bottone nella camera dietro; la dose e la posizione delle ruote si salvano nella memoria dell'ESP32 a ogni passo. Una dose saltata per mancanza di corrente non esce mai da sola dopo.

**Umidità:** nel mozzo di ogni ruota c'è una tasca per circa 2 g di gel di silice, chiusa da un tappo con feritoie; forellini da 1,2 mm portano l'aria secca in ogni scomparto (le pillole non ci passano). Gli sportellini chiudono direttamente sopra i divisori.

**Fermo delle cassette, comandato dall'app:** per ogni cassetta un dente entra in una tacca della flangia e la blocca; lo gira di un quarto di giro un micro servo nascosto nell'angolo davanti in basso, sotto la ruota. Nell'app, nella ricarica guidata, il pulsante «Sblocca le cassette» apre i fermi per 2 minuti; quando la cassetta torna dentro (il sensore della ruota rivede il magnete) il fermo si richiude da solo. Il controllo verifica che, chiuso, la cassetta non esca.

**Pezzi di prova (prima della scatola intera):** `cad/prove_v8.py` crea in `v8/2m/prove/`:
- *prova 1, spicchio di ruota*: un quarto di ruota con 3 scomparti, lamelle, sportellini e il pezzo di cassetta con l'uscita e l'asse. Metti pillole vere (anche minuscole) negli scomparti, gira avanti e indietro 20 volte: non deve passare niente tra ruota e anello, lo scomparto vicino all'uscita non si deve svuotare, e la ruota deve girare con le lamelle senza forzare.
- *prova 2, piattino pesato*: piattino, staffa e una base per la cella di carico. Con cella, HX711 ed ESP32 pesa 10 volte una pillola da 90 mg e una da 12 mg: si vede quanto è precisa la bilancia.

**Ricarica guidata nell'app:** nell'app Blistra, nella scatoletta scegli il modello "v0.8": la ricarica guidata divide gli scomparti tra cassetta di sinistra (dispari) e di destra (pari), con il numero che trovi sul mozzo e le pillole da mettere.

**Robustezza:** la parte di sopra sta a sbalzo sulla nicchia del bicchierino e poggia sulla colonna dietro. `cad/controlli_v8.py` calcola le sezioni vere del corpo: con qualcuno che preme sul tasto con 5 kg, la colonna lavora a circa 1,2 MPa contro 15 MPa di resistenza tra gli strati di stampa del PETG (sicurezza 12 volte); la parete da 1,2 mm si imbarcherebbe solo a 4,1 MPa (3,4 volte); la cima si sposta di 0,2 mm. Gli angoli della nicchia hanno uno scivolo a 45° per tutta la larghezza e due squadrette ai lati.

**Pillole piccole:** in punta a ogni divisorio della ruota c'è una lamella di PETG che arriva a 0,1 mm dall'anello fermo senza toccarlo (si incastra a pressione e si può limare): tra ruota e anello non passa niente e ogni scomparto resta chiuso finché non arriva sull'uscita. Le altre fessure lungo il percorso delle pillole sono di 0,6 mm o meno (gioco ruota-anello 0,3, ruota-coperchio 0,3, cassetta-imbuto 0,6, imbuto-piattino 0,4, piattino-paratia 0,6), così anche una pillola da 3 × 1,6 mm non si incastra.

**Stabilità:** quasi tutto il peso è nel piede (10 cm di larghezza) con dentro una piastra di ferro da 104 × 76 × 6 mm (circa 370 g su 680). Baricentro a 5,2 cm da terra: si ribalta solo se inclinata di 44° di lato, 50° in avanti, 47° indietro. Sotto, quattro piedini di gomma.

Pareti da 1,2 mm, cassette da 1 mm. Corpo 10,5 × 5 × 20,4 cm (1,08 l), piede 11,9 × 10 cm, uno scomparto 4,3 cm³. Modello in `cad/scatoletta_v8.py`, controlli in `cad/controlli_v8.py` (nessuna interferenza), pezzi in `v8/2m/`, visore: [modello 3D v0.8](https://tigrisxvi.github.io/scatoletta-blistra/modello-3d/v8.html). Non ancora stampata.

## In prova: v0.7 a due ruote

Due ruote in piedi da 14 dosi, ognuna con il suo motorino, in cassette che si sfilano di lato. Lo scomparto che arriva in basso si svuota da solo: niente sportelli e niente servi. Bilancia sotto il bicchierino. **11 × 8 × 17,5 cm (1,5 litri), un terzo della v0.5.** Modello in `cad/scatoletta_v7.py`, controlli in `cad/controlli_v7.py`, pezzi in `v7/stl/`, visore: [modello 3D v0.7](https://tigrisxvi.github.io/scatoletta-blistra/modello-3d/v7.html). Non ancora stampata né simulata.

## In prova: v0.6 a due piani

Due caroselli da 14 scomparti uno sopra l'altro: in pianta occupa quasi la metà (circa 18 × 12 cm invece di 24,5 × 17,5). Fondi a cono, due sportelli a ghigliottina, bilancia sotto il bicchierino. Modello in `cad/scatoletta_v6.py`, controlli in `cad/controlli_v6.py`, pezzi in `v6/stl/`, visore: [modello 3D v0.6](https://tigrisxvi.github.io/scatoletta-blistra/modello-3d/v6.html). Non ancora stampata né simulata.

## Com'è fatta

- **Un guscio unico** arrotondato nasconde il meccanismo. Sopra c'è un **cofanetto**, il coperchio colorato con la cerniera dietro: si apre per ricaricare.
- **Davanti**, su una fascia inclinata: display da 1,3" con l'ora e la prossima dose, tasto grande da 30 mm e una linea di luce che traspare dalla plastica solo quando si accende (gialla: è ora; bianca: prendi le pillole; verde: presa; rossa: da controllare; blu: verifica).
- **Sotto**, una nicchia con il **bicchierino** estraibile dove cadono le pillole.
- **Sul fianco destro** l'interruttore, incassato perché non si spenga per sbaglio, e la presa USB-C.

## Come funziona dentro

- **29 scomparti** su un carosello: 4 dosi al giorno (mattina, pranzo, pomeriggio, sera) per 7 giorni, più uno scomparto di riposo sempre vuoto.
- **Fondo a rampa fisso**: il pavimento sale a elica e sotto l'uscita ha un ripiano piano inclinato verso l'esterno. I setti del carosello flottano in verticale nel mozzo e seguono la rampa, così le pillole non si incastrano.
- **Ripiano pesato e vibrante**: sotto l'uscita c'è una piastra su cella di carico (HX711) con un micro motore vibrante. La vibrazione fa scendere anche le compresse che con l'attrito resterebbero ferme; il peso conferma che la dose è uscita.
- **Sportello motorizzato**: premendo il tasto un micro servo alza lo sportello di 35° con una leva e scopre l'apertura nella parete. Per chiudere, la leva scende e lo sportello si richiude per il suo peso: non spinge mai verso il basso, quindi non schiaccia le dita. Un sensore Hall impedisce al carosello di girare con lo sportello aperto.
- **Scivolo**: le pillole scendono a 40° e cadono nel bicchierino.
- **ESP32** con motore passo-passo 28BYJ-48 e cicalino. Si collega opzionalmente all'app web Blistra.

Misure: 245 × 175 × 103 mm (il guscio entra in una stampante con piatto da 256 mm).

La v0.5 riusa il meccanismo della v0.3 e della v0.4 (`cad/scatoletta_v3.py`, `cad/scatoletta_v4.py`) e disegna l'esterno in `cad/scatoletta_v5.py`. Le schede tecniche in PDF descrivono ancora la v0.3: carosello, rampa, piastra e scivolo non sono cambiati.

## Cosa c'è nel progetto

| Cartella | Contenuto |
|---|---|
| `cad/` | Modello 3D parametrico in Python (manifold3d + trimesh), elettronica, viti e cavi (`elettronica_v5.py`), controlli di interferenza, render Blender, schede tecniche |
| `stl/stampa/` | Pezzi pronti per la stampa 3D |
| `stl/assieme/` | Pezzi nella posizione di montaggio |
| `firmware/` | Programma ESP32 (Arduino IDE) e istruzioni di taratura |
| `simulazioni/` | Simulazione fisica in Blender delle pillole che scendono, con i risultati |
| `docs/` | Schede tecniche in PDF (misure, sensori, schema), immagini e il visore 3D (`docs/modello-3d/`, three.js con licenza MIT) |

## Simulazioni

Simulazione a corpi rigidi della v0.3 (Blender/Bullet) con attrito realistico 0,35, vibrazione 50 Hz e 0,6 mm per 3 secondi, compresse dalle minicompresse da 2 mm fino a una compressa grande come un Augmentin:

- 238 dosi arrivate in fondo allo scivolo su 240 (le 2 mancate nel caso peggiore, attrito 0,5);
- 80 su 80 con la geometria esatta della v0.3. Rampa e parte inclinata dello scivolo sono le stesse nella v0.5; il salto finale nel bicchierino (circa 2 cm) non è stato simulato.

Una simulazione non sostituisce la prova vera: servono test con un prototipo stampato.

## Costruirla

1. Stampa i pezzi di `stl/stampa/` (PLA o PETG). Il guscio va stampato in bianco, così la luce traspare; il cofanetto del colore che preferisci.
2. Componenti: ESP32 DevKit, motore 28BYJ-48 con driver ULN2003, cella di carico da 100 g con HX711, motorino vibrante 8×2 mm con MOSFET, 2 sensori Hall A3144 con magneti, cicalino, micro servo SG90, display OLED I2C da 1,3\" (SH1106), barra di 8 LED WS2812, pulsante arcade da 30 mm a profilo basso, interruttore a bilanciere KCD11, presa USB-C da pannello, 2 magneti al neodimio (4×2 e 6×3 mm), 2 perni da 2 mm (o pezzi di filamento) per le cerniere di sportello e cofanetto.
   Le schede (ESP32, ULN2003, HX711, MOSFET) e il cicalino vanno nel vano sotto il fondo, incollate con biadesivo spesso 3–4 mm; i fili passano dai tre fori nella parete davanti. Nel visore 3D, «Mostra l'elettronica» fa vedere dove va ogni cosa.
3. Viti:

   | Quante | Vite | Dove |
   |---|---|---|
   | 4 | M3×14 testa cilindrica | fondo sulla base |
   | 2 + 2 dadi | M3×8 testa svasata + dadi M3 | motore sotto il fondo (testa a filo, sotto il mozzo) |
   | 2 | M3×8 testa cilindrica | cella di carico sul fondo, da sotto |
   | 2 | M3×6 testa bassa (2 mm) | piastra sulla cella; sopra vanno i tappini, incollati |
   | 4 | M3×10 testa cilindrica | scivolo sulla base, da fuori |
   | 2 | M2×6 | presa USB-C sul fianco |
   | 2 + 1 | M2 del sacchetto del servo | servo sulla culla, leva sulla squadretta |
4. Firmware: segui `firmware/LEGGIMI.txt`. Copia `config.example.h` in `config.h` e scrivi lì le tue password: `config.h` non va mai pubblicato.

## Contribuire

Prove di stampa, foto, misure, correzioni e idee sono benvenute: apri una issue o una pull request.

## Licenze

- Hardware (modelli 3D, STL, schede tecniche): [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt)
- Software (firmware, script CAD e di simulazione): [MIT](LICENSES/MIT.txt)
- Documentazione e immagini: [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt)

© 2026 Giuseppe Vasco
