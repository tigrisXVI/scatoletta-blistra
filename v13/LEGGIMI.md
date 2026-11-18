# Scatoletta Blistra v1.3

La v1.2 resa più stretta, con i caroselli che sporgono dal fianco. Modello in `cad/scatoletta_v13.py` (sottoclasse della v1.2), controlli in `cad/controlli_v13.py`: sono gli stessi della v1.2 e passano tutti (interferenze, croce di Malta, stepper e finecorsa, ricarica, cassette che si sfilano, cavi, stampa, robustezza, stabilità).

**Da stampare:** `blistra_v13_stampa.zip` (pezzi già orientati per la stampa). Parametri di stampa come nella v1.0 (`v10/PARAMETRI_STAMPA.md`).

Corpo 105 × **53** × 218 mm (la v1.2 era larga 64), piede 122 × 112 mm, peso circa 765 g. Si ribalta solo oltre 41° di lato, 45° in avanti e 42° indietro.

## Cosa è cambiato

- **Simmetria a mezzo giro.** Il lato destro è uguale al sinistro girato di 180° attorno all'asse verticale:
  - dietro in alto ci sono lo stepper, la croce e la ricarica dall'alto della ruota **sinistra**;
  - davanti in alto ci sono lo stepper, la croce e la ricarica dall'alto della ruota **destra**.
  Le due ruote girano in versi opposti. Il firmware deve tenerne conto: per avanzare di uno scomparto, lo stepper destro gira nel verso contrario rispetto al sinistro.
- **Stepper girati verso il centro.** La faccia con l'albero guarda la propria ruota e il corpo passa sopra l'altra ruota, dove nella v1.2 c'era l'altra metà della ricarica. Le alette si avvitano con 2 viti M3 × 6 a una piastra del cappello, che sta dietro le alette dalla parte del corpo. Le viti si mettono dalla parte dell'albero.
- **Guscio stretto:** 52,9 mm, come la v1.0.
- **Cassette con la cornice:** un anello che esce di 2 mm dal fianco, così intorno alla ruota non c'è più il pozzetto. La ruota si vede dall'oblò e gli sportellini si aprono come prima.
- **Ricarica dall'alto divisa in due:** ogni ruota ha la sua mezza canaletta (`17_staffa_alta_sx` dietro, `17_staffa_alta_dx` davanti), con la testata dalla parte del centro.
- **Display spostato:** l'OLED 0,96" sta davanti, al centro del corpo scuro, sotto le ruote. In alto davanti adesso c'è la croce della ruota destra. Si infila dall'interno tra due mensoline.
- **Camera dietro:** gli ULN2003 sono più verso il centro (y da -24 a 8), l'HX711 è a destra e l'ESP32-S3 sta **in piedi**, parallelo al fianco destro, tra due mensole con la scanalatura. La presa USB-C resta dietro. Così l'antenna sta a 10 mm dal metallo più vicino.
- **Cavi:** quelli della ruota destra (stepper e finecorsa) vanno dietro passando sotto il tetto. Attraversano la parete centrale in due fori, sotto il tasto e davanti in alto. Il canale dei cavi dietro è spostato 5,5 mm più indietro (x = -47,5).

## Ferramenta

Come la v1.2 (`v12/LEGGIMI.md`).

## Da fare

- Firmware: oltre a quanto scritto per la v1.2, il verso dello stepper destro è invertito.
